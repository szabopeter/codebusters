import unittest
from coordinatesystem import Ordinate, XC, YC, Position, Boundary


# todo split up class
class CoordinateSystemTestCase(unittest.TestCase):
    def testOrdinateEquality(self):
        self.assertNotEqual(XC(25), XC(444))
        self.assertEqual(XC(55), XC(55))
        self.assertNotEqual(XC(55), YC(55))

    def test_ordinate_ordering(self):
        o = Ordinate(5)
        x = XC(6)
        y = YC(7)
        self.assertLess(o, x)
        self.assertLessEqual(o, x)
        self.assertGreater(x, o)
        with self.assertRaises(AssertionError):
            x < y

        l = [        XC(5), XC(1), XC(2), XC(4), XC(6), XC(0), XC(2) ]
        self.assertEqual(XC(0), min(l))
        self.assertEqual(XC(6), max(l))
        expected = [ XC(0), XC(1), XC(2), XC(2), XC(4), XC(5), XC(6) ]
        self.assertListEqual(expected, sorted(l))

    def testOrdinateAddition(self):
        x1 = XC(100)
        x2 = XC(200)
        self.assertEqual(XC(300), x1 + x2)

    def test_ordinate_Substraction(self):
        x1 = XC(220)
        x2 = XC(100)
        self.assertEqual(XC(120), x1-x2)

    def testOrdinateMultiplication(self):
        x1 = XC(100)
        self.assertEqual(XC(300), x1 * 3.0)

    def test_ordinate_division(self):
        x1 = XC(100)
        self.assertEqual(XC(33), x1 / 3)
        self.assertEqual(XC(66), x1 * 2 / 3)

    def test_ordinate_weighted_midpoint(self):
        x1 = XC(100)
        x2 = XC(200)
        xm = x1 + (x2-x1) * 0.259
        self.assertEqual(XC(125), xm)

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
        self.assertEqual(expected, actual, str(expected) + "!=" + str(actual))

        boundary = Boundary(Position(XC(100), YC(0)), Position(XC(100+30), YC(999)))
        actual = origin.towards(target, 999, boundary)
        self.assertEqual(expected, actual)

        boundary = Boundary(Position(XC(0), YC(200-40)), Position(XC(999), YC(200)))
        actual = origin.towards(target, 999, boundary)
        self.assertEqual(expected, actual)

        expected = target
        actual = origin.towards(target, 999)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
