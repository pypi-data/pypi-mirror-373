from cyclopts import App
from hashlib import sha256
import json
import logging
import niquests
import os
from pathlib import Path
from pip._internal.utils import compatibility_tags
import subprocess
import sys
import tomllib
from urllib.parse import urlparse
from wheel_filename import parse_wheel_filename, ParsedWheelFilename


logger = logging.getLogger("wheel_getter")
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
app = App()


class TagMatcher:
    """Matches (parsed) filenames of wheels against a list of applicable tags."""
    
    def __init__(self,
            python: str,
            ) -> None:
        self.python = python
        self.interpreters: set[str] = set()
        max_minor = int(python.split(".")[1])
        for i in range(max_minor + 1):
            self.interpreters.add(f"py3{i}")
            self.interpreters.add(f"cp3{i}")
        self.tags = compatibility_tags.get_supported()
    
    def match_parsed_filename(self,
            name: ParsedWheelFilename,
            ) -> int | None:
        """Returns an integer weight if filename matches, None otherwise."""
        check_platform = "any" not in name.platform_tags
        check_abi = "none" not in name.abi_tags
        check_python = "py3" not in name.python_tags
        for i, tag in enumerate(self.tags):
            if tag.interpreter not in self.interpreters:
                continue
            if check_platform:
                if tag.platform not in name.platform_tags:
                    continue
            if check_python:
                if tag.interpreter not in name.python_tags:
                    continue
            if check_abi:
                if tag.abi not in name.abi_tags:
                    continue
            return i
        return None


def check_or_get_wheel(
        wheelhouse: Path,
        filename: str,
        url: str,
        hash: str,
        size: int,
        dry_run: bool,
        ) -> bool:
    """
    Checks if a wheel is in the wheelhouse, otherwise downloads and checks it.
    
    Returns always True because an error is raised if the operation is unsuccessful.
    This could change.
    """
    p = wheelhouse / filename
    if p.exists():
        logger.debug("wheel %s is present", filename)
        data = p.read_bytes()
        file_hash = f"sha256:{sha256(data).hexdigest()}"
        if file_hash != hash:
            logger.error(
                    "hash for %s doesn't match:\n  on disk:   %s\nshould be: %s",
                    filename,
                    file_hash,
                    hash,
                    )
            raise ValueError(f"wrong hash for {filename}")
        if len(data) != size:
            logger.error(
                    "size for %s doesn't match:\n on disk:   %s\nshould be: %s",
                    filename,
                    len(data),
                    size,
                    )
            raise ValueError(f"wrong size for {filename}")
        return True
    logger.debug("downloading %s …", filename)
    if dry_run:
        print(f"would download {url}")
        return True
    r = niquests.get(url)
    if r.status_code != 200:
        logger.error(
                "server sent status code %s for %s",
                r.status_code,
                url,
                )
        raise ValueError("download failure")
    target = wheelhouse / filename
    if not r.content:
        logger.error(
                "no data received from %s",
                url,
                )
        raise ValueError("download failure")
    if len(r.content) != size:
        logger.error(
                "wrong file size received from %s (was %s, should be %s)",
                url,
                len(r.content),
                size,
                )
        raise ValueError("download failure")
    file_hash = f"sha256:{sha256(r.content).hexdigest()}"
    if file_hash != hash:
        logger.error(
                "wrong hash for file from %s:\nwas:       %s\nshould be: %s",
                url,
                file_hash,
                hash,
                )
        raise ValueError("download failure")
    target.write_bytes(r.content)
    logger.info("downloaded %s", filename)
    return True


def get_and_build_wheel(
        package: str,
        version: str,
        wheelhouse: Path,
        url: str,
        hash: str,
        size: int,
        workdir: Path,
        package_dir: Path,
        python: str,
        dry_run: bool,
        ) -> bool:
    """
    Downloads an sdist archive and builds a wheel (invoking uv).
    
    Returns always True (for now) as an error is raised if the operation
    was unsuccessful.
    """
    if dry_run:
        print(f"would download sdist {url} and build {package}")
        return True
    
    parsed_url = urlparse(url)
    filename = Path(parsed_url.path).name
    
    workdir = workdir.absolute()
    filepath = workdir / filename
    
    try:
        if not workdir.exists():
            workdir.mkdir()
        
        logger.debug("downloading sdist %s …", filename)
        r = niquests.get(url)
        if r.status_code != 200:
            logger.error(
                    "server sent status code %s for %s",
                    r.status_code,
                    url,
                    )
            raise ValueError("download failure")
        if not r.content:
            logger.error(
                    "no data received from %s",
                    url,
                    )
            raise ValueError("download failure")
        if len(r.content) != size:
            logger.error(
                    "wrong file size received from %s (was %s, should be %s)",
                    url,
                    len(r.content),
                    size,
                    )
            raise ValueError("download failure")
        file_hash = f"sha256:{sha256(r.content).hexdigest()}"
        if file_hash != hash:
            logger.error(
                    "wrong hash for file from %s:\nwas:       %s\nshould be: %s",
                    url,
                    file_hash,
                    hash,
                    )
            raise ValueError("download failure")
        filepath.write_bytes(r.content)
        logger.info("downloaded %s", filename)
        
        subprocess.run(
                ["uv", "build", "--wheel", "--python", python, filepath],
                check=True,
                )
        
    finally:
        filepath.unlink(missing_ok=True)
        try:
            workdir.rmdir()
        except OSError:
            pass
    
    
    subprocess.run(["ls", "-l", package_dir / "dist"])
    for p in (package_dir / "dist").glob("*.whl"):
        wheel_name = parse_wheel_filename(p)
        if (wheel_name.project == package and wheel_name.version == version):
            content = p.read_bytes()
            wheel_hash = f"sha256:{sha256(content).hexdigest()}"
            wheel_size = len(content)
            p.rename(wheelhouse / p.name)
            metadata = {"name": p.name, "hash": wheel_hash, "size": wheel_size}
            metafile = wheelhouse / f"{package}-{version}.info"
            json.dump(metadata, open(metafile, "w"))
            break
    else:
        logger.error("wheel for %s not found", package)
        raise ValueError("wheel not found")
    
    return True


@app.default
def get_wheels(
        wheelhouse: Path = Path("wheels"),
        # lockfile: Path = Path("uv.lock"),
        package: Path | None = None,
        directory: Path | None = None,
        python: str | None = None,
        debug: bool = False,
        dry_run: bool = False,
        ) -> None:
    """Gets and/or builds wheels if necessary, putting them in the wheelhouse."""
    if debug:
        logger.setLevel(logging.DEBUG)
    
    if directory is not None:
        os.chdir(directory)
        logger.debug("changed to %s", directory)
    
    if package is None:
        base_dir = Path.cwd()
        while not (base_dir / "pyproject.toml").exists():
            parent = base_dir.parent
            if parent == base_dir:
                logger.error("no project found")
                raise ValueError("no project found")
            base_dir = parent
    else:
        base_dir = package
        if not (base_dir / "pyproject.toml").exists():
            logger.error("%s is not a package directory", package)
            raise ValueError("no project found")
    logger.debug("using base directory %s", base_dir)
    
    if python is None:
        if (pin_file := base_dir / ".python-version").exists():
            python_version = pin_file.read_text().strip()
        else:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        logger.info("working with Python version %s", python)
    else:
        python_version = python
    py_marker = f"cp{python_version.replace('.', '')}"
    logger.debug("using python marker %s", py_marker)
    
    lockfile = base_dir / "uv.lock"
    if not lockfile.exists():
        logger.error("no lockfile found at %s", base_dir)
        raise ValueError("no lockfile found")
    
    if not wheelhouse.exists():
        wheelhouse.mkdir(parents=True, exist_ok=True)
    workdir = wheelhouse / "temp"
    
    uvl = tomllib.load(open(lockfile, "rb"))
    logger.info("read lockfile from %s", lockfile)
    
    matcher = TagMatcher(python=python_version)
    
    for pkg in uvl["package"]:
        pkg_name = pkg["name"]
        pkg_version = pkg["version"]
        logger.debug("analyzing %s (version %s) …", pkg_name, pkg_version)
        
        present = False
        
        # find matching wheel name in lockfile
        matched_wheels: list[tuple[int, dict]] = []
        for wh in pkg.get("wheels", []):
            parsed_url = urlparse(wh["url"])
            filename = Path(parsed_url.path).name
            parsed_filename = parse_wheel_filename(filename)
            
            if (w := matcher.match_parsed_filename(parsed_filename)) is not None:
                matched_wheels.append((w, wh))
        
        # get best matching wheel name (if any) and look for that wheel,
        # download it if it isn't present
        if matched_wheels:
            matched_wheels.sort()
            w, wh = matched_wheels[0]
            parsed_url = urlparse(wh["url"])
            filename = Path(parsed_url.path).name
            
            logger.debug("trying wheel %s", filename)
            present = check_or_get_wheel(
                    wheelhouse,
                    filename,
                    url=wh["url"],
                    hash=wh["hash"],
                    size=wh["size"],
                    dry_run=dry_run,
                    )
        else:
            logger.debug("no wheel in lockfile found for %s", pkg_name)
        
        if not present:
            # is a locally built wheel present in the wheelhouse?
            info_name = wheelhouse / f"{pkg_name}-{pkg_version}.info"
            if info_name.exists():
                metadata = json.load(open(info_name))
                filename = wheelhouse / metadata["name"]
                hash = metadata["hash"]
                size = metadata["size"]
                if filename.exists():
                    content = filename.read_bytes()
                    content_hash = f"sha256:{sha256(content).hexdigest()}"
                    if len(content) == size and content_hash == hash:
                        logger.info("locally built wheel found for %s", pkg_name)
                        present = True
        
        if not present:
            # try to find a wheel in an editable project
            if "source" in pkg and "editable" in pkg["source"]:
                logger.debug("package %s is editable", pkg_name)
                edit_path = base_dir / pkg["source"]["editable"]
                if (dist_path := edit_path / "dist").exists():
                    for dist_name in dist_path.glob("*.whl"):
                        parsed_dist_name = parse_wheel_filename(dist_name.name)
                        if (parsed_dist_name.project == pkg_name and
                                parsed_dist_name.version == pkg_version):
                            m = matcher.match_parsed_filename(parsed_dist_name)
                            if m is not None:
                                logger.debug("wheel %s found in dist dir",
                                        dist_name.name)
                                (wheelhouse / dist_name.name).write_bytes(
                                        dist_name.read_bytes())
                                logger.info("wheel %s found in editable project",
                                        dist_name.name)
                                present = True
        
        if not present:
            # try to download and build a source archive
            sdist = pkg.get("sdist")
            if sdist is None:
                logger.error("cannot download package %s, no sdist", pkg_name)
                raise ValueError(f"package {pkg_name}")
            present = get_and_build_wheel(
                    package=pkg_name,
                    version=pkg_version,
                    wheelhouse=wheelhouse.absolute(),
                    package_dir=base_dir.absolute(),
                    url=sdist["url"],
                    hash=sdist["hash"],
                    size=sdist["size"],
                    workdir=workdir,
                    python=python_version,
                    dry_run=dry_run,
                    )
            if present:
                logger.info("wheel %s successfully built", filename)
            else:
                logger.error("wheel %s was not downloaded", filename)
