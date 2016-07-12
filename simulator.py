# import sys
# import math
import random

from coordinatesystem import Position, XC, YC, Boundary

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
MAPB = Boundary(Position(XC(0),YC(0)), Position(XC(MAPW-1),YC(MAPH-1)))

TEAMIDS = (0, 1,)
VISIBILITY = 2200
GHOST_MOVE_DIST = 400
BUSTER_MOVE_DIST = 800

STATE_STUNNED = 2
STATE_CARRYING = 1
STATE_IDLE = 0
STATE_ILLEGAL = 9
STATE_UNSET = 8
STATE_CARRIED = 7
STATE_FINISHED = 6
ACTIVE_GHOST_STATES = (STATE_IDLE,)
ACTIVE_BUSTER_STATES = (STATE_IDLE, STATE_STUNNED, STATE_CARRYING,)

STUN_RECHARGE = 20
STUN_EFFECT = 5  # todo

BASEOFFSET = 200 # todo
BASECENTER = (
    Position(XC(BASEOFFSET),YC(BASEOFFSET)),
    Position(XC(MAPW-BASEOFFSET), YC(MAPH-BASEOFFSET)),
    )
BASERANGE = 600 # todo

def dbg(msg):
    print(msg)


class MapObject(object):
    def __init__(self, pos):
        assert isinstance(pos, Position)
        self.pos = pos
        self.state = STATE_IDLE

    def set_position(self, newpos):
        self.pos = newpos


class Ghost(MapObject):
    def __init__(self, nr, pos):
        MapObject.__init__(self, pos)
        self.nr = int(nr)
        self.tnr = -1
        self.max_move_dist = GHOST_MOVE_DIST

    def invalidate(self):
        pass

    def is_carried(self):
        return self.state == STATE_CARRIED

    def finish(self):
        self.state = STATE_FINISHED

    def is_active(self):
        return self.state in ACTIVE_GHOST_STATES

    def release(self, pos):
        self.pos = pos
        self.state = STATE_IDLE

    def get_value(self):
        return 1 # todo stamina

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
        ghost.state = STATE_CARRIED

    def is_carrying(self):
        return self.carries != None

    def get_value(self):
        return self.carries.nr if self.carries else -1

    def release(self):
        self.carries.release(self.pos)
        self.carries = None

    def invalidate(self):
        self.state = STATE_ILLEGAL

    def is_active(self):
        return self.state in ACTIVE_BUSTER_STATES

class Command(object):
    def __init__(self):
        self.priority = 100

    def execute(self):
        pass


class MoveCommand(Command):
    def __init__(self, actor, target):
        Command.__init__(self)
        assert isinstance(actor, MapObject)
        assert isinstance(target, Position)
        self.actor = actor
        self.target = target
        self.priority = 50

    def execute(self):
        if not self.target in MAPB:
            actor.invalidate()
            return False

        max_dist = self.actor.max_move_dist
        targetpos = self.actor.pos.towards(self.target, max_dist, MAPB)
        self.actor.set_position(targetpos)
        return True


class StunCommand(Command):
    def __init__(self, actor, targetactor):
        Command.__init__(self)
        assert isinstance(actor, Buster)
        assert isinstance(targetactor, Buster)
        self.actor = actor
        self.target = targetactor
        self.priority = 10


class BustCommand(Command):
    def __init__(self, actor, targetactor):
        Command.__init__(self)
        assert isinstance(actor, Buster)
        assert isinstance(targetactor, Ghost)
        self.actor = actor
        self.target = targetactor
        self.priority = 20

    def execute(self):
        if self.target.is_carried():
            self.actor.invalidate()
            return False

        self.actor.grab(self.target)
        return True

class ReleaseCommand(Command):
    def __init__(self, simulator, actor):
        Command.__init__(self)
        self.simulator = simulator
        self.actor = actor
        self.priority = 30

    def execute():
        if not self.actor.is_carrying():
            self.invalidate()
            return False

        ghost = self.actor.carries
        self.actor.release()

        TBASE = BASECENTER[self.actor.tnr]
        if ghost.pos.dist_to(TBASE) <= BASERANGE:
            ghost.finish()
            self.simulator.score(self.actor.tnr)

        return True

class FailedCommand(Command):
    def append(self, _):
        pass


class DoNothingCommand(Command):
    def __init__(self, actor):
        Command.__init__(self)
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

    def score(self, tnr):
        self.scores[tnr] += 1

    def inform_teams(self):
        for tnr in TEAMIDS:
            algo = self.algos[tnr]
            algo.start_turn()
            teampositions = [p.pos for p in self.busters if p.tnr == tnr]
            actors = self.busters[:] + self.ghosts[:]
            visibles = [
                a for a in actors 
                if a.is_active()
                and a.pos.is_close_to_any(teampositions, VISIBILITY) 
                ]
            dbg(visibles)
            for a in visibles:
                algo.update(a.nr, a.pos.getx(), a.pos.gety(), a.tnr, a.state, a.get_value())

    def create_command(self, buster, action):
        ss = action.split()
        # todo: register invalid actions
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
            cmd = ReleaseCommand(self, buster)
        else:
            cmd = FailedCommand(buster)
        dbg("%s => %s"%(action, cmd,))
        return cmd

    def ask_actions(self):
        actions = [list(self.algos[tnr].actions()) for tnr in TEAMIDS]
        return actions

    def prepare_commands(self, actions):
        commands = []
        for buster in self.busters:
            dbg(actions)
            dbg("actions[%d][%d] is next action"%(buster.tnr, 0,))
            nextaction = actions[buster.tnr][0]
            dbg(nextaction)
            del actions[buster.tnr][0]
            command = self.create_command(buster, nextaction)
            commands.append(command)

        for ghost in self.ghosts:
            command = self.make_ghost_command(ghost)
            commands.append(command)

        return commands

    def execute_commands(self, commands):
        dbg(commands)
        commands.sort(key = lambda command: command.priority)
        for command in commands:
            command.execute()

    def make_ghost_command(self, ghost):
        # todo: move away
        return DoNothingCommand(ghost)

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
            commands = self.prepare_commands(actions)
            self.execute_commands(commands)
            self.turn += 1

