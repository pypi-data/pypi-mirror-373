# wheel-getter

## What's the problem?

I want to install (locally authored) Python packages on servers that (for
security and other reasons) can't retrieve packages from PyPI or that (for
security reasons) don't have compilers and other development tools
installed. And I want to be sure that the same packages are installed as in
my development or staging environment, identified by a hash checksum.

My workflows are based on uv, which is fast and has other advantages in
comparison to pip, pip-tools and other “legacy” tools. Unfortunately uv
doesn't (yet?) offer an export of wheels (like `pip wheel`) that were
downloaded or locally built. AFAICT uv doesn't even cache downloaded wheel
but just their contents (which makes copying / hardlinking them into venv's
faster).

## How can wheel-getter help?

This tool reads uv's lockfile and downloads the same wheels that uv has used
for the current project. The lockfile contains checksums for these wheels;
they are checked against the downloaded files.

For locally built wheels the lockfile has “sdist” information with URLs and
checksums for the source archives. The wheel-getter tool retrieves these
archives, invokes `uv build` and grabs the resulting wheels.

For these freshly made wheels some metadata is added to the wheel directory,
containing file size and checksum so that the wheels can be verified.

## Can wheel-getter guarantee workflow security?

No. Use it at your own risk.

## How can I install this tool?

The easiest way is `uv tool install wheel-getter`; there are plenty of
alternatives, of course.

## How should I use wheel-getter?

It is recommended to cd into the base directory of your project where your
`pyproject.toml` file lives, after having locked and synced (and tested) the
project. Then invoke wheel-getter, specifying the Python version unless it's
the one that executes wheel-getter itself:

```
wheel-getter --python=3.11
```

If all is well, all required wheels should be collected in the `wheels`
subdirectory (or the output directory specified by `--wheelhouse`).

Please note that no wheels are built for packages installed as editable; you
should build them as usual and copy them to the “wheelhouse” yourself.

Since this tool has only been tested and used under Linux, there can (and
will) be problems with other OSes.

## If you find a bug or want to improve this tool …

… you are welcome to write a bug report or, preferably, supply a PR. Please
be aware, though, that I may be slow (but willing) to respond; my primary
concern is that this tool works for me, and I probably haven't run into lots
of edge and corner cases.
