import unittest
from unittest.mock import Mock, patch

from Xlib.xobject import colormap


class TestColormap(unittest.TestCase):

    def test_copy_colormap_and_free(self):
        display = Mock()
        display.allocate_resource_id.return_value = 42
        display.get_resource_class.return_value = colormap.Colormap
        cmap = colormap.Colormap(display, 1)
        with patch.object(colormap.request, 'CopyColormapAndFree') as req:
            new_cmap = cmap.copy_colormap_and_free(7)
        req.assert_called_once_with(display=display, mid=42, src_cmap=7)
        self.assertIsInstance(new_cmap, colormap.Colormap)
        self.assertEqual(new_cmap.id, 42)


if __name__ == '__main__':
    unittest.main()
