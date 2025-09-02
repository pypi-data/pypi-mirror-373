import sys
from contextlib import contextmanager
import gzip
from pathlib import Path

import os
import shutil
from tempfile import mkstemp
from typing import Union

def samefile(path1, path2):
    return Path(path1).resolve() == Path(path2).resolve()

def exists(path):
    return Path(path).exists()

if sys.version_info >= (3, 6):
    from os import PathLike, fspath
    AnyPath = Union[str, PathLike]

else:
    fspath = str 
    AnyPath = str


@contextmanager
def temp_path(suffix='', prefix=''):
    tmpfd, tmpfile = mkstemp(suffix=suffix, prefix=prefix)
    os.close(tmpfd)
    try:
        yield tmpfile
    finally:
        os.remove(tmpfile)


def same_file(f1: AnyPath, f2: AnyPath) -> bool:
    if exists(f1) and exists(f2):
        return samefile(f1, f2)
    return False


def compress(infile: AnyPath) -> None:
    with open(infile, 'rb') as f_in:
        with gzip.open(fspath(infile) + '.gz', 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
