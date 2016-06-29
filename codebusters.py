import sys
import math
import random

MAPW = 16001
MAPH = 9001
GRIDSIZE = 2000
STUN_RECHARGE = 20
DEFAULTBASEOFFSET = 1100
SHOOTMIN = 900
SHOOTMAX = 1760

TODO="""
select different targets, especially in the opening turns
detect if the last command was executed successfully
"""

def log(s):
    # To debug: print("Debug messages...", file=sys.stderr)
    print(s, file=sys.stderr)

# Send your busters out into the fog to trap ghosts and bring them home!

class p(object):
    def __init__(self, x, y, id = 0):
        self.x, self.y, self.id = int(x), int(y), id

    def __str__(self):
        return "[%d: %d,%d]"%(self.id, self.x, self.y,)

def dist(p1, p2):
    return ((p1.x - p2.x)**2 + (p1.y-p2.y)**2)**0.5

def celldist(origo, cell):
    xd = origo.x - cell.center.x
    yd = origo.y - cell.center.y
    return math.sqrt(xd**2 + yd**2)

def isshootingdistance(d):
    return SHOOTMIN <= d and d <= SHOOTMAX

def sortdistances(origo, points):
    if not points: return []
    withdistances = [ (dist(origo, pt), pt,) for pt in points ]
    withdistances.sort(key=lambda pair:pair[0])
    return withdistances

def findshootable(shooter, targets):
    distancesandtargets = sortdistances(shooter, targets)
    if distancesandtargets: 
        log("%d spotted: %s"%(shooter.id, [ pair[0] for pair in distancesandtargets ],))

    filteredfordist = [ pair for pair in distancesandtargets if isshootingdistance(pair[0]) ]
    return filteredfordist[0][1] if filteredfordist else None

def towards(buster, ghost):
    TD = 1500
    d = dist(buster, ghost)
    xd = ghost.x - buster.x
    yd = ghost.y - buster.y
    return p(ghost.x - xd * TD / d, ghost.y - yd * TD / d)

def getbase(teamid, offset=DEFAULTBASEOFFSET):
    return p(offset, offset) if teamid == 0 else p(MAPW-offset, MAPH-offset)
    
class grid(object):
    def __init__(self, gridsize):
        self.gridsize = gridsize
        self.w, self.h = int(MAPW/gridsize), int(MAPH/gridsize)
        if MAPW%gridsize>100: self.w += 1
        if MAPH%gridsize>100: self.h += 1
        self.data = [ [ self.createcell(x, y) for x in range(self.w) ] for y in range(self.h) ]

    def getcells(self):
        flat = []
        for line in self.data:
            for cell in line:
                flat.append(cell)
        return flat

    def getfor(self, x, y):
        gy = int(y/self.gridsize)
        if (gy >= len(self.data)): gy = len(self.data)-1
        gx = int(x/self.gridsize)
        if (gx >= len(self.data[gy])): gx = len(self.data[gy])-1
        return self.data[gy][gx]

    def closest(self, origo, data):
        distances = [ (cell, celldist(origo, cell),) for cell in data ]
        distances.sort(key=lambda item:item[1])
        closestcell = distances[0][0]
        log("Chose %d,%d from %d items"%(closestcell.x, closestcell.y, len(distances),))
        return closestcell
    
    def createcell(self, gx, gy):
        cell = p(gx, gy)
        cell.center = self.centerof(cell)
        return cell

    def centerof(self, cell):
        gx, gy = cell.x*self.gridsize, cell.y*self.gridsize
        ngx, ngy = gx + self.gridsize, gy + self.gridsize
        if ngx>MAPW: ngx = MAPW
        if ngy>MAPH: ngy = MAPH
        cx = int((gx+ngx)/2)
        cy = int((gy+ngy)/2)
        return p(cx, cy)

class gamestate(object):
    def __init__(self, my_team_id, ghost_count, busters_per_player):
        self.teamid = my_team_id
        self.ghostcount = ghost_count
        self.squadsize = busters_per_player
        self.targets = {}
        self.base = getbase(my_team_id)
        self.stun_used = {}
        self.turn = -1
        self.neutralized = []
        self.ghostmem = {}
        self.grid = grid(GRIDSIZE)
        self.toexplore = self.grid.getcells()
    
    def start_turn(self):
        self.turn += 1
        self.ghosts = []
        self.team = []
        self.enemy = []
        self.carriers = []

    def updatebuster(self, entity_id, x, y, state):
        buster = p(x, y, entity_id)
        self.team.append(buster)
        if state == 1: self.carriers.append(entity_id)
        #todo: stuned state
        currentcell = self.grid.getfor(buster.x, buster.y)
        if currentcell in self.toexplore: self.toexplore.remove(currentcell)
        return buster

    def updateghost(self, entity_id, x, y):
        newghost = p(x,y,entity_id)
        self.ghosts.append(newghost)
        if not entity_id in self.ghostmem:
            self.ghostmem[entity_id] = newghost
        return newghost
    
    def updateenemy(self, entity_id, x, y, hasghost, ghostid):
        newenemy = p(x,y,entity_id)
        self.enemy.append(newenemy)
        if hasghost == 1 and ghostid in self.ghostmem: del self.ghostmem[ghostid]
        return newenemy

    def update(self, entity_id, x, y, entity_type, state, value):
        if entity_type == -1:
            self.updateghost(entity_id, x, y)
        elif entity_type == my_team_id:
            buster = self.updatebuster(entity_id, x, y, state)
            #todo: what about carried ghosts?
            buster.target = None
        else:
            self.updateenemy(entity_id, x, y, state, value)

    def actions(self):
        #ret commands
        firstbuster = self.team[0].id
        for t in self.team:
            terminator = t.id == firstbuster \
                and len(self.team) > 1 \
                and len(self.team)>len(self.neutralized) \
                and (not t.id in self.stun_used or self.turn - self.stun_used[t.id] >= STUN_RECHARGE / 2)
            t.target = self.targets[t.id] if t.id in self.targets else None
            log("Current target for " + str(t) + " is " + str(t.target))
            if not t.id in self.targets:
                if terminator:
                    enemybase = getbase(1-self.teamid, 1600)
                    t.target = enemybase
                else:
                    if self.ghostmem:
                        ghosts = self.ghostmem.values()
                        ghostdists = [ (dist(t, g), g,) for g in ghosts]
                        filtered = []
                        for d, g in ghostdists:
                            if d < 20:
                                del self.ghostmem[g.id]
                            else:
                                filtered.append((d,g,))
                        if filtered:
                            ghostdists = filtered
                            ghostdists.sort(key=lambda pair: pair[0])
                            t.target = ghostdists[0][1]
                    if not t.target:
                        tcell = self.grid.closest(t, self.toexplore)
                        center = self.grid.centerof(tcell)
                        t.target = p(center.x, center.y)
                self.targets[t.id] = t.target
                log("New target for " + str(t) + " is " + str(t.target))

            target = t.target

            if t.id in self.carriers:
                if t.x == self.base.x and t.y == self.base.y:
                    yield "RELEASE I ain't afraid of no ghost!"
                    ghostid = self.targets[t.id].id
                    if ghostid in self.ghostmem:
                        del self.ghostmem[ghostid]
                    del self.targets[t.id]
                else:
                    yield "MOVE %d %d"%(self.base.x, self.base.y,)
            else:
                canstun = not t.id in self.stun_used or self.turn - self.stun_used[t.id] >= STUN_RECHARGE
                closeenemies = [ enemy for enemy in self.enemy if not enemy in self.neutralized ]
                e = findshootable(t, closeenemies) if canstun else None
                if e:
                    yield "STUN %d Get lost copycat!"%(e.id,)
                    self.stun_used[t.id] = self.turn
                    #self.neutralized.append(e.id)
                else:
                    g = findshootable(t, self.ghosts) if not terminator else None
                    if g:
                        yield "BUST %d Ghost Busters!"%(g.id,)
                    elif t.x == target.x and t.y == target.y:
                        log("%d in position, but no target..."%(t.id))
                        yield "MOVE %d %d Who you gonna call?"%(target.x, target.y,)
                        del self.targets[t.id]
                    else:
                        yield "MOVE %d %d"%(target.x, target.y,)
                        
    def dump(self):
        log("----------")
        for r in range(self.grid.h):
            row = ""
            for c in range(self.grid.w):
                if self.grid.data[r][c] in self.toexplore: row += "*"
                else: row += " "
            log(row)

busters_per_player = int(input())  # the amount of busters you control
ghost_count = int(input())  # the amount of ghosts on the map
my_team_id = int(input())  # if this is 0, your base is on the top left of the map, if it is one, on the bottom right

state = gamestate(my_team_id, ghost_count, busters_per_player)

# game loop
while True:
    entities = int(input())  # the number of busters and ghosts visible to you
    state.start_turn()
    
    for i in range(entities):
        # entity_id: buster id or ghost id
        # y: position of this buster / ghost
        # entity_type: the team id if it is a buster, -1 if it is a ghost.
        # state: For busters: 0=idle, 1=carrying a ghost.
        # value: For busters: Ghost id being carried. For ghosts: number of busters attempting to trap this ghost.
        entity_id, x, y, entity_type, entity_state, value = [int(j) for j in input().split()]
        state.update(entity_id, x, y, entity_type, entity_state, value)
        state.dump()
            
    for cmd in state.actions():
        print (cmd)

        
        # Write an action using print
        # MOVE x y | BUST id | RELEASE

