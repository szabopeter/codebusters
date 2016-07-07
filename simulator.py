# import sys
# import math
import random

from coordinatesystem import Position, XC, YC

WIN0 = "Winner: 1st"
WIN1 = "Winner: 2nd"
DRAW = "Inconclusive"
KEEP_GOING = "let them fight"

STARTING_POSITIONS = {
    # todo find out actual starting positions
    2: ((100, 100,), (200, 200,),),
    3: ((100, 100,), (200, 200,), (300, 300,),),
    4: ((100, 100,), (200, 200,), (300, 300,), (400, 400),),
}

MAPW = 16001
MAPH = 9001
TEAMIDS = (0, 1,)
VISIBILITY = 2200
GHOST_MOVE_DIST = 400
BUSTER_MOVE_DIST = 800

STATE_STUNNED = 2
STATE_CARRYING = 1
STATE_IDLE = 0

STUN_RECHARGE = 20
STUN_EFFECT = 5  # todo


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
        self.max_move_dist = GHOST_MOVE_DIST


class Buster(MapObject):
    def __init__(self, nr, pos, tnr):
        MapObject.__init__(self, pos)
        self.nr = int(nr)
        self.tnr = tnr
        self.carries = None
        self.max_move_dist = BUSTER_MOVE_DIST

    def stun(self):
        self.state = STATE_STUNNED

    def grab(self, ghost):
        assert isinstance(ghost, Ghost)
        self.carries = ghost


class Command(object):
    def __init__(self):
        self.priority = 100

    def append_to(self, appendable):
        appendable.append(self)

    def execute(self):
        pass


class MoveCommand(Command):
    def __init__(self, actor, target):
        assert isinstance(actor, MapObject)
        assert isinstance(target, Position)
        self.actor = actor
        self.target = target
        self.priority =

    def execute(self):
        max_dist = self.actor.max_move_dist
        targetpos = self.actor.pos.towards(self.target, max_dist)


class StunCommand(Command):
    def __init__(self, actor, targetactor):
        assert isinstance(actor, Buster)
        assert isinstance(targetactor, Buster)
        self.actor = actor
        self.target = targetactor


class BustCommand(Command):
    def __init__(self, actor, targetactor):
        assert isinstance(actor, Buster)
        assert isinstance(targetactor, Ghost)
        self.actor = actor
        self.target = targetactor


class ReleaseCommand(Command):
    def __init__(self, actor):
        self.actor = actor


class FailedCommand(Command):
    def append(self, _):
        pass


class DoNothingCommand(Command):
    def __init__(self, actor):
        self.actor = actor


class SimulatorParams(object):
    def __init__(self, squadsize, ghostcount, seed):
        self.squadsize, self.ghostcount, self.seed = squadsize, ghostcount, seed


class Simulator(SimulatorParams):
    def __init__(self, params, algo0, algo1):
        SimulatorParams.__init__(self, params.squadsize, params.ghostcount, params.seed)
        random.seed(params.seed)
        self.algos = [algo0, algo1]
        self.scores = [0, 0]
        self.ghosts = []
        self.busters = []
        self.turn = 0
        self.actions = []
        self.commands = []

        # todo split up method
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
                if tnr:
                    x, y = MAPW - x, MAPH - y
                pos = Position(XC(x), YC(y))
                p1 = Buster(len(self.busters), pos, tnr)
                self.busters.append(p1)

    def inform_teams(self):
        for tnr in TEAMIDS:
            algo = self.algos[tnr]
            algo.start_turn()
            teampositions = [p.pos for p in self.busters if p.tnr == tnr]
            actors = self.busters[:] + self.ghosts[:]
            visibles = [a for a in actors if a.pos.is_close_to_any(teampositions, VISIBILITY)]
            for a in visibles:
                algo.update(a.nr, a.pos.getx(), a.pos.gety(), a.tnr, a.state, a.value)

    def create_command(self, buster, action):
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

    def ask_actions(self):
        actions = [list(self.algos[tnr].actions()) for tnr in TEAMIDS]
        return actions

    def prepare_commands(self, actions):
        commands = []
        for buster in self.busters:
            nextaction = actions[buster.nr][0]
            del actions[buster.nr][0]
            command = self.create_command(buster, nextaction)
            command.append_to(self.commands)

        for ghost in self.ghosts:
            command = self.make_ghost_command(ghost)
            command.append_to(self.commands)

        return commands

    def execute_commands(self, commands):
        commands.sort(key = lambda command: command.priority)
        for command in commands:
            command.execute()

    def make_ghost_command(self, ghost):
        # todo: move away
        return DoNothingCommand()

    def final_result(self):
        s0, s1 = self.scores
        t = self.ghostcount if self.turn < 401 else s0 + s1
        left = t - s0 - s1
        if s0 + left < s1:
            return WIN1
        if s1 + left < s0:
            return WIN0
        if s0 + s1 == t:
            return DRAW
        return KEEP_GOING

    def play(self):
        while self.final_result() == KEEP_GOING:
            self.inform_teams()
            actions = self.ask_actions()
            commands self.prepare_commands(actions)
            self.execute_commands(commands)
            self.turn += 1

