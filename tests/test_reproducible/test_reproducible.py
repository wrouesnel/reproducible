import os
import filecmp
from reproducible.reproducible import main


def test_reproducible_tar_file(repo_root: str, tmpdir: str):
    """Test that reproducible tar files can be generated"""
    test_data = os.path.join(repo_root, "reproducible")

    main(["-f", "tar", "-d", test_data, "-o", os.path.join(tmpdir, "archive1.tar")])
    main(["-f", "tar", "-d", test_data, "-o", os.path.join(tmpdir, "archive2.tar")])

    assert filecmp.cmp(
        os.path.join(tmpdir, "archive1.tar"), os.path.join(tmpdir, "archive2.tar")
    ), "Outputs are not identical"


def test_reproducible_compressed_tar_file(repo_root: str, tmpdir: str):
    """Test that reproducible gzip'd tar files can be generated"""
    test_data = os.path.join(repo_root, "reproducible")

    main(["-f", "tar-gz", "-d", test_data, "-o", os.path.join(tmpdir, "archive1.tar.gz")])
    main(["-f", "tar-gz", "-d", test_data, "-o", os.path.join(tmpdir, "archive2.tar.gz")])

    assert filecmp.cmp(
        os.path.join(tmpdir, "archive1.tar.gz"), os.path.join(tmpdir, "archive2.tar.gz")
    ), "Outputs are not identical"


def test_reproducible_zip_file(repo_root: str, tmpdir: str):
    """Test that reproducible zip files can be generated"""
    test_data = os.path.join(repo_root, "reproducible")

    main(["-f", "zip-store", "-d", test_data, "-o", os.path.join(tmpdir, "archive1.zip")])
    main(["-f", "zip-store", "-d", test_data, "-o", os.path.join(tmpdir, "archive2.zip")])

    assert filecmp.cmp(
        os.path.join(tmpdir, "archive1.zip"), os.path.join(tmpdir, "archive2.zip")
    ), "Outputs are not identical"


def test_reproducible_compressed_zip(repo_root: str, tmpdir: str):
    """Test that reproducible deflated zip files can be generated"""
    test_data = os.path.join(repo_root, "reproducible")

    main(["-f", "zip-deflate", "-d", test_data, "-o", os.path.join(tmpdir, "archive1.zip")])
    main(["-f", "zip-deflate", "-d", test_data, "-o", os.path.join(tmpdir, "archive2.zip")])

    assert filecmp.cmp(
        os.path.join(tmpdir, "archive1.zip"), os.path.join(tmpdir, "archive2.zip")
    ), "Outputs are not identical"
