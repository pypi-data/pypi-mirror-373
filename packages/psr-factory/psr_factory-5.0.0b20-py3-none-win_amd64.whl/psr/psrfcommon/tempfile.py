# PSR Factory. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import errno
import io
import os
from random import Random


class _RandomNameSequence:
    """An instance of _RandomNameSequence generates an endless
    sequence of unpredictable strings which can safely be incorporated
    into file names.  Each string is eight characters long.  Multiple
    threads can safely use the same instance at the same time.

    _RandomNameSequence is an iterator."""

    # Method extracted from tempfile Python's module.

    characters = "abcdefghijklmnopqrstuvwxyz0123456789_"

    @property
    def rng(self):
        cur_pid = os.getpid()
        if cur_pid != getattr(self, "_rng_pid", None):
            self._rng = Random()  # nosec
            self._rng_pid = cur_pid
        return self._rng

    def __iter__(self):
        return self

    def __next__(self):
        c = self.characters
        choose = self.rng.choice
        letters = [choose(c) for dummy in range(8)]
        return "".join(letters)


def _get_tempfile_name(base_path: str, prefix: str):
    """Calculate the default directory to use for temporary files.
    This routine should be called exactly once.

    We determine whether a candidate temp dir is usable by
    trying to create and write to a file in that directory.  If this
    is successful, the test file is deleted.  To prevent denial of
    service, the name of the test file must be randomized."""
    # Method extracted from tempfile Python's module.

    _text_openflags = os.O_RDWR | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        _text_openflags |= os.O_NOFOLLOW

    _bin_openflags = _text_openflags
    if hasattr(os, "O_BINARY"):
        _bin_openflags |= os.O_BINARY

    namer = _RandomNameSequence()

    if base_path != os.curdir:
        base_path = os.path.abspath(base_path)
    # Try only a few names per directory.
    for seq in range(100):
        name = next(namer)
        filename = os.path.join(base_path, prefix + name)
        try:
            fd = os.open(filename, _bin_openflags, 0o600)
            try:
                try:
                    with io.open(fd, "wb", closefd=False) as fp:
                        fp.write(b"blat")
                finally:
                    os.close(fd)
            finally:
                os.unlink(filename)
            return filename
        except FileExistsError:
            pass
        except PermissionError:
            # This exception is thrown when a directory with the chosen name
            # already exists on windows.
            if (
                os.name == "nt"
                and os.path.isdir(base_path)
                and os.access(base_path, os.W_OK)
            ):
                continue
            break  # no point trying more names in this directory
        except OSError:
            break  # no point trying more names in this directory
    raise FileNotFoundError(
        errno.ENOENT, "No usable temporary file found in " % base_path
    )


class CreateTempFile:
    def __init__(
        self,
        base_path: str,
        prefix: str,
        file_content: str,
        extension: str = ".dat",
        delete_tempfile: bool = True,
    ):
        self.delete_tempfile = delete_tempfile
        # get temp file name
        self.temp_file_name = _get_tempfile_name(base_path, prefix) + extension
        self.temp_content = file_content

    def __enter__(self):
        with open(self.temp_file_name, "w", encoding="utf-8-sig") as tempfile:
            tempfile.write(self.temp_content)
            return tempfile

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.delete_tempfile:
            os.remove(self.temp_file_name)
