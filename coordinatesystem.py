import unittest

class Ordinate(object):
    def __init__(self, val):
        self.val = int(val)

    def getval(self): return self.val

    def __int__(self): return self.val

    def __eq__(self, other):
        return type(self) == type(other) and self.getval() == other.getval()

    def __add__(self, other):
        assert type(self) == type(other)
        return self.modified(self.getval() + other.getval())

    def __sub__(self, other):
        assert type(self) == type(other)
        return self.modified(self.getval() - other.getval())

    def __mul__(self, multiplier):
        assert type(multiplier) in (type(0), type(0.0))
        return self.modified(self.getval() * multiplier)

class XC(Ordinate):
    def modified(self, value):
        return XC(value)

class YC(Ordinate):
    def modified(self, value):
        return YC(value)

class Position(object):
    def __init__(self, x, y):
        assert isinstance(x, XC)
        assert isinstance(y, YC)
        self.x, self.y = x, y

    def __eq__(self, other):
        assert isinstance(other, Position)
        return self.x == other.x and self.y == other.y

    def getx(self):
        return self.x.getval()

    def gety(self):
        return self.y.getval()

    def distTo(self, other):
        xd = int(self.x - other.x)
        yd = int(self.y - other.y)
        return int((xd**2 + yd**2)**0.5)

    def isCloseToAny(self, poslist, maxdist):
        for pos in poslist:
            if self.distTo(pos) <= maxdist:
                return True
        return False

    def towards(self, other, maxdist):
        dist = self.distTo(other)
        if dist <= maxdist:
            return other
        r = maxdist / dist
        x = (other.x - self.x) * r + self.x
        y = (other.y - self.y) * r + self.y
        return Position(x, y)

class coordinatesystemTestcase(unittest.TestCase):
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
        p2 = Position(XC(100+300), YC(200+400))
        self.assertEqual(0, p1.distTo(p1))
        self.assertEqual(500, p1.distTo(p2))
        self.assertEqual(500, p2.distTo(p1))

    def testIsCloseTo(self):
        p0 = Position(XC(100), YC(200))
        pts = (
            Position(XC(100+30), YC(200+40)),
            Position(XC(100+60), YC(200+80)),
            Position(XC(100-90), YC(200-120)),
            )
        self.assertTrue(p0.isCloseToAny(pts, 50))
        self.assertFalse(p0.isCloseToAny(pts, 49))
        self.assertTrue(pts[2].isCloseToAny(pts, 0))

    def testTowards(self):
        origin = Position(XC(100), YC(200))
        target = Position(XC(100+2*30), YC(200-2*40))
        expected = Position(XC(100+30), YC(200-40))
        actual = origin.towards(target, 50)
        self.assertEqual(expected, actual)

        expected = target
        actual = origin.towards(target, 999)
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
