import random
import pygame as py
import math

''' 
=====================================================
    STATIC VALUES AND FUNCTIONS USED IN THE CASS
=====================================================
'''
ZERO: float = 1e-8

SCREEN_WIDTH: int = 1400
SCREEN_HEIGHT: int = 700
CELS_PER_AXIS: int = 35
CEL_GAP_X: int = SCREEN_WIDTH // CELS_PER_AXIS
CEL_GAP_Y: int = SCREEN_HEIGHT // CELS_PER_AXIS

def set_resolution(width: int, height: int):
    global SCREEN_WIDTH, SCREEN_HEIGHT, CEL_GAP_X, CEL_GAP_Y
    SCREEN_WIDTH = width
    SCREEN_HEIGHT = height
    CEL_GAP_X = SCREEN_WIDTH // CELS_PER_AXIS
    CEL_GAP_Y = SCREEN_HEIGHT // CELS_PER_AXIS
    print(f'{SCREEN_HEIGHT = }, {SCREEN_WIDTH = }')
    print(f'{CEL_GAP_X = }, {CEL_GAP_Y = }')


CEL_RADIUS_CHECK: int = 3
DISTANCE_RADIUS_CHECK: int = 100
MAX_FORCE = 1
MAX_SPEED = 200
AVG_SIZE = 6

def set_max_force(v: float):
    global MAX_FORCE
    MAX_FORCE = v
def set_max_speed(v: float):
    global MAX_SPEED
    MAX_SPEED = v

class Boid:
    def __init__(self, x: float = 0, y: float = 0, size: float = AVG_SIZE, matrix: list = None, color: tuple = (255, 0, 0)):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

        self.dx = random.uniform(-MAX_SPEED,MAX_SPEED)
        self.dy = random.uniform(-MAX_SPEED,MAX_SPEED)
        self.ax = random.uniform(-MAX_SPEED,MAX_SPEED)
        self.ay = random.uniform(-MAX_SPEED,MAX_SPEED)

        self.Separation = False
        self.Alignment = False
        self.Cohesion = False

        self.matrix = matrix
        # Add to matrix. Refactored code here to avoid extra comparisons later
        if self.matrix is None: return
        i: int = int(self.x // CEL_GAP_X) % CELS_PER_AXIS
        j: int = int(self.y // CEL_GAP_Y) % CELS_PER_AXIS

        self.matrix[i][j].append(self)
        self.actualI = i; self.actualJ = j

    def __str__(self):
        return f'({self.x:.2f},{self.y:.2f} | {self.actualJ},{self.actualI})'

    def get_position(self) -> tuple:
        return self.x, self.y
    def set_position(self, pos: tuple) -> None:
        self.x = pos[0]; self.y = pos[1]
    def get_direction(self) -> tuple:
        return self.dx, self.dy
    def set_direction(self, dir: tuple) -> None:
        self.dx = dir[0]; self.dy = dir[1]

    def switch_separation(self, value: bool = None) -> None:
        self.Separation = not self.Separation if value is None else value

    def switch_alignment(self, value: bool = None) -> None:
        self.Alignment = not self.Alignment if value is None else value

    def switch_cohesion(self, value: bool = None) -> None:
        self.Cohesion = not self.Cohesion if value is None else value

    def draw(self, screen) -> None:
        angle = math.atan2(self.dy, self.dx)
        points = [
            # Upper dot
            (self.x + self.size * math.cos(angle), self.y + self.size * math.sin(angle)),
            # Left lower dot
            (self.x + self.size * math.cos(angle + 2.5 * math.pi / 3),
             self.y + self.size * math.sin(angle + 2.5 * math.pi / 3)),
            # mid point
            (self.x, self.y),
            # Right lower dot
            (self.x + self.size * math.cos(angle - 2.5 * math.pi / 3),
             self.y + self.size * math.sin(angle - 2.5 * math.pi / 3))
        ]

        py.draw.polygon(screen, self.color, points)

    def add_to_matrix(self):
        if self.matrix is None: return

        i: int = int(self.x // CEL_GAP_X) % CELS_PER_AXIS
        j: int = int(self.y // CEL_GAP_Y) % CELS_PER_AXIS

        if i == self.actualI and j == self.actualJ: return

        self.matrix[self.actualI][self.actualJ].remove(self)
        self.matrix[i][j].append(self)

        self.actualI = i; self.actualJ = j
    def remove_from_matrix(self):
        self.matrix[self.actualI][self.actualJ].remove(self)

    def update_color(self):
        theta = math.atan2(self.dy, self.dx)
        normalizedAngle = (theta + math.pi) / (2 * math.pi)
        color = hsv_a_rgb(normalizedAngle, 1.0, 1.0)

        self.color = tuple(int(c * 255) for c in color)
    def update_size(self):
        self.size = vector_norm(self.dx,self.dy) * AVG_SIZE / MAX_SPEED + AVG_SIZE
    def move_down(self, y: float = None, deltaTime: float = 1) -> None:
        if y is None: y = 10 * deltaTime
        self.move(dir = (0, y))
    def move_up(self, y: float = None, deltaTime: float = 1) -> None:
        if y is None: y = 10 * deltaTime
        self.move(dir = (0,-y))
    def move_right(self, x: float = None, deltaTime: float = 1) -> None:
        if x is None: x = 10 * deltaTime
        self.move(dir = (x, 0))
    def move_left(self, x: float =  None, deltaTime: float = 1) -> None:
        if x is None: x = 10 * deltaTime
        self.move(dir = (-x,0))
    def move(self, dir: tuple = None, deltaTime: float = 1) -> None:
        # Make random changes to direction
        OffsetRange = 2.5
        self.change_velocity_direction(random.uniform(-OffsetRange, OffsetRange))

        if dir is not None:
            self.x += dir[0]; self.y += dir[1]
        else: # Update position and velocity
            self.normalize_direction(deltaTime)
            self.x += self.dx * deltaTime
            self.y += self.dy * deltaTime

        # print(f'{self.x = }, {self.y = }, {self.dx = }, {self.dy= }')
        self.normalize_position()
        self.update_color()
        self.update_size()
        self.add_to_matrix()

    def normalize_position(self):
        if self.x > SCREEN_WIDTH or self.x < 0: self.x = self.x % SCREEN_WIDTH
        if self.y > SCREEN_HEIGHT or self.y < 0: self.y = self.y % SCREEN_HEIGHT

    def normalize_direction(self, deltaTime: float = 1) -> None:
        self.dx += self.ax
        self.dy += self.ay

        norm: float = math.sqrt(self.dx ** 2 + self.dy ** 2)
        if norm > MAX_SPEED:
            self.dx *= MAX_SPEED/norm
            self.dy *= MAX_SPEED/norm
    def normalize_and_set_acceleration(self, ax: float, ay: float):
        # Limit de acceleration to a max force
        self.ax, self.ay = normalize_acceleration(ax,ay)

    def change_direction(self, angle: float = None) -> None:
        theta = math.radians(angle)
        self.normalize_and_set_acceleration(self.ax * math.cos(theta) - self.ay * math.sin(theta),
                                            self.ax * math.sin(theta) + self.ay * math.cos(theta))
    def change_velocity_direction(self, angle: float = None) -> None:
        theta = math.radians(angle)
        self.dx = self.dx * math.cos(theta) - self.dy * math.sin(theta)
        self.dy = self.dx * math.sin(theta) + self.dy * math.cos(theta)

    def boid_movement(self, deltaTime: float) -> None:
        # if all the options are disabled
        if not self.Separation and not self.Alignment and not self.Cohesion:
            self.move(deltaTime=deltaTime)
            return

        avgX: float = 0; avgY: float = 0
        avgDirX: float = 0; avgDirY: float = 0
        SeparationDirX: float = 0; SeparationDirY: float = 0
        count: int = 0
        separationCount: int = 0

        # Values to know if boid is being analyzed throw the other part of the map (out of the edge)
        invertLowe0X: bool = False; invertUpperWX: bool = False
        invertLowe0Y: bool = False; invertUpperHY: bool = False

        for i in range(self.actualI - CEL_RADIUS_CHECK, self.actualI + CEL_RADIUS_CHECK + 1):
            invertLowe0X = i < 0
            invertUpperWX = i >= CELS_PER_AXIS

            i = i % CELS_PER_AXIS
            for j in range(self.actualJ - CEL_RADIUS_CHECK, self.actualJ + CEL_RADIUS_CHECK + 1):
                invertLowe0Y = j < 0
                invertUpperHY = j >= CELS_PER_AXIS

                j = j % CELS_PER_AXIS
                for boid in self.matrix[i][j]:
                    if boid is self: continue
                    count += 1

                    auxX, auxY = boid.get_position()
                    if invertLowe0X:
                        auxX -= SCREEN_WIDTH
                    if invertUpperWX:
                        auxX += SCREEN_WIDTH
                    if invertLowe0Y:
                        auxY -= SCREEN_HEIGHT
                    if invertUpperHY:
                        auxY += SCREEN_HEIGHT

                    dist = 0
                    if self.Separation:
                        dist: float = distance(boid = self, position = (auxX,auxY))
                        if dist > DISTANCE_RADIUS_CHECK: continue

                    # Cohesion: boids move toward the center of mass of their neighbors.
                    if self.Cohesion:
                        avgX += auxX
                        avgY += auxY

                    # Separation: boids move away from other boids that are too close.
                    if self.Separation:
                        if dist == 0: dist = ZERO
                        separationCoefficient: float = separation_coefficient(dist)
                        if separationCoefficient > 0:
                            separationCount += 1
                            SeparationDirX += (self.x-auxX) * separationCoefficient
                            SeparationDirY += (self.y-auxY) * separationCoefficient

                    # Alignment: boids attempt to match the velocities of their neighbors.
                    if self.Alignment:
                        auxX, auxY = boid.get_direction()
                        avgDirX += auxX
                        avgDirY += auxY

                # End for boids
            # End for j
        # End for i

        accelerationX: float = 0
        accelerationY: float = 0

        if count > 0:
            avgX /= count; avgY /= count

            if self.Alignment:
                avgDirX, avgDirY = normalize_acceleration(avgDirX/count,
                                                          avgDirY/count)
                accelerationX += avgDirX
                accelerationY += avgDirY

            if self.Cohesion:
                avgX, avgY = normalize_acceleration(avgX - self.x,
                                                    avgY - self.y)
                accelerationX += avgX
                accelerationY += avgY

            if self.Separation and separationCount > 0:
                SeparationDirX, SeparationDirY = normalize_acceleration(SeparationDirX,
                                                                        SeparationDirY)
                accelerationX += SeparationDirX
                accelerationY += SeparationDirY


        self.normalize_and_set_acceleration(accelerationX,accelerationY)
        # Update pos
        self.move(deltaTime = deltaTime)


''' 
=====================================================
        STATIC FUNCTIONS USED IN THE CASS
        NOT MEANT TO BE IMPORT
=====================================================
'''


def distance(boid: Boid, position: tuple) -> float:
    """
    :return: Euclidean distance between Boid1 and the position
    """
    x1, y1 = boid.get_position()
    x2, y2 = position
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def normalize_acceleration(ax: float, ay: float, force: float = MAX_FORCE) -> tuple[float, float]:
    """
    :return: Limit de acceleration to a max force
    """
    norm: float = vector_norm(ax,ay)
    if norm > force:
        return ax*force/norm, ay*force/norm
    else:
        return ax, ay
def vector_norm(dx: float, dy: float) -> float:
    """
    :return: The norm of the vector ||dx,dy||
    """
    return math.sqrt(dx**2 + dy**2)

def separation_coefficient(dist: float) -> float:
    """
    :return: A value depending on the distance between the two boids
    """
    margin: float = 50
    if dist > margin: return 0
    else:
        aux = math.log(dist + 1)
        if aux == 0: aux = ZERO
        return (1 / aux) * 50000
def hsv_a_rgb(h, s, v) -> tuple:
    """
    :param h: Hue
    :param s: Saturation
    :param v: Value
    :return: (R,G,B)
    """
    i = int(h * 6)
    f = h * 6 - i
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    i = i % 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q