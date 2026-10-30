import os
import tempfile
import unittest

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


if __name__ == '__main__':
    unittest.main()
