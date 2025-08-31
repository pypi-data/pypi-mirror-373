"""Geometry module."""

from functools import reduce
from sympy import Abs, Max, Min, atan2, oo, pi
from sympy.core.expr import Expr
from sympy.core.symbol import Symbol
from sympy.geometry.ellipse import Circle, Ellipse
from sympy.geometry.entity import GeometryEntity, GeometrySet
from sympy.geometry.exceptions import GeometryError
from sympy.geometry.line import Line
from sympy.geometry.point import Point
from typing import Any, Callable, Iterable


tau = 2 * pi

type Scalar = Expr | int | float


class Arc(GeometrySet):
    """
    An arc segment on an axis-aligned ellipse.

    Parameters:
    • ellipse: ellipse along whose perimeter the arc lies
    • start: starting angle of the arc in radians
    • length: angular length in radians, where −2π < length < 2π

    If length is 0, the arc degenerates to a single point on the ellipse.
    """

    def __new__(
        cls,
        ellipse: Ellipse,
        start: Scalar,
        length: Scalar,
        **kwargs: Any,
    ):
        if not -tau < length < tau:
            raise GeometryError("restriction: −2π < length < 2π")
        if length == 0:
            a = Symbol("a", real=True)
            return ellipse.arbitrary_point(a).subs(a, start)
        start = start % tau
        return GeometryEntity.__new__(cls, ellipse, start, length, **kwargs)

    @property
    def ellipse(self) -> Ellipse:
        """Ellipse along whose perimeter the arc lies."""
        return self.args[0]

    @property
    def start(self) -> Scalar:
        """Starting angle in radians."""
        return self.args[1]

    @property
    def length(self) -> Scalar:
        """Angular length in radians."""
        return self.args[2]

    @property
    def bounds(self) -> tuple[Scalar, Scalar, Scalar, Scalar]:
        """A tuple representing the bounding rectangle of the arc."""
        start = self.start % tau
        end = start + self.length
        if start > end:
            start, end = end, start
        span = end - start
        angles = [start, end]
        for critical in (0, pi / 2, pi, 3 * pi / 2):
            distance = (critical - start) % tau
            if 0 < float(distance) < float(span):
                angles.append(start + distance)
        t = Symbol("t", real=True)
        point = self.ellipse.arbitrary_point(t)
        points = [point.subs(t, angle) for angle in angles]
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        return (Min(*xs), Min(*ys), Max(*xs), Max(*ys))

    @property
    def points(self) -> tuple[Point, Point]:
        """Start and end points of the arc."""
        start = self.start
        end = self.start + self.length
        a = Symbol("a", real=True)
        point = self.ellipse.arbitrary_point(a)
        return tuple(point.subs(a, angle) for angle in (start, end))

    def arbitrary_point(self, parameter: str = "t") -> Point:
        """Return a parameterized point on the arc."""
        return self.ellipse.arbitrary_point(parameter)

    def encloses(self, o: GeometryEntity) -> bool:
        """Return False, as no arc can enclose another geometric entity."""
        return False

    def intersection(self, o: GeometryEntity) -> list[GeometryEntity]:
        """
        Return the intersection point(s) of the arc with the specified geometric entity.
        """
        start = self.start % tau
        end = self.start + self.length

        def on_arc(point: Point) -> bool:
            angle = ellipse_angle(self.ellipse, point) % tau
            if self.length > 0:
                return float((angle - start) % tau) <= float(self.length)
            else:
                return float((start - angle) % tau) <= float(self.length)

        return [p for p in self.ellipse.intersection(o) if on_arc(p)]

    def reflect(self, line: Line) -> "Arc":
        """
        Reflect the arc across a line.

        Parameters:
        • line: line across which the arc is reflected
        """
        if line.slope == 0:
            start = -self.start % tau
        elif line.slope == oo:
            start = (pi - self.start) % tau
        else:
            raise GeometryError("restriction: line slope ∈ {0, ∞}")
        return Arc(self.ellipse.reflect(line), start, -self.length)

    def rotate(self, angle=0, pt=None) -> "Arc":
        """
        Rotate the arc counterclockwise.

        Parameters:
        • angle: angle of rotation in radians
        • pt: point around which to rotate
        """
        raise NotImplementedError

    def scale(self, x=1, y=1, pt=None) -> "Arc":
        """
        Scale the arc.

        Parameters:
        • x: scaling factor along the x-axis
        • y: scaling factor along the y-axis
        • pt: the point relative to which scaling is performed
        """
        if x == 0 or y == 0:
            raise GeometryError("restrictions: x ≠ 0, y ≠ 0")
        return Arc(
            self.ellipse.scale(x, y, pt),
            self.start if y >= 0 else tau - self.start,
            self.length if y >= 0 else -self.length,
        )

    def translate(self, x: Scalar = 0, y: Scalar = 0) -> "Arc":
        """
        Shift the arc.

        Parameters:
        • x: translation along the x-axis
        • y: translation along the y-axis
        """
        return Arc(self.ellipse.translate(x, y), self.start, self.length)


def _absify(entity: GeometryEntity) -> GeometryEntity:
    """Override radii negating behavior of SymPy reflect and scale."""
    match entity:
        case Arc():
            return Arc(_absify(entity.ellipse), entity.start, entity.length)
        case Circle():
            return Circle(entity.center, Abs(entity.radius))
        case Ellipse():
            return Ellipse(entity.center, Abs(entity.hradius), Abs(entity.vradius))
    return entity


class Transformer:
    """
    Defines a sequence of geometric transformations to apply to geometric entities.
    Transformations are applied in the order they are added.
    """

    def __init__(self):
        self._transforms: list[Callable[[GeometryEntity], GeometryEntity]] = []

    def rotate(self, angle: Scalar, pt: Point | None = None) -> None:
        """
        Add a rotation to the transformation sequence.

        Parameters:
        • angle: angle of rotation in radians
        • pt: point around which to rotate
        """
        self._transforms.append(lambda e: e.rotate(angle, pt=pt))

    def translate(self, x: Scalar = 0, y: Scalar = 0) -> None:
        """
        Add a translation to the transformation sequence.

        Parameters:
        • x: translation along the x-axis
        • y: translation along the y-axis
        """
        self._transforms.append(lambda e: e.translate(x, y))

    def scale(self, x: Scalar = 1, y: Scalar = 1, pt: Point | None = None) -> None:
        """
        Add scaling to the transformation sequence.

        Parameters:
        • x: scaling factor along the x-axis
        • y: scalaing factor along the y-axis
        • pt: the point relative to which scaling is performed
        """
        self._transforms.append(lambda e: _absify(e.scale(x, y, pt=pt)))

    def reflect(self, line: Line) -> None:
        """
        Add a reflection to the transformation sequence.

        Parameters:
        • line: line across which an entity is reflected
        """
        self._transforms.append(lambda e: _absify(e.reflect(line)))

    def apply(self, entity: GeometryEntity) -> GeometryEntity:
        """
        Apply the transformation sequence to the given geometric entity.

        Parameters:
        • entity: geometric entity to transform
        """
        return reduce(lambda e, f: f(e), self._transforms, entity)


def closest_entity(point: Point, entities: Iterable[GeometryEntity]) -> GeometryEntity | None:
    """
    Return the entity with the smallest Euclidean distance from a specified point.

    Parameters:
    • point: point to which distance is computed
    • entities: entities to compare distances from the point
    """
    result = None
    for entity in entities:
        distance = point.distance(entity)
        if not result or distance < result[1]:
            result = (entity, distance)
    if result:
        return result[0]


def closest_point(entity: GeometryEntity, points: Iterable[Point]) -> Point | None:
    """
    Return the point with the smallest Euclidean distance from a specified entity.

    Parameters:
    • entity: geometric entity to which distance is computed
    • points: points to compare distances from the entity
    """
    result = None
    for point in points:
        distance = point.distance(entity)
        if not result or distance < result[1]:
            result = (point, distance)
    if result:
        return result[0]


def ellipse_angle(ellipse: Ellipse, point: Point) -> Scalar:
    """
    Return the angle of a point, relative to the center of an axis-aligned ellipse.

    Parameters:
    • ellipse: the ellipse whose center is the reference for the angle
    • point: the point whose angle relative to the ellipse center is to be calculated
    """
    return (
        atan2(
            (point.y - ellipse.center.y) / ellipse.vradius,
            (point.x - ellipse.center.x) / ellipse.hradius,
        )
        % tau
    )
