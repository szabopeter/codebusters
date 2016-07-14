from simulator import Simulator, SimulatorParams
from codebusters import gamestate

p0 = gamestate()
p1 = gamestate()
simulator = Simulator(SimulatorParams(3, 10, 0), p0, p1)
simulator.play()

print(simulator.scores)
