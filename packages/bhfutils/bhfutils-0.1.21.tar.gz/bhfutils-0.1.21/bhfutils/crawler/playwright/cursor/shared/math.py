import math
import random
import bezier
import numpy as np
from typing import Tuple, List, Optional


class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return "x: {}, y: {}".format(self.x, self.y)


origin = Vector(0, 0)


def sub(a: Vector, b: Vector) -> Vector:
    return Vector(a.x - b.x, a.y - b.y)


def div(a: Vector, b: float) -> Vector:
    return Vector(a.x / b, a.y / b)


def mult(a: Vector, b: float) -> Vector:
    return Vector(a.x * b, a.y * b)


def add(a: Vector, b: Vector) -> Vector:
    return Vector(a.x + b.x, a.y + b.y)


def direction(a: Vector, b: Vector) -> Vector:
    return sub(b, a)


def perpendicular(a: Vector) -> Vector:
    return Vector(a.y, -1 * a.x)


def magnitude(a: Vector) -> float:
    return math.sqrt(a.x ** 2 + a.y ** 2)


def unit(a: Vector) -> Vector:
    return div(a, magnitude(a))


def set_magnitude(a: Vector, amount: float) -> Vector:
    return mult(unit(a), amount)


def random_vector_online(a: Vector, b: Vector) -> Vector:
    vec = direction(a, b)
    multiplier = random.random()
    return add(a, mult(vec, multiplier))


def random_normal_line(a: Vector, b: Vector, range_: float) -> Tuple[Vector, Vector]:
    randMid = random_vector_online(a, b)
    normalV = set_magnitude(perpendicular(direction(a, randMid)), range_)
    return randMid, normalV


def generate_bezier_anchors(a: Vector, b: Vector, spread: float) -> List[Vector]:
    side = 1 if round(random.random()) == 1 else -1

    def calc() -> Vector:
        randMid, normalV = random_normal_line(a, b, spread)
        choice = mult(normalV, side)
        return random_vector_online(randMid, add(randMid, choice))

    return sorted([calc(), calc()], key=lambda vec: vec.x)


def clamp(target: float, min_: float, max_: float) -> float:
    return min(max_, max(min_, target))


def overshoot(coordinate: Vector, radius: float) -> Vector:
    a = random.random() * 2 * math.pi
    rad = radius * math.sqrt(random.random())
    vector = Vector(rad * math.cos(a), rad * math.sin(a))
    return add(coordinate, vector)


def bezier_curve(
    start: Vector, finish: Vector, override_spread: Optional[float]
) -> bezier.curve.Curve:
    min_ = 2
    max_ = 200
    vec = direction(start, finish)
    length = magnitude(vec)
    spread = clamp(length, min_, max_)
    anchors = generate_bezier_anchors(
        start, finish, override_spread if override_spread is not None else spread
    )
    all_vectors = [start] + anchors + [finish]
    nodes = np.asfortranarray(
        [[el.x, el.y] for el in all_vectors],
    )
    return bezier.curve.Curve.from_nodes(nodes)
