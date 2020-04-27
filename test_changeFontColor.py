import changeFontColor as cfc
import unittest

class TestChangeFontColor(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestChangeFontColor, self).__init__(*args, **kwargs)
        self.rgbVal = (255, 125, 20)
        self.hexVal = 'ff7d14'

    def test_rgbToHex(self):
        out = cfc.ChangeFontColor.rgbToHex(None, self.rgbVal)
        self.assertEqual(out, self.hexVal)
        self.assertEqual(type(out), str)

    def test_hexToRgb(self):
        out = cfc.ChangeFontColor.hexToRgb(None, self.hexVal)
        self.assertEqual(out, self.rgbVal)
        self.assertEqual(type(out), tuple)

if __name__ == '__main__':
    unittest.main()