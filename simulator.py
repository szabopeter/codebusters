import sys
import math
import random

WIN0 = "Winner: 1st"
WIN1 = "Winner: 2nd"
DRAW = "Inconclusive"
KEEPGOING = "let them fight"

STARTING_POSITIONS = {
    #todo find out actual starting positions
    2: ((100,100,), (200,200,),                       ),
    3: ((100,100,), (200,200,), (300,300,),           ),
    4: ((100,100,), (200,200,), (300,300,), (400,400),),
}

MAPW = 16001
MAPH =  9001
TEAMIDS = (0, 1,)
VISIBILITY = 2200

STATE_STUNNED = 2
STATE_CARRYING = 1
STATE_IDLE = 0

STUN_RECHARGE = 20
STUN_EFFECT = 5 # todo

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

    def getx(self):
        return self.x.x

    def gety(self):
        return self.y.y

    def distTo(self, other):
        xd = self.getx()-other.getx()
        yd = self.gety()-other.gety()
        return int((xd**2 + yd**2)**0.5)

    def isVisibleToAny(self, poslist):
        for pos in poslist:
            if self.distTo(pos) <= VISIBILITY:
                return True
        return False

class MapObject(object):
    def __init__(self, pos):
        assert isinstance(pos, Position)
        self.pos = pos
        self.state = 0
        self.value = 0

class Ghost(MapObject):
    def __init__(self, nr, pos):
        MapObject.__init__(self, pos)
        self.nr = int(nr)
        self.tnr = -1

class Buster(MapObject):
    def __init__(self, nr, pos, tnr):
        MapObject.__init__(self, pos)
        self.nr = int(nr)
        self.tnr = tnr
        self.carries = None

    def stun(self):
        self.state = STATE_STUNNED

    def grab(self, ghost):
        assert isinstance(ghost, Ghost)
        self.carries = ghost

class SimulatorParams(object):
    def __init__(self, squadsize, ghostcount, seed):
        self.squadsize, self.ghostcount, self.seed = squadsize, ghostcount, seed

class Simulator(SimulatorParams):
    def __init__(self, params, algo0, algo1):
        SimulatorParams.__init__(self, params.squadsize, params.ghostcount, params.seed)
        random.seed(params.seed)
        self.algos = [ algo0, algo1 ]
        self.scores = [ 0, 0 ]
        self.ghosts = []
        self.busters = []
        self.turn = 0
        
        for i in range(params.ghostcount):
            x = XC(random.randrange(MAPW))
            y = YC(random.randrange(MAPH))
            g = Ghost(i, Position(x, y))
            self.ghosts.append(g)

        startingpositions = STARTING_POSITIONS[params.squadsize]
        for tnr in TEAMIDS:
            self.algos[tnr].setup(tnr, self.ghostcount, self.squadsize)
            for i in range(params.squadsize):
                x, y = startingpositions[i]
                if tnr: x, y = MAPW - x, MAPH - y
                pos = Position(XC(x), YC(y))
                p1 = Buster(len(self.busters), pos, tnr)
                self.busters.append(p1)

    def informTeams(self):
        for tnr in TEAMIDS:
            algo = self.algos[tnr]
            algo.start_turn()
            teampositions = [ p.pos for p in self.busters if p.tnr == tnr ]
            actors = self.busters[:] + self.ghosts[:]
            visibles = [ a for a in actors if a.pos.isVisibleToAny(teampositions) ]
            # todo isVisibleToAny
            for a in visibles:
                algo.update(a.nr, a.pos.getx(), a.pos.gety(), a.tnr, a.state, a.value)

    def createCommand(self, buster, action):
        ss = action.split()
        if ss[0] == "MOVE":
            target = Position(XC(ss[1]), YC(ss[2]))
            cmd = MoveCommand(buster, target)
        elif ss[0] == "STUN":
            targetid = int(ss[1])
            target = self.busters[targetid]
            cmd = StunCommand(buster, target)
        elif ss[0] == "BUST":
            targetid = int(ss[1])
            cmd = BustCommand(buster, self.ghosts[targetid])
        elif ss[0] == "RELEASE":
            cmd = ReleaseCommand(buster)
        else:
            cmd = FailedCommand(buster)
        return cmd

    def askActions(self):
        self.actions = [ list(self.algos[tnr].actions()) for tnr in TEAMIDS ]

    def executeActions(self):
        self.commands = []
        for buster in self.busters:
            nextaction = self.actions[buster.id][0]
            del self.actions[buster.id][0]
            command = self.createCommand(buster, nextaction)
            if command:
                self.commands.append(command)

    def moveGhosts(self):
        pass

    def finalResult(self):
        s0, s1 = self.scores
        t = self.ghostcount if self.turn < 401 else s0 + s1
        left = t - s0 - s1
        if s0 + left < s1: return WIN1
        if s1 + left < s0: return WIN0
        if s0 + s1 == t: return DRAW
        return KEEPGOING

    def play(self):
        while self.finalResult() == KEEPGOING:
            self.informTeams()
            self.askActions()
            self.executeActions()
            self.moveGhosts() # maybe incorporated in askActions
            self.turn += 1

