### simulation of drops and waves
### wave propagation from https://github.com/Alexander3/wave-propagation

from dataclasses import dataclass
import math

scale = 58  # 1m -> 58 cells
size_x = 1 * scale
size_y = 7
damping = 0.99
omega = 3 / (2 * math.pi)

initial_P = 1
vertPos = size_y - 3
horizPos = round(0.5 * scale)
# wallTop = size_y - 3 * scale
# wall_x_pos = 2 * scale
max_pressure = initial_P / 2
min_presure = -initial_P / 2

drop_decay = 30 # frames

@dataclass
class Drop:
    position: list
    startframe: int

class Simulation:
    def __init__(self):
        self.frame = 0
        self.pressure = [[0.0 for x in range(size_x)] for y in range(size_y)]
        # outflow velocities from each cell
        self._velocities = [[[0.0, 0.0, 0.0, 0.0] for x in range(size_x)] for y in range(size_y)]
        # self.pressure[vertPos][horizPos] = initial_P
        # self.drops = [Drop(position=[horizPos, vertPos], startframe=0), Drop(position=[5, 1], startframe=10)]
        self.drops = []

    def cleanup_drops(self):
        drops_to_remove = []
        for drop in self.drops:
            amp = math.exp(-(self.frame - drop.startframe) / drop_decay)
            if amp < 0.05:
                drops_to_remove.append(drop)
        for drop in drops_to_remove:
            self.drops.remove(drop)

    def updateV(self):
        """Recalculate outflow velocities from every cell basing on preassure difference with each neighbour"""
        V = self._velocities
        P = self.pressure
        for i in range(size_y):
            for j in range(size_x):
                # if wall[i][j] == 1:
                #     V[i][j][0] = V[i][j][1] = V[i][j][2] = V[i][j][3] = 0.0
                #     continue
                cell_pressure = P[i][j]
                V[i][j][0] = V[i][j][0] + cell_pressure - P[i - 1][j] if i > 0 else cell_pressure
                V[i][j][1] = V[i][j][1] + cell_pressure - P[i][j + 1] if j < size_x - 1 else cell_pressure
                V[i][j][2] = V[i][j][2] + cell_pressure - P[i + 1][j] if i < size_y - 1 else cell_pressure
                V[i][j][3] = V[i][j][3] + cell_pressure - P[i][j - 1] if j > 0 else cell_pressure

    def updateP(self):
        for i in range(size_y):
            for j in range(size_x):
                self.pressure[i][j] -= 0.5 * damping * sum(self._velocities[i][j])

    def step(self):
        # self.pressure[vertPos][horizPos] = initial_P * math.sin(omega * self.frame)
        # TODO add drops for a limited time - decaying over time
        for drop in self.drops:
            if self.frame < drop.startframe:
                continue
            self.pressure[drop.position[1]][drop.position[0]] = initial_P * math.sin(omega * (self.frame - drop.startframe)) * math.exp(-(self.frame - drop.startframe) / drop_decay)
        self.updateV()
        self.updateP()
        self.cleanup_drops()
        self.frame += 1
