import unittest
from unittest.mock import Mock, patch

from Xlib.ext import xinerama


class TestXinerama(unittest.TestCase):

    def test_get_info_returns_reply(self):
        disp = Mock()
        with patch.object(xinerama, 'GetInfo') as req:
            result = xinerama.get_info(disp, 7)
        self.assertIs(result, req.return_value)


if __name__ == '__main__':
    unittest.main()
