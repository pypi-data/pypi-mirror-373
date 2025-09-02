import os
import sys
from contextlib import contextmanager


@contextmanager
def suppress_stdout(suppress=False):
    if suppress:
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:
                yield
            finally:
                sys.stdout = old_stdout
    else:
        yield
