import unittest
from coordinatesystem import XC, YC, Position


class CoordinateSystemTestCase(unittest.TestCase):
    def testOrdinateEquality(self):
        self.assertNotEqual(XC(25), XC(444))
        self.assertEqual(XC(55), XC(55))
        self.assertNotEqual(XC(55), YC(55))

    def testOrindateAddition(self):
        x1 = XC(100)
        x2 = XC(200)
        self.assertEqual(XC(300), x1 + x2)

    def testOrdinateMultiplication(self):
        x1 = XC(100)
        self.assertEqual(XC(300), x1 * 3)

    def testPositionEquality(self):
        p1 = Position(XC(100), YC(180))
        p2 = Position(XC(55), YC(60))
        self.assertNotEqual(p1, p2)
        self.assertEqual(p1, Position(XC(100), YC(180)))

    def testDistTo(self):
        p1 = Position(XC(100), YC(200))
        p2 = Position(XC(100 + 300), YC(200 + 400))
        self.assertEqual(0, p1.dist_to(p1))
        self.assertEqual(500, p1.dist_to(p2))
        self.assertEqual(500, p2.dist_to(p1))

    def testIsCloseTo(self):
        p0 = Position(XC(100), YC(200))
        pts = (
            Position(XC(100 + 30), YC(200 + 40)),
            Position(XC(100 + 60), YC(200 + 80)),
            Position(XC(100 - 90), YC(200 - 120)),
        )
        self.assertTrue(p0.is_close_to_any(pts, 50))
        self.assertFalse(p0.is_close_to_any(pts, 49))
        self.assertTrue(pts[2].is_close_to_any(pts, 0))

    def testTowards(self):
        origin = Position(XC(100), YC(200))
        target = Position(XC(100 + 2 * 30), YC(200 - 2 * 40))
        expected = Position(XC(100 + 30), YC(200 - 40))
        actual = origin.towards(target, 50)
        self.assertEqual(expected, actual)

        expected = target
        actual = origin.towards(target, 999)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
