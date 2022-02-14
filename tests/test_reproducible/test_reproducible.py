import os
from reproducible.reproducible import main


def test_reproducible_tar_file(repo_root, tmpdir):
    main(["-f", "tar", "-d", repo_root, "-o", os.path.join(tmpdir, "archive.tar")])


def test_reproducible_zip_file(repo_root, tmpdir):
    main(["-f", "zip-store", "-d", repo_root, "-o", os.path.join(tmpdir, "archive.tar")])
