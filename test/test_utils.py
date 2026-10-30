import os
import re
import subprocess
import sys
import unittest

from Xlib import X, error
from Xlib.protocol import display, event, request

UTILS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils')


def xbug_log(packets):
    """Serialize (source, data) packets in the log format written by utils/tcpbug.py."""
    return b''.join(source + str(len(data)).encode() + b'\n' + data for source, data in packets)


class TestParseXbug(unittest.TestCase):

    def test_parse_session(self):
        setup = display.ConnectionSetupRequest
        setup_success = setup._success_reply.to_binary(
            release_number=1, resource_id_base=0, resource_id_mask=0, motion_buffer_size=0,
            vendor='test', max_request_length=0xffff, roots=[], pixmap_formats=[],
            image_byte_order=0, bitmap_format_bit_order=0, bitmap_format_scanline_unit=32,
            bitmap_format_scanline_pad=32, min_keycode=8, max_keycode=255,
        )
        log = xbug_log((
            (b'C', setup._request.to_binary(
                byte_order=0x6c if sys.byteorder == 'little' else 0x42,
                protocol_major=11, protocol_minor=0, auth_prot_name='', auth_prot_data='',
            )),
            (b'S', setup._reply.to_binary(
                status=1, reason_length=0, protocol_major=11, protocol_minor=0,
                additional_length=len(setup_success) // 4,
            ) + setup_success),
            (b'C', request.GetInputFocus._request.to_binary() + request.MapWindow._request.to_binary(window=0x42)),
            (b'S', request.GetInputFocus._reply.to_binary(revert_to=X.RevertToParent, sequence_number=1, focus=0x1234)),
            (b'S', error.XError._fields.to_binary(
                type=0, code=X.BadWindow, sequence_number=2, resource_id=0x42, minor_opcode=0, major_opcode=8,
            )),
            (b'S', event.MapNotify(window=0x42, event=0x42, override=0)._binary),
        ))

        # parsexbug patches Xlib modules on import, keep it out of the test process
        process = subprocess.Popen(
            [sys.executable, os.path.join(UTILS_DIR, 'parsexbug.py')],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        out, err = process.communicate(log)
        self.assertEqual(process.returncode, 0, err.decode())

        out = out.decode()
        headers = [line.split() for line in out.splitlines() if re.match(r'\w+:', line)]
        self.assertEqual(headers, [
            ['request:', 'ConnectionSetup'],
            ['reply:', 'ConnectionSetup'],
            ['request:', 'GetInputFocus'],
            ['reply:', 'GetInputFocus'],
            ['request:', 'MapWindow'],
            ['error:', 'BadWindow'],
            ['event:', 'MapNotify'],
        ])
        self.assertIn("'vendor': 'test'", out)
        self.assertIn("'focus': 4660", out)


if __name__ == '__main__':
    unittest.main()
