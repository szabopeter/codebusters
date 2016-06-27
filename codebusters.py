import sys
import math
import random

def log(s):
    print(s, file=sys.stderr)

# Send your busters out into the fog to trap ghosts and bring them home!

busters_per_player = int(input())  # the amount of busters you control
ghost_count = int(input())  # the amount of ghosts on the map
my_team_id = int(input())  # if this is 0, your base is on the top left of the map, if it is one, on the bottom right

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

state = 'GO'
targets = {}
base = p(0,0,0) if my_team_id == 0 else p(16000, 9000, 0)
stun_used = {}

# game loop
turn = -1
while True:
    turn += 1
    entities = int(input())  # the number of busters and ghosts visible to you
    ghosts = []
    team = []
    enemy = []
    carriers = []
    for i in range(entities):
        # entity_id: buster id or ghost id
        # y: position of this buster / ghost
        # entity_type: the team id if it is a buster, -1 if it is a ghost.
        # state: For busters: 0=idle, 1=carrying a ghost.
        # value: For busters: Ghost id being carried. For ghosts: number of busters attempting to trap this ghost.
        entity_id, x, y, entity_type, state, value = [int(j) for j in input().split()]
        if entity_type == -1:
            ghosts.append(p(x,y,entity_id))
        elif entity_type == my_team_id:
            buster = p(x,y,entity_id)
            buster.target = None
            team.append(buster)
            if state == 1: carriers.append(entity_id)
        else:
            enemy.append(p(x,y,entity_id))
            
    for t in team:
        t.target = targets[t.id] if t.id in targets else None
        log("Current target for " + str(t) + " is " + str(t.target))
        if not t.id in targets:
            # tg = ghosts[random.randrange(len(ghosts))]
            # t.target = towards(t, tg)
            t.target = p(random.randrange(16001), random.randrange(9001), 0)
            targets[t.id] = t.target
            log("New target for " + str(t) + " is " + str(t.target))
        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr)

        # MOVE x y | BUST id | RELEASE

        target = t.target
        
        if t.id in carriers:
            if t.x == base.x and t.y == base.y:
                print("RELEASE I ain't afraid of no ghost!")
                del targets[t.id]
            else:
                print("MOVE %d %d"%(base.x, base.y,))
        else:
            canstun = not t.id in stun_used or turn - stun_used[t.id] >= 20
            e = findaghost(t, enemy) if canstun else None
            if e:
                print("STUN %d Get lost copycat!"%(e.id,))
            else:
                g = findaghost(t, ghosts)
                if g:
                    print("BUST %d Ghost Busters!"%(g.id,))
                elif t.x == target.x and t.y == target.y:
                    log("In position, but no target...")
                    print("MOVE %d %d Who you gonna call?"%(target.x, target.y,))
                    del targets[t.id]
                else:
                    print("MOVE %d %d"%(target.x, target.y,))
        

