from __future__ import absolute_import

import io
import os
import sys
import tempfile

import mmap
from billiard import reduction
from billiard import util
from billiard.heap import (
    reduce_arena,
    Arena as BilliardArena,
)


def ensure_get_temp_dir():
    temp_dir = util.get_temp_dir()
    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


if sys.platform == 'win32':
    Arena = BilliardArena
else:
    class Arena:
        def __init__(self, size, fd=-1):
            self.size = size
            self.fd = fd
            if fd == -1:
                self.fd, name = tempfile.mkstemp(
                    prefix='pym-%d-' % (os.getpid(),),
                    dir=ensure_get_temp_dir(),
                )

                os.unlink(name)
                util.Finalize(self, os.close, (self.fd,))
                with io.open(self.fd, 'wb', closefd=False) as f:
                    bs = 1024 * 1024
                    if size >= bs:
                        zeros = b'\0' * bs
                        for _ in range(size // bs):
                            f.write(zeros)
                        del(zeros)
                    f.write(b'\0' * (size % bs))
                    assert f.tell() == size
            self.buffer = mmap.mmap(self.fd, self.size)

    reduction.register(Arena, reduce_arena)
