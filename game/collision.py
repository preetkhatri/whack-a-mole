"""Pure geometry helpers for point and swept-segment hit tests."""

from __future__ import annotations


def point_in_circle(
    px: float,
    py: float,
    cx: float,
    cy: float,
    radius: float,
) -> bool:
    """Return True when (px, py) lies inside or on the circle boundary."""
    dx = px - cx
    dy = py - cy
    return (dx * dx + dy * dy) <= (radius * radius)


def segment_intersects_circle(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    cx: float,
    cy: float,
    radius: float,
) -> bool:
    """Return True when the segment from (x1, y1) to (x2, y2) meets the circle.

    Uses the closest point on the segment to the circle centre, which covers
    endpoint-inside, chord-through, and grazing cases in O(1) time.
    """
    dx = x2 - x1
    dy = y2 - y1
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return point_in_circle(x1, y1, cx, cy, radius)

    # Project circle centre onto the segment, clamped to [0, 1].
    t = ((cx - x1) * dx + (cy - y1) * dy) / length_sq
    t = max(0.0, min(1.0, t))
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    dist_sq = (closest_x - cx) ** 2 + (closest_y - cy) ** 2
    return dist_sq <= radius * radius


def point_or_segment_hits_circle(
    current: tuple[float, float],
    previous: tuple[float, float] | None,
    center: tuple[float, float],
    radius: float,
) -> bool:
    """Hit if the current point is inside the circle or the motion path crosses it."""
    cx, cy = center
    if point_in_circle(current[0], current[1], cx, cy, radius):
        return True
    if previous is None:
        return False
    return segment_intersects_circle(
        previous[0],
        previous[1],
        current[0],
        current[1],
        cx,
        cy,
        radius,
    )
