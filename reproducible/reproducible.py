#!/usr/bin/env python3
"""Standalone python file for building or repacking archives reproducibly"""

import io
import shutil
import tempfile
import zipfile
import gzip
import itertools
import locale
import os
import contextlib
import functools

import sys
import tarfile

from argparse import ArgumentParser

from typing import List, Tuple, Optional, Set, IO, Sequence, Iterator, cast, TYPE_CHECKING
from zipfile import ZipFile

if TYPE_CHECKING:
    from _typeshed import SupportsWrite


@contextlib.contextmanager
def setlocale(name: str) -> Iterator[None]:
    """Context manager for changing the current locale"""
    saved_locale = locale.setlocale(locale.LC_ALL)
    try:
        locale.setlocale(locale.LC_ALL, name)
        yield
    finally:
        locale.setlocale(locale.LC_ALL, saved_locale)


def os_walk_error_handler(exc_instance: BaseException) -> None:
    """Exception handler function for os.walk"""
    raise exc_instance


def tar_archive_deterministically(
    dir_to_archive: str,
    out_file: IO[bytes],
    prepend_path: Optional[str] = None,
    compress: bool = True,
    file_selector: Optional[Set[str]] = None,
) -> None:
    """Create a deterministic tar archive

    :param dir_to_archive: path to the directory to form the root of the archive
    :param out_file: name of the output file
    :param prepend_path: path to prepend to the root of the arhive
    :param compress: if true, uses gz compression
    :param file_selector: set of relative file paths to include
    :return:
    """
    representative_name = f"{os.path.basename(dir_to_archive)}.tar"

    def reset(tarinfo: tarfile.TarInfo) -> tarfile.TarInfo:
        """Helper to reset owner/group and modification time for tar entries"""
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = "root"
        tarinfo.mtime = 0
        return tarinfo

    target_files: List[Tuple[str, str]] = []
    for root, dirs, files in os.walk(dir_to_archive, onerror=os_walk_error_handler):
        for fname in itertools.chain(dirs, files):
            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, dir_to_archive)
            if file_selector is not None:
                if relpath not in file_selector:
                    continue
            target_files.append((relpath, fpath))

    # Sort file entries with the fixed locale
    with setlocale("C"):
        target_files.sort(key=lambda t: locale.strxfrm(t[0]))

    def tar_deterministically(outf: SupportsWrite[bytes]) -> None:
        with tarfile.open(fileobj=cast(IO[bytes], outf), mode="w:") as tar_file:
            for relpath, fpath in target_files:
                arcname = relpath
                if prepend_path is not None:
                    arcname = os.path.normpath(os.path.join(prepend_path, relpath))
                tar_file.add(fpath, filter=reset, recursive=False, arcname=arcname)

    if compress:
        with gzip.GzipFile(
            filename=representative_name, mode="wb", fileobj=out_file, mtime=0
        ) as gzip_file:
            tar_deterministically(gzip_file)
    else:
        tar_deterministically(out_file)


def zip_archive_deterministically(
    dir_to_archive: str,
    out_file: IO[bytes],
    prepend_path: Optional[str] = None,
    compress: bool = True,
    file_selector: Optional[Set[str]] = None,
) -> None:
    """Create a deterministic zip archive

    :param dir_to_archive: path to the directory to form the root of the archive
    :param out_file: name of the output file
    :param prepend_path: path to prepend to the root of the arhive
    :param compress: if true, uses gz compression
    :param file_selector: set of relative file paths to include
    :return:
    """
    # Zip files can't be written sequentially, so fake it with named temporary files
    with tempfile.NamedTemporaryFile(mode="r+b") as f:
        with ZipFile(
            f.name,
            "w",
            allowZip64=True,
            compression=zipfile.ZIP_STORED if not compress else zipfile.ZIP_DEFLATED,
        ) as z:
            target_files: List[Tuple[str, str]] = []
            for root, _dirs, files in os.walk(dir_to_archive, onerror=os_walk_error_handler):
                for fname in files:
                    fpath = os.path.join(root, fname)
                    # Note that dates prior to 1 January 1980 are not supported
                    relpath = os.path.relpath(fpath, dir_to_archive)
                    if file_selector is not None:
                        if relpath not in file_selector:
                            continue
                    target_files.append((relpath, fpath))

            # Sort file entries with the fixed locale
            with setlocale("C"):
                target_files.sort(key=lambda t: locale.strxfrm(t[0]))

            for relpath, fpath in sorted(target_files):
                arcname = (
                    os.path.normpath(os.path.join(prepend_path, relpath))
                    if prepend_path is not None
                    else relpath
                )
                info = zipfile.ZipInfo(arcname, date_time=(1980, 1, 1, 0, 0, 0))
                with open(fpath, "rb") as inpf:
                    z.writestr(info, inpf.read())
        f.seek(0, io.SEEK_SET)
        while True:
            data_bytes = f.read(1024)
            if len(data_bytes) == 0:
                break
            out_file.write(data_bytes)


"""Define the possible output formats. Default is tar.gz"""
OUTPUT_FMTS = {
    "tar": functools.partial(tar_archive_deterministically, compress=False),
    "tar-gz": functools.partial(tar_archive_deterministically, compress=True),
    "zip-store": functools.partial(zip_archive_deterministically, compress=False),
    "zip-deflate": functools.partial(zip_archive_deterministically, compress=True),
}


def main(argv: Optional[Sequence[str]]) -> None:
    """Entrypoint for the command line utility"""
    parser = ArgumentParser()

    parser.add_argument(
        "-f", "--format", choices=OUTPUT_FMTS, default="tar-gz", help="output format"
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--dir", help="directory to archive")
    group.add_argument("-a", "--archive", help="archive to repack deterministically")

    parser.add_argument("-o", "--out", help="archive destination", required=True)
    parser.add_argument("-p", "--prepend", help="prepend path")

    args = parser.parse_args(argv)

    fn = OUTPUT_FMTS[args.format]

    if args.archive is not None:
        temp_dir = tempfile.TemporaryDirectory()
        archive_dir = temp_dir.name
        # Unpack the archive to the temporary directory
        shutil.unpack_archive(args.archive, archive_dir)
    else:
        archive_dir = args.dir

    fn(archive_dir, args.out, args.prepend)

    if args.archive is not None:
        temp_dir.cleanup()


if __name__ == "__main__":
    main(sys.argv[1:])
