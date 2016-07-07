

class Ordinate(object):
    def __init__(self, val):
        self.val = int(val)

    def __str__(self):
        return str(self.val)

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

    def modified(self, value):
        return Ordinate(value)


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

    def __str__(self):
        return "(%s, %s)"%(self.x, self.y,)

    def __eq__(self, other):
        assert isinstance(other, Position)
        return self.x == other.x and self.y == other.y

    def getx(self):
        return self.x.getval()

    def gety(self):
        return self.y.getval()

    def dist_to(self, other):
        xd = int(self.x - other.x)
        yd = int(self.y - other.y)
        return int((xd ** 2 + yd ** 2) ** 0.5)

    def is_close_to_any(self, poslist, maxdist):
        for pos in poslist:
            if self.dist_to(pos) <= maxdist:
                return True
        return False

    def towards(self, other, maxdist):
        dist = self.dist_to(other)
        if dist <= maxdist:
            return other
        r = float(maxdist) / dist
        print("%s / %s = %s"%(maxdist, dist, r,))
        x = (other.x - self.x) * r + self.x
        y = (other.y - self.y) * r + self.y
        return Position(x, y)
