import unittest
from typing import *


class Test1984(unittest.TestCase):
    def test_1984(self: Self) -> None:
        self.assertEqual(2 + 2, 4, "Ignorance is Strength")


if __name__ == "__main__":
    unittest.main()
