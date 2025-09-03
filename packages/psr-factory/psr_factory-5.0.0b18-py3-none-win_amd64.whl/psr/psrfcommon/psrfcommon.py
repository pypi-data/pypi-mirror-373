# PSR Factory. Copyright (C) PSR, Inc - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import os
import pathlib
import subprocess
import sys
from contextlib import contextmanager
from typing import Union, List


@contextmanager
def change_cwd(new_dir: Union[str, pathlib.Path]):
    last_dir = os.getcwd()
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(last_dir)


def exec_cmd(cmd: Union[str, List[str]], **kwargs) -> int:
    dry_run = kwargs.get("dry_run", False)
    print_progress = kwargs.get("show_progress", False)

    if print_progress or dry_run:
        sys.stdout.flush()

    if dry_run:
        if isinstance(cmd, list):
            print(" ".join(cmd))
        else:
            print(cmd)
        return_code = 0
    else:
        try:
            return_code = subprocess.call(cmd, shell=True)
            if return_code > 0:
                raise RuntimeError(f"Execution error, code {return_code}")
            else:
                if print_progress:
                    print("Execution success", return_code)
        except OSError as e:
            msg = f"Execution failed: {e}"
            if print_progress:
                print(msg, file=sys.stderr)
            raise RuntimeError(msg)

    if print_progress or dry_run:
        sys.stdout.flush()
    return return_code


