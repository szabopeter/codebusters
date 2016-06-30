import sys
import math
import random

MAPW=16001
MAPH=9001

WIN0="Winner: 1st"
WIN1="Winner: 2nd"
DRAW="Inconclusive"
KEEPGOING="let them fight"

STARTING_POSITIONS = {
    #todo find out actual starting positions
    2: ((100,100,), (200,200,),                       ),
    3: ((100,100,), (200,200,), (300,300,),           ),
    4: ((100,100,), (200,200,), (300,300,), (400,400),),
}

class XC(object):
    def __init__(self, x):
        self.x = int(x)

class YC(object):
    def __init__(self, y):
        self.y = int(y)

class Position(object):
    def __init__(self, x, y):
        assert isinstance(x, XC)
        assert isinstance(y, YC)
        self.x, self.y = x, y

class MapObject(object):
    def __init__(self, pos):
        assert isinstance(pos, Position)
        self.pos = pos

class Ghost(MapObject):
    def __init__(self, nr, pos):
        MapObject.__init__(self, pos)
        self.nr = int(nr)

class Player(MapObject):
    def __init__(self, nr, pos, tnr):
        MapObject.__init__(self, pos)
        self.nr = int(nr)
        self.tnr = tnr
        

class SimulatorParams(object):
    def __init__(self, squadsize, ghostcount, seed):
        self.squadsize, self.ghostcount, self.seed = squadsize, ghostcount, seed

class Simulator(SimulatorParams):
    def __init__(self, params, algo0, algo1):
        SimulatorParams.__init__(self, params.squadsize, params.ghostcount, params.seed)
        random.seed(params.seed)
        self.algos = [ algo0, algo1 ]
        self.scores = [ 0, 0 ]
        self.ghosts = {}
        self.players = []
        self.turn = 0
        
        for i in range(params.ghostcount):
            x = XC(random.randrange(MAPW))
            y = YC(random.randrange(MAPH))
            self.ghosts[i] = Ghost(i, Position(x, y))

        startingpositions = STARTING_POSITIONS[params.squadsize]
        for tnr in (0, 1):
            self.algos[tnr].setup(tnr, self.ghostcount, self.squadsize)
            for i in range(params.squadsize):
                x, y = startingpositions[i]
                if tnr: x, y = MAPW - x, MAPH - y
                pos = Position(XC(x), YC(y))
                p1 = Player(len(self.players), pos, tnr)
                self.players.append(p1)

    def finalResult(self):
        s0, s1 = self.scores
        t = self.ghostcount if self.turn < 401 else s0 + s1
        left = t - s0 - s1
        if s0 + left < s1: return WIN1
        if s1 + left < s0: return WIN0
        if s0 + s1 == t: return DRAW
        return KEEPGOING

    def askActions(self):
        pass

    def executeActions(self):
        pass

    def moveGhosts(self):
        pass

    def play(self):
        while self.finalResult() == KEEPGOING:
            self.askActions()
            self.executeActions()
            self.moveGhosts()
            self.turn += 1

