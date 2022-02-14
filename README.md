[![Build](https://github.com/wrouesnel/reproducible/actions/workflows/python.yml/badge.svg)](https://github.com/wrouesnel/reproducible/actions/workflows/python.yml)

# reproducible

Modified Version.

Create or convert archives into bit-exact reproducible formats.

## Installation

The only required file is `reproducible/reproducible.py` which works with any standard Python 3.8 or higher
installation and can be used by itsef. The virtualenv and other support files are to provice CI support.

## Usage

In the simplest form you pass the path for the directory you want to pack up, and optionally
a prefix you want to include in the tar file (which will be created with whatever is in the
directory as root):

```bash
./reproducible.py -d dir_to_archive -o archive.tar.gz  \
                  --prepend RepoName-master
```

You can also create zip files:

```bash
./reproducible.py -f zip-deflate  -d dir_to_archive -o archive.zip  \
                  --prepend RepoName-master
```

More useful would is potentially repacking an archive which was generated from another source:

```bash
./reproducible.py -f zip-deflate  -a some-existing-archive.zip -o reproducible-archive.zip
```
