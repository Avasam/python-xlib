
import unittest
import binascii
import difflib
import os
import socket
import struct
import subprocess
import tempfile
import array

import Xlib.protocol.event
import Xlib.protocol.rq
import Xlib.xauth


class CmpArray(object):

    def __init__(self, *args, **kws):
        self.array = array.array(*args, **kws)

    def __len__(self):
        return len(self.array)

    def __getitem__(self, key):
        if isinstance(key, slice):
            x = key.start
            y = key.stop
            return list(self.array[x:y])
        else:
            return self.array[key]

    def __getattr__(self, attr):
        return getattr(self.array, attr)

    def __eq__(self, other):
        return self.array.tolist() == other

Xlib.protocol.rq.array = CmpArray


class DummyDisplay(object):

    def get_resource_class(self, x):
        return None

    event_classes = Xlib.protocol.event.event_class


class TestCase(unittest.TestCase):

    def assertBinaryEqual(self, bin1, bin2):
        if bin1 != bin2:
            self.fail('binary contents differ:\n' + bindiff(bin1, bin2))

    def assertBinaryEmpty(self, bin):
        if len(bin) != 0:
            self.fail('binary content not empty:\n' + ''.join(tohex(bin)))

class BigEndianTest(TestCase):

    @classmethod
    def setUpClass(cls):
        if struct.unpack('BB', struct.pack('H', 0x0100))[0] != 1:
            raise unittest.SkipTest('big-endian tests, skipping on this system')

class LittleEndianTest(TestCase):

    @classmethod
    def setUpClass(cls):
        if struct.unpack('BB', struct.pack('H', 0x0100))[0] != 0:
            raise unittest.SkipTest('little-endian tests, skipping on this system')


def tohex(bin):
    hex = []
    for i in range(0, len(bin), 16):
        hex.append(str(binascii.hexlify(bin[i:i+16])) + '\n')
    return hex

def bindiff(bin1, bin2):
    hex1 = tohex(bin1)
    hex2 = tohex(bin2)
    return ''.join(difflib.ndiff(hex1, hex2))


class Xvfb(object):
    """A private Xvfb server for the tests that need a live X display.

    Use `start` and `stop` as a module's `setUpModule` and `tearDownModule`.
    While the server runs, `DISPLAY` and `XAUTHORITY` point to it, so
    subprocesses use it too.
    """

    def __init__(self):
        self.process = None
        self.authfile = None
        self.saved_environ = None

    def start(self):
        try:
            self._start()
        except BaseException:
            self.stop()
            raise

    def _start(self):
        fd, self.authfile = tempfile.mkstemp(prefix='xlib-test-', suffix='.Xauthority')
        with os.fdopen(fd, 'wb') as f:
            # Xvfb loads every cookie in the file, and Xlib matches an entry
            # without a display number to any display, so the cookie can be
            # written before Xvfb picks the display.
            f.write(xauth_entry(
                Xlib.xauth.FamilyLocal, socket.gethostname().encode(), b'',
                b'MIT-MAGIC-COOKIE-1', os.urandom(16),
            ))
        # With `-displayfd`, Xvfb picks a free display and writes its number
        # to that pipe once it accepts connections.
        read_fd, write_fd = os.pipe()
        try:
            self.process = subprocess.Popen(
                ['Xvfb', '-auth', self.authfile, '-noreset', '-displayfd', str(write_fd)],
                pass_fds=(write_fd,),
            )
        except BaseException:
            os.close(read_fd)
            raise
        finally:
            os.close(write_fd)
        with os.fdopen(read_fd, 'rb') as pipe:
            display_number = pipe.readline().strip().decode()
        if not display_number:
            raise RuntimeError('Xvfb exited before reporting its display')
        self.saved_environ = dict((name, os.environ.get(name)) for name in ('DISPLAY', 'XAUTHORITY'))
        os.environ['DISPLAY'] = ':' + display_number
        os.environ['XAUTHORITY'] = self.authfile

    def stop(self):
        if self.saved_environ is not None:
            for name, value in self.saved_environ.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value
            self.saved_environ = None
        if self.process is not None:
            self.process.terminate()
            self.process.wait()
            self.process = None
        if self.authfile is not None:
            os.unlink(self.authfile)
            self.authfile = None


def xauth_entry(family, address, number, name, data):
    """Serialize one entry in the Xauthority file format."""
    fields = (address, number, name, data)
    return struct.pack('>H', family) + b''.join(struct.pack('>H', len(field)) + field for field in fields)
