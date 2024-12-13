import os.path
import random
from collections import deque, defaultdict
from enum import Enum, global_enum
from functools import cached_property
from typing import NamedTuple, Collection

import pygame
from pygame import Vector2
from pygame.color import THECOLORS

TILE_SIZE = 0
FPS = 60

BRIGHT_COLORS = [
    color for color_tuple in THECOLORS.values()
    if (color := pygame.Color(color_tuple)).hsva[1] > 80
]

CROP_COLORS = defaultdict(lambda: random.choice(BRIGHT_COLORS))


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        if isinstance(other, Enum):
            other = other.value
        dx, dy = other
        return Point(self.x + dx, self.y + dy)

    def __sub__(self, other):
        if isinstance(other, Enum):
            other = other.value
        dx, dy = other
        return Point(self.x - dx, self.y - dy)

    def neighbors(self):
        yield Point(self.x, self.y + 1)
        yield Point(self.x, self.y - 1)
        yield Point(self.x + 1, self.y)
        yield Point(self.x - 1, self.y)

    def tile_center(self):
        return Vector2((self.x + 0.5) * TILE_SIZE, (self.y + 0.5) * TILE_SIZE)


@global_enum
class Direction(Enum):
    UP = Point(0, -1)
    DOWN = Point(0, 1)
    LEFT = Point(-1, 0)
    RIGHT = Point(1, 0)

    def turn_right(self):
        return Direction(Point(-self.value.y, self.value.x))

    def turn_left(self):
        return Direction(Point(self.value.y, -self.value.x))


class Region:
    def __init__(self, plots: Collection[Point], crop):
        self.plots = plots
        self.crop = crop
        self._boundaries: list[list[Point]] = []

    @property
    def area(self):
        return len(self.plots)

    @property
    def boundaries(self):
        if not self._boundaries:
            # First, just find edges
            edges = set()
            for plot in self.plots:
                # Add boundaries based on where there are not neighboring plots in the region. Order is clockwise around the boundary
                if plot + Direction.UP not in self.plots:
                    # top
                    edges.add((plot, plot + Direction.RIGHT))
                if plot + Direction.RIGHT not in self.plots:
                    # right
                    edges.add((plot + Direction.RIGHT, plot + Direction.RIGHT + Direction.DOWN))
                if plot + Direction.DOWN not in self.plots:
                    # bottom
                    edges.add((plot + Direction.RIGHT + Direction.DOWN, plot + Direction.DOWN))
                if plot + (-1, 0) not in self.plots:
                    # left
                    edges.add((plot + Direction.DOWN, plot))

            # The min is going to be a top-left corner of the boundary; this is a good starting point
            boundaries = []
            current_walk: list | None = None
            travel_dir = None
            while edges or current_walk:
                if current_walk is None:
                    a, b = edges.pop()
                    current_walk = [a, b]
                    travel_dir = Direction(b - a)
                position = current_walk[-1]
                # First see if we can turn right, then straight, then left
                for try_move in (travel_dir.turn_right(), travel_dir, travel_dir.turn_left()):
                    edge = position, position + try_move
                    if edge in edges:
                        travel_dir = try_move
                        current_walk.append(edge[1])
                        edges.remove(edge)
                        break
                else:
                    assert current_walk[0] == current_walk[-1], 'This should be the end of a loop'
                    boundaries.append(current_walk[:-1])
                    current_walk = None
            self._boundaries = boundaries
        return self._boundaries

    @property
    def perimeter(self):
        return sum(map(len, self.boundaries))

    @cached_property
    def num_sides(self):
        corner_count = 0
        for boundary in self.boundaries:
            for i in range(len(boundary)):
                a = boundary[i - 2]
                b = boundary[i - 1]
                c = boundary[i]
                if a - b != b - c:
                    corner_count += 1
        return corner_count

    @property
    def price(self):
        return self.area * self.perimeter

    @property
    def discount_price(self):
        return self.area * self.num_sides

    def render(self, surface):
        global TILE_SIZE
        for plot in self.plots:
            center = plot.tile_center()
            rect = pygame.Rect(center.elementwise() - (TILE_SIZE / 2), (TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(surface, CROP_COLORS[self.crop], rect)
        for boundary in self.boundaries:
            mapped_boundary = [Vector2(p) * TILE_SIZE for p in boundary]
            pygame.draw.polygon(surface, THECOLORS['black'], mapped_boundary, 1)


def find_regions(grid):
    def flood_fill(start_point):
        points = set()
        check = deque([start_point])
        while check:
            p = check.popleft()
            if p in points:
                continue
            points.add(p)
            for neighbor in p.neighbors():
                if neighbor not in grid_dict or neighbor in points:
                    continue
                if grid_dict[neighbor] == grid_dict[p]:
                    check.append(neighbor)

        return points

    regions: list[Region] = []
    seen: set[Point] = set()
    grid_dict = {
        (x, y): value
        for y, line in enumerate(grid)
        for x, value in enumerate(line)
    }
    for y, line in enumerate(grid):
        for x, crop in enumerate(line):
            if Point(x, y) not in seen:
                region = flood_fill(Point(x, y))
                seen.update(region)
                regions.append(Region(region, crop))
    p1_total = p2_total = 0
    for region in regions:
        print(f'"{region.crop}" region '
              f'with area {region.area} '
              f'and perimeter {region.perimeter} '
              f'({region.discount_price // region.area} sides)')
        p1_total += region.price
        p2_total += region.discount_price
    print('Part 1:', p1_total)
    print('Part 2:', p2_total)
    return regions


class Map:
    def __init__(self, filename):
        if os.path.exists(filename):
            with open(filename) as f:
                grid = f.read().splitlines()
        else:
            grid = filename.splitlines()
        self.grid_size = len(grid)
        self.regions: Collection[Region] = find_regions(grid)

    def update(self):
        pass

    def render(self, surface: pygame.surface.Surface):
        global TILE_SIZE
        TILE_SIZE = min(surface.get_size()) / self.grid_size
        for region in self.regions:
            region.render(surface)


def is_quit(event: pygame.event.Event):
    if event.type == pygame.QUIT:
        return True
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return True
    return False


class Animation:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode((800, 800), flags=pygame.SRCALPHA)
        pygame.display.set_caption('Day 12: Garden Groups')
        pygame.display.set_icon(pygame.image.load('assets/aoc_favicon.png'))
        self.clock = pygame.time.Clock()
        self.model: Map = None  # noqa

    def update(self):
        self.model.update()

    def render(self):
        self.window.fill(0xFFFFFF)
        self.model.render(self.window)

    def run(self, model: Map):
        self.model = model
        running = True
        while running:
            for event in pygame.event.get():
                if is_quit(event):
                    running = False
            self.update()
            self.render()
            pygame.display.update()
            self.clock.tick(FPS)

        pygame.quit()


def main(filename):
    model = Map(filename)
    Animation().run(model)


xo_test = '''\
OOOOO
OXOXO
OOOOO
OXOXO
OOOOO'''
if __name__ == '__main__':
    # main(xo_test)
    # main('../inputs/sample12.txt')
    main('../inputs/day12.txt')
