import sys
import math
import random

MAPW = 16001
MAPH = 9001
STUN_RECHARGE=20

def log(s):
    # To debug: print("Debug messages...", file=sys.stderr)
    print(s, file=sys.stderr)

# Send your busters out into the fog to trap ghosts and bring them home!

class p(object):
    def __init__(self, x, y, id):
        self.x, self.y, self.id = int(x), int(y), id
    
    def __str__(self):
        return "[%d: %d,%d]"%(self.id, self.x, self.y,)
    
def dist(p1, p2):
    return ((p1.x - p2.x)**2 + (p1.y-p2.y)**2)**0.5

def findaghost(buster, ghosts):
    for g in ghosts:
        d = dist(buster, g)
        if 900 <= d and d <= 1760:
            return g
            
    return None

def towards(buster, ghost):
    td = 1000
    d = dist(buster, ghost)
    xd = ghost.x - buster.x
    yd = ghost.y - buster.y
    return p(ghost.x - xd * 1400 / d, ghost.y - yd * 1400 / d, 0)

class gamestate(object):
    def __init__(self, my_team_id, ghost_count, busters_per_player):
        self.teamid = my_team_id
        self.ghostcount = ghost_count
        self.squadsize = busters_per_player
        self.targets = {}
        self.base = p(0,0,0) if my_team_id == 0 else p(MAPW-1, MAPH-1, 0)
        self.stun_used = {}
        self.turn = -1
        
    def start_turn(self):
        self.turn += 1
        self.ghosts = []
        self.team = []
        self.enemy = []
        self.carriers = []

    def update(self, entity_id, x, y, entity_type, state, value):
        if entity_type == -1:
            self.ghosts.append(p(x,y,entity_id))
        elif entity_type == my_team_id:
            buster = p(x,y,entity_id)
            buster.target = None
            self.team.append(buster)
            if state == 1: self.carriers.append(entity_id)
        else:
            self.enemy.append(p(x,y,entity_id))

    def actions(self):
        #ret commands
        for t in self.team:
            t.target = self.targets[t.id] if t.id in self.targets else None
            log("Current target for " + str(t) + " is " + str(t.target))
            if not t.id in self.targets:
                t.target = p(random.randrange(MAPW), random.randrange(MAPH), 0)
                self.targets[t.id] = t.target
                log("New target for " + str(t) + " is " + str(t.target))

            target = t.target
            
            if t.id in self.carriers:
                if t.x == self.base.x and t.y == self.base.y:
                    yield "RELEASE I ain't afraid of no ghost!"
                    del self.targets[t.id]
                else:
                    yield "MOVE %d %d"%(self.base.x, self.base.y,)
            else:
                canstun = not t.id in self.stun_used or turn - self.stun_used[t.id] >= STUN_RECHARGE
                e = findaghost(t, enemy) if canstun else None
                if e:
                    yield "STUN %d Get lost copycat!"%(e.id,)
                else:
                    g = findaghost(t, ghosts)
                    if g:
                        yield "BUST %d Ghost Busters!"%(g.id,)
                    elif t.x == target.x and t.y == target.y:
                        log("In position, but no target...")
                        yield "MOVE %d %d Who you gonna call?"%(target.x, target.y,)
                        del self.targets[t.id]
                    else:
                        yield "MOVE %d %d"%(target.x, target.y,)



busters_per_player = int(input())  # the amount of busters you control
ghost_count = int(input())  # the amount of ghosts on the map
my_team_id = int(input())  # if this is 0, your base is on the top left of the map, if it is one, on the bottom right

state = gamestate(my_team_id, ghost_count, busters_per_player)

# game loop
while True:
    entities = int(input())  # the number of busters and ghosts visible to you
    for i in range(entities):
        # entity_id: buster id or ghost id
        # y: position of this buster / ghost
        # entity_type: the team id if it is a buster, -1 if it is a ghost.
        # state: For busters: 0=idle, 1=carrying a ghost.
        # value: For busters: Ghost id being carried. For ghosts: number of busters attempting to trap this ghost.
        entity_id, x, y, entity_type, state, value = [int(j) for j in input().split()]
        gamestate.update(entity_id, x, y, entity_type, state, value)
            
    for cmd in gamestate.actions():
        print (cmd)

        
        # Write an action using print
        # MOVE x y | BUST id | RELEASE

