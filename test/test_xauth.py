import logging
import os
import tempfile
import unittest
from unittest.mock import patch

from Xlib import error, xauth
from . import xauth_entry

COOKIE = b'MIT-MAGIC-COOKIE-1'


class TestGetBestAuth(unittest.TestCase):

    def get_best_auth(self, entries, family, address, dispno):
        fd, filename = tempfile.mkstemp(prefix='xlib-test-', suffix='.Xauthority')
        self.addCleanup(os.unlink, filename)
        with os.fdopen(fd, 'wb') as f:
            f.write(b''.join(xauth_entry(*entry) for entry in entries))
        return xauth.Xauthority(filename).get_best_auth(family, address, dispno)

    def test_exact_match(self):
        self.assertEqual(self.get_best_auth([
            (xauth.FamilyLocal, b'other', b'0', COOKIE, b'wrong host'),
            (xauth.FamilyLocal, b'host', b'1', COOKIE, b'wrong display'),
            (xauth.FamilyLocal, b'host', b'0', COOKIE, b'right'),
        ], xauth.FamilyLocal, b'host', 0), (COOKIE, b'right'))

    def test_any_display_number(self):
        self.assertEqual(self.get_best_auth([
            (xauth.FamilyLocal, b'host', b'', COOKIE, b'any display'),
        ], xauth.FamilyLocal, b'host', 3), (COOKIE, b'any display'))

    def test_wild_family(self):
        # Mutter's XWayland writes a FamilyWild entry, which libXau matches
        # whatever the family and address, for example after a hostname change
        self.assertEqual(self.get_best_auth([
            (xauth.FamilyLocal, b'old-host', b'', COOKIE, b'wrong host'),
            (xauth.FamilyWild, b'old-host', b'', COOKIE, b'wild'),
        ], xauth.FamilyLocal, b'new-host', 0), (COOKIE, b'wild'))

    def test_exact_match_preferred_over_wild_family(self):
        for entries in (
            [(xauth.FamilyWild, b'', b'', COOKIE, b'wild'), (xauth.FamilyLocal, b'host', b'0', COOKIE, b'exact')],
            [(xauth.FamilyLocal, b'host', b'0', COOKIE, b'exact'), (xauth.FamilyWild, b'', b'', COOKIE, b'wild')],
        ):
            self.assertEqual(self.get_best_auth(entries, xauth.FamilyLocal, b'host', 0), (COOKIE, b'exact'))

    def test_no_match(self):
        with self.assertRaises(error.XNoAuthError):
            self.get_best_auth([
                (xauth.FamilyLocal, b'other', b'0', COOKIE, b'wrong host'),
            ], xauth.FamilyLocal, b'host', 0)


class TestWarnings(unittest.TestCase):

    def read(self, raw):
        fd, filename = tempfile.mkstemp(prefix='xlib-test-', suffix='.Xauthority')
        self.addCleanup(os.unlink, filename)
        with os.fdopen(fd, 'wb') as f:
            f.write(raw)
        # Patched rather than `assertLogs`, which needs Python 3.4
        with patch.object(logging.getLogger('Xlib.xauth'), 'warning') as warning:
            auth = xauth.Xauthority(filename)
        return auth, filename, warning

    def test_valid(self):
        auth, _, warning = self.read(xauth_entry(xauth.FamilyLocal, b'host', b'0', COOKIE, b'cookie'))
        self.assertEqual(len(auth), 1)
        warning.assert_not_called()

    def test_truncated(self):
        entry = xauth_entry(xauth.FamilyLocal, b'host', b'0', COOKIE, b'cookie')
        auth, filename, warning = self.read(entry + b'\x01')
        self.assertEqual(len(auth), 1)
        warning.assert_called_once_with(
            'Failed to parse part of Xauthority file %s, ignoring the rest of it', filename)

    def test_empty(self):
        auth, filename, warning = self.read(b'')
        self.assertEqual(len(auth), 0)
        warning.assert_called_once_with('No Xauthority entries found in %s', filename)


class TestDefaultFilename(unittest.TestCase):

    def setUp(self):
        self.home = tempfile.mkdtemp(prefix='xlib-test-')
        self.addCleanup(os.rmdir, self.home)
        filename = os.path.join(self.home, '.Xauthority')
        with open(filename, 'wb') as f:
            f.write(xauth_entry(xauth.FamilyLocal, b'host', b'0', COOKIE, b'cookie'))
        self.addCleanup(os.unlink, filename)

    def test_home(self):
        with patch.dict(os.environ, {'HOME': self.home, 'USERPROFILE': 'elsewhere'}):
            os.environ.pop('XAUTHORITY', None)
            self.assertEqual(len(xauth.Xauthority()), 1)

    def test_user_profile_without_home(self):
        # As on Windows, where $HOME is usually unset
        with patch.dict(os.environ, {'USERPROFILE': self.home}):
            os.environ.pop('XAUTHORITY', None)
            os.environ.pop('HOME', None)
            self.assertEqual(len(xauth.Xauthority()), 1)

    def test_no_home(self):
        with patch.dict(os.environ):
            for name in ('XAUTHORITY', 'HOME', 'USERPROFILE'):
                os.environ.pop(name, None)
            with self.assertRaises(error.XauthError):
                xauth.Xauthority()


if __name__ == '__main__':
    unittest.main()
