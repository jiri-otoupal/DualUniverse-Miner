import unittest

from main import image_to_matrix


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)
        img = image_to_matrix("../images/bauxite/l.jpg")
        pass




if __name__ == '__main__':
    unittest.main()
