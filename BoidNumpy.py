import random
import pygame as py
import math
import numpy as np

''' 
=====================================================
    STATIC VALUES AND FUNCTIONS USED IN THE CASS
=====================================================
'''
# INDEX FOR VALUES
X: int = 0
Y: int = 1


ZERO: np.floating = np.finfo(float).eps

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
    def __init__(self, x: float = 0.0, y: float = 0.0, size: float = AVG_SIZE, matrix: list = None, color: tuple = (255, 0, 0)):
        self.position = np.array([x,y]) + np.array([0.001,0.001])
        self.size = size
        self.color = color

        self.direction = np.array([random.uniform(-MAX_SPEED, MAX_SPEED),
                                   random.uniform(-MAX_SPEED,MAX_SPEED)])
        self.acceleration = np.array([random.uniform(-MAX_SPEED,MAX_SPEED),
                                      random.uniform(-MAX_SPEED,MAX_SPEED)])

        self.Separation = False
        self.Alignment = False
        self.Cohesion = False

        self.matrix = matrix
        # Add to matrix. Refactored code here to avoid extra comparisons later
        if self.matrix is None: return
        i: int = int(self.position[X] // CEL_GAP_X) % CELS_PER_AXIS
        j: int = int(self.position[Y] // CEL_GAP_Y) % CELS_PER_AXIS

        self.matrix[i][j].append(self)
        self.actualI = i; self.actualJ = j

    def __str__(self):
        return f'({self.position[X]:.2f},{self.position[Y]:.2f} | {self.actualJ},{self.actualI})'

    def get_position(self) -> np.ndarray:
        return self.position
    def set_position(self, pos: tuple) -> None:
        self.position[X] = pos[X]; self.position[Y] = pos[Y]
    def get_direction(self) -> np.ndarray:
        return self.direction
    def set_direction(self, dir: tuple) -> None:
        self.direction[X] = dir[X]; self.direction[Y] = dir[Y]

    def switch_separation(self, value: bool = None) -> None:
        self.Separation = not self.Separation if value is None else value
    def switch_alignment(self, value: bool = None) -> None:
        self.Alignment = not self.Alignment if value is None else value
    def switch_cohesion(self, value: bool = None) -> None:
        self.Cohesion = not self.Cohesion if value is None else value
    def draw(self, screen) -> None:
        angle = math.atan2(self.direction[Y], self.direction[X])
        points = [
            # Upper dot
            (float(self.position[X] + self.size * math.cos(angle)),
             float(self.position[Y] + self.size * math.sin(angle))),
            # Left lower dot
            (float(self.position[X] + self.size * math.cos(angle + 2.5 * math.pi / 3)),
             float(self.position[Y] + self.size * math.sin(angle + 2.5 * math.pi / 3))),
            # mid point
            (float(self.position[X]), float(self.position[Y])),
            # Right lower dot
            (float(self.position[X] + self.size * math.cos(angle - 2.5 * math.pi / 3)),
             float(self.position[Y] + self.size * math.sin(angle - 2.5 * math.pi / 3)))
        ]

        py.draw.polygon(screen, self.color, points)

    def add_to_matrix(self):
        if self.matrix is None: return

        i: int = int(self.position[X] // CEL_GAP_X) % CELS_PER_AXIS
        j: int = int(self.position[Y] // CEL_GAP_Y) % CELS_PER_AXIS

        if i == self.actualI and j == self.actualJ: return

        self.matrix[self.actualI][self.actualJ].remove(self)
        self.matrix[i][j].append(self)

        self.actualI = i; self.actualJ = j

    def remove_from_matrix(self):
        self.matrix[self.actualI][self.actualJ].remove(self)

    def update_color(self):
        theta = math.atan2(self.direction[Y], self.direction[X])
        normalizedAngle = (theta + math.pi) / (2 * math.pi)
        color = hsv_a_rgb(normalizedAngle, 1.0, 1.0)

        self.color = tuple(int(c * 255) for c in color)
    def update_size(self):
        self.size = vector_norm(self.direction) * AVG_SIZE / MAX_SPEED + AVG_SIZE
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
            self.position += dir
        else: # Update position and velocity
            self.normalize_direction(deltaTime)
            self.position += self.direction * deltaTime

        # print(f'{self.position[X] = }, {self.position[Y] = }, {self.direction[X] = }, {self.direction[Y]= }')
        self.normalize_position()
        self.update_color()
        self.update_size()
        self.add_to_matrix()

    def normalize_position(self):
        if self.position[X] > SCREEN_WIDTH or self.position[X] < 0: self.position[X] = self.position[X] % SCREEN_WIDTH
        if self.position[Y] > SCREEN_HEIGHT or self.position[Y] < 0: self.position[Y] = self.position[Y] % SCREEN_HEIGHT

    def normalize_direction(self, deltaTime: float = 1) -> None:
        self.direction += self.acceleration
        norm: np.floating = vector_norm(self.direction)
        if norm > MAX_SPEED:
            self.direction *= MAX_SPEED/norm

    def normalize_and_set_acceleration(self, acc: np.ndarray):
        # Limit de acceleration to a max force
        self.acceleration = normalize_acceleration(acc)

    def change_direction(self, angle: float = None) -> None:
        theta = math.radians(angle)
        self.normalize_and_set_acceleration(
            np.array([self.acceleration[X] * np.cos(theta) - self.acceleration[Y] * np.sin(theta),
                      self.acceleration[X] * np.sin(theta) + self.acceleration[Y] * np.cos(theta)]))
    def change_velocity_direction(self, angle: float = None) -> None:
        theta = math.radians(angle)
        self.direction[X] = self.direction[X] * np.cos(theta) - self.direction[Y] * np.sin(theta)
        self.direction[Y] = self.direction[X] * np.sin(theta) + self.direction[Y] * np.cos(theta)

    def boid_movement(self, deltaTime: float) -> None:
        # if all the options are disabled
        if not self.Separation and not self.Alignment and not self.Cohesion:
            self.move(deltaTime=deltaTime)
            return

        '''HACER QUE NO SE TENGAN QUE CREAR CADA ITERACIÓN'''
        avgPosition: np.ndarray = np.array([.0,.0])
        avgDir: np.ndarray = np.array([.0,.0])
        SeparationDir: np.ndarray = np.array([.0,.0])
        count: int = 0

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

                    auxPos: np.ndarray = boid.get_position()
                    if invertLowe0X:
                        auxPos[X] -= SCREEN_WIDTH
                    if invertUpperWX:
                        auxPos[X] += SCREEN_WIDTH
                    if invertLowe0Y:
                        auxPos[Y] -= SCREEN_HEIGHT
                    if invertUpperHY:
                        auxPos[Y] += SCREEN_HEIGHT

                    dist = ZERO
                    if self.Separation:
                        dist: np.floating = distance(boid = self, position = auxPos)
                        if dist > DISTANCE_RADIUS_CHECK: continue

                    # Cohesion: boids move toward the center of mass of their neighbors.
                    if self.Cohesion:
                        avgPosition += auxPos

                    # Separation: boids move away from other boids that are too close.
                    if self.Separation:
                        if dist == 0: dist = ZERO
                        SeparationDir = (self.position - auxPos) * separation_coefficient(dist)

                    # Alignment: boids attempt to match the velocities of their neighbors.
                    if self.Alignment:
                        avgDir += boid.get_direction()

                # End for boids
            # End for j
        # End for i

        acceleration: np.ndarray = np.array([.0,.0])

        if count > 0:
            avgPosition /= count

            if self.Alignment:
                acceleration += normalize_acceleration(avgDir/count)

            if self.Cohesion:
                acceleration += normalize_acceleration(avgPosition - self.position)

            if self.Separation:
                acceleration += normalize_acceleration(SeparationDir/count)

        self.normalize_and_set_acceleration(acceleration)
        # Update pos
        self.move(deltaTime = deltaTime)


''' 
=====================================================
        STATIC FUNCTIONS USED IN THE CASS
        NOT MEANT TO BE IMPORT
=====================================================
'''

def distance(boid: Boid, position: np.ndarray) -> np.floating:
    """
    :return: Euclidean distance between Boid1 and the position
    """
    return np.linalg.norm(boid.get_position() - position)
def normalize_acceleration(acceleration: np.ndarray, force: float = MAX_FORCE) -> np.ndarray:
    """
    :return: Limit de acceleration to a max force
    """
    norm: np.floating = vector_norm(acceleration)
    if norm > force: return acceleration*force/norm
    else:            return acceleration

def vector_norm(vect: np.ndarray) -> np.floating:
    """
    :return: The norm of the vector ||dx,dy||
    """
    return np.linalg.norm(vect)

def separation_coefficient(dist: np.floating) -> np.floating:
    margin: np.floating = np.float32(50)
    res: np.floating = np.float32(0)
    if dist <= margin:
        res = 1/np.log(dist+1)*50000
    return res

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