

class safefloat(float):
    def __truediv__(self, divisor):
        try:
            return float.__truediv__(self, divisor)
        except ZeroDivisionError:
            return self

class Ordinate(object):
    def __init__(self, val):
        self.val = int(val)

    def __str__(self):
        return str(self.val)

    def getval(self): return self.val

    def __int__(self): return self.val

    def __float__(self): return float(self.val)

    def __abs__(self): return self.modified(abs(self.getval()))

    def __eq__(self, other):
        return type(self) == type(other) and self.getval() == other.getval()

    def __lt__(self, other):
        assert isinstance(other, type(self)) or isinstance(self, type(other))
        return self.getval().__lt__(other.getval())

    def __le__(self, other):
        return self == other or self < other

    def __add__(self, other):
        assert type(self) == type(other)
        return self.modified(self.getval() + other.getval())

    def __sub__(self, other):
        assert type(self) == type(other)
        return self.modified(self.getval() - other.getval())

    def __mul__(self, multiplier):
        assert isinstance(multiplier, int) \
            or isinstance(multiplier, float)
        return self.modified(self.getval() * multiplier)

    def __truediv__(self, divisor):
        assert type(divisor) in (type(0), type(0.0))
        return self.modified(self.getval() / divisor)

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

    def towards(self, other, maxdist, boundary = None):
        assert boundary == None or isinstance(boundary, Boundary)
        assert boundary == None or boundary.contains(self)

        if boundary == None:
            boundary = Boundary(self, other)

        ld = maxdist
        lx = abs(other.x - self.x)
        ly = abs(other.y - self.y)

        if other.x > boundary.x2:
            lx = boundary.x2 - self.x
        if other.x < boundary.x1:
            lx = self.x - boundary.x1

        if other.y > boundary.y2:
            ly = boundary.y2 - self.x
        if other.y < boundary.y1:
            ly = self.y - boundary.y1

        dd = self.dist_to(other)
        dx = abs(other.x - self.x)
        dy = abs(other.y - self.y)

        if dd <= ld and dx <= lx and dy <= ly:
            return other

        rd = safefloat(ld) / int(dd)
        rx = safefloat(lx) / int(dx)
        ry = safefloat(ly) / int(dy)

        r = min(rd, rx, ry)
        
        x = (other.x - self.x) * r + self.x
        y = (other.y - self.y) * r + self.y
        return Position(x, y)


class Boundary(object):
    def __init__(self, p1, p2):
        assert isinstance(p1, Position)
        assert isinstance(p2, Position)
        self.x1, self.x2 = sorted([p1.x, p2.x,])
        self.y1, self.y2 = sorted([p1.y, p2.y,])

    def __contains__(self, p):
        return self.x1 <= p.x <= self.x2 and self.y1 <= p.y <= self.y2

    def contains(self, p):
        return p in self
