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
Remember the ghosts we carry. And forget the ones we lost.
Insist less on set targets.
Target carriers instead of strong ghosts.
Be prepared for terminator duty.
???
PROFIT!
"""

def log(s):
    # To debug: print("Debug messages...", file=sys.stderr)
    print(s, file=sys.stderr)

# Send your busters out into the fog to trap ghosts and bring them home!

class Point(object):
    def __init__(self, x, y, id = 0):
        self.x, self.y, self.id = int(x), int(y), id

    def __str__(self):
        return "[%d: %d,%d]"%(self.id, self.x, self.y,)

class Cell(Point):
    def __init__(self, pt, center):
        Point.__init__(self, pt.x, pt.y)
        self.center = center

class Actor(Point):
    def __init__(self, x, y, id):
        Point.__init__(self, x, y, id)

class Enemy(Actor):
    pass

class Buster(Actor):
    def __init__(self, x, y, id):
        Point.__init__(self, x, y, id)
        self.target = None

class Ghost(Actor):
    pass

NOTCARRYING="Not carrying"

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
    return Point(offset, offset) if teamid == 0 else Point(MAPW-offset, MAPH-offset)
    
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
        pt = Point(gx, gy)
        return Cell(pt, self.centerof(pt))

    def centerof(self, cell):
        gx, gy = cell.x*self.gridsize, cell.y*self.gridsize
        ngx, ngy = gx + self.gridsize, gy + self.gridsize
        if ngx>MAPW: ngx = MAPW
        if ngy>MAPH: ngy = MAPH
        cx = int((gx+ngx)/2)
        cy = int((gy+ngy)/2)
        return Point(cx, cy)

class gamestate(object):
    def __init__(self):
        pass

    def setup(self, my_team_id, ghost_count, busters_per_player):
        self.teamid = my_team_id
        self.ghostcount = ghost_count
        self.squadsize = busters_per_player
        self.base = getbase(my_team_id)
        self.stun_used = {}
        self.turn = -1
        self.neutralized = []
        self.ghostmem = {}
        self.grid = grid(GRIDSIZE)
        self.toexplore = self.grid.getcells()
        self.team = {}
        self.enemy = {}
    
    def start_turn(self):
        self.turn += 1
        self.ghosts = []

    def turnsuntilstun(self, buster):
        if not buster.id in self.stun_used: return 0
        turnspassed = self.turn - self.stun_used[buster.id]
        return STUN_RECHARGE - turnspassed

    def updateghost(self, entity_id, x, y, stamina):
        newghost = Ghost(x,y,entity_id)
        newghost.stamina = stamina
        self.ghosts.append(newghost)
        if not entity_id in self.ghostmem:
            self.ghostmem[entity_id] = newghost
        return newghost
    
    def updatebuster(self, entity_id, x, y, state, ghostcarried):
        if not entity_id in self.team:
            self.team[entity_id] = Buster(x, y, entity_id)
        buster = self.team[entity_id]
        buster.x, buster.y = x, y
        buster.carrying = ghostcarried if state == 1 else NOTCARRYING
        buster.isstunned = state == 2
        if buster.isstunned: buster.target = None
        currentcell = self.grid.getfor(buster.x, buster.y)
        if currentcell in self.toexplore: self.toexplore.remove(currentcell)
        return buster

    def updateenemy(self, entity_id, x, y, state, ghostid):
        if not entity_id in self.enemy:
            self.enemy[entity_id] = Enemy(x, y, entity_id)
        enemy = self.enemy[entity_id]
        enemy.x, enemy.y = x, y
        if state == 1 and ghostid in self.ghostmem: del self.ghostmem[ghostid]
        enemy.carrying = ghostid if state == 1 else NOTCARRYING
        enemy.isstunned = state == 2
        return enemy

    def update(self, entity_id, x, y, entity_type, state, value):
        if entity_type == -1:
            self.updateghost(entity_id, x, y, state)
        elif entity_type == my_team_id:
            buster = self.updatebuster(entity_id, x, y, state, value)
        else:
            self.updateenemy(entity_id, x, y, state, value)

    def getenemybase(self):
        return getbase(1-self.teamid, 1700)

    def chooseterminator(self):
        if self.squadsize < 2: return -1
        enemybase = self.getenemybase()
        myteam = sortdistances(enemybase, self.team.values())
        for pair in myteam:
            dst, buster = pair
            if buster.isstunned: continue
            if buster.carrying != NOTCARRYING: continue
            #todo: what was I doing?
            #todo calculate turns needed to cover the distance to the enemy base, instead of fixed value
            if self.turnsuntilstun(buster) < 3: continue
            return buster.id
        return -1

    def getalltargets(self):
        return [ b.target for b in self.team.values() ]

    def actions(self):
        #ret commands
        terminatorid = self.chooseterminator()
        for t in self.team.values():
            if t.isstunned:
                yield "MOVE 0 0 You'll regret that!"
                continue
            terminator = t.id == terminatorid \
                and self.squadsize > len(self.neutralized) \
                and self.turnsuntilstun(t) < STUN_RECHARGE /2
            log("Current target for " + str(t) + " is " + str(t.target))
            if not t.target:
                if terminator:
                    enemybase = self.getenemybase()
                    t.target = enemybase
                else:
                    if self.ghostmem:
                        ghosts = [ g for g in self.ghostmem.values() if g.stamina <= 2 ]
                        ghostdists = [ (dist(t, g), g,) for g in ghosts]
                        filtered = []
                        for d, g in ghostdists:
                            if d < 20:
                                del self.ghostmem[g.id]
                            else:
                                filtered.append((d,g,))
                        if filtered:
                            ghostdists = filtered
                            ghostdists.sort(key=lambda pair : pair[0])
                            d, g = ghostdists[0]
                            t.target = g
                    if not t.target:
                        consider = self.toexplore[:]
                        centers = {}
                        for cell in consider:
                            centers[cell.center] = cell
                        for targeted in self.getalltargets():
                            if targeted in centers:
                                consider.remove(centers[targeted])
                        tcell = self.grid.closest(t, consider)
                        t.target = tcell.center
                log("New target for " + str(t) + " is " + str(t.target))

            if t.carrying != NOTCARRYING:
                if t.x == self.base.x and t.y == self.base.y:
                    yield "RELEASE I ain't afraid of no ghost!"
                    ghostid = t.target.id
                    if ghostid in self.ghostmem:
                        del self.ghostmem[ghostid]
                    t.target = None
                else:
                    yield "MOVE %d %d"%(self.base.x, self.base.y,)
            else:
                canstun = self.turnsuntilstun(t) < 1
                closeenemies = [ enemy for enemy in self.enemy.values() \
                    if not enemy in self.neutralized \
                    and not enemy.isstunned \
                    and enemy.carrying != NOTCARRYING ]
                e = findshootable(t, closeenemies) if canstun else None
                if e:
                    yield "STUN %d Get lost copycat!"%(e.id,)
                    self.stun_used[t.id] = self.turn
                    t.target = None
                    #todo bring neutralization back
                    #self.neutralized.append(e.id)
                else:
                    g = findshootable(t, self.ghosts) if not terminator else None
                    if g:
                        yield "BUST %d Ghost Busters!"%(g.id,)
                    elif t.x == t.target.x and t.y == t.target.y:
                        log("%d in position, but no target..."%(t.id))
                        yield "MOVE %d %d Who you gonna call?"%(t.target.x, t.target.y,)
                        t.target = None
                    else:
                        yield "MOVE %d %d"%(t.target.x, t.target.y,)
                        
    def dump(self):
        log("----------")
        for r in range(self.grid.h):
            row = ""
            for c in range(self.grid.w):
                if self.grid.data[r][c] in self.toexplore: row += "*"
                else: row += " "
            log(row)

if __name__ == "__main__":
    busters_per_player = int(input())  # the amount of busters you control
    ghost_count = int(input())  # the amount of ghosts on the map
    my_team_id = int(input())  # if this is 0, your base is on the top left of the map, if it is one, on the bottom right

    state = gamestate()
    state.setup(my_team_id, ghost_count, busters_per_player)

    # game loop
    while True:
        entities = int(input())  # the number of busters and ghosts visible to you
        state.start_turn()
        
        for i in range(entities):
            # entity_id: buster id or ghost id
            # y: position of this buster / ghost
            # entity_type: the team id if it is a buster, -1 if it is a ghost.
            # state: For busters: 0=idle, 1=carrying a ghost, 2=stunned
            # value: For busters: Ghost id being carried. For ghosts: number of busters attempting to trap this ghost.
            entity_id, x, y, entity_type, entity_state, value = [int(j) for j in input().split()]
            state.update(entity_id, x, y, entity_type, entity_state, value)
            # state.dump()
                
        for cmd in state.actions():
            print (cmd)

            
            # Write an action using print
            # MOVE x y | BUST id | RELEASE
