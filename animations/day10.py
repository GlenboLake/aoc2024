import math
from collections import Counter
from enum import Enum, auto
from itertools import chain
from typing import NamedTuple, Collection

import pygame
from pygame import Vector2
from pygame.color import THECOLORS, Color

TILE_SIZE = 20
FONT_SIZE = 14
FPS = 120
TICK_SIZE = 1

def hsv_color(hsva):
    c = Color(0)
    c.hsva = hsva
    return c


colors = [
    hsv_color((36 * i, 50, 100, 100))
    for i in range(10)
]


class Point(NamedTuple):
    x: int
    y: int

    @property
    def vec(self):
        return Vector2(self)

    def __add__(self, other):
        return Point(int(self.x + other.x), int(self.y + other.y))


def tile_center(p: Point | Vector2):
    v: Vector2 = p.vec if isinstance(p, Point) else p
    tile_top_left = v.elementwise() * TILE_SIZE
    return tile_top_left.elementwise() + (TILE_SIZE / 2)


class Tile:
    def __init__(self, value):
        self.value = value
        self.reachable_by: set[Point] = set()

    def render(self, font: pygame.font.Font):
        surf = pygame.surface.Surface([TILE_SIZE, TILE_SIZE], pygame.SRCALPHA)
        surf.fill(colors[self.value])
        text = font.render(str(self.value), True, (50, 50, 50))
        x = (TILE_SIZE / 2) - (text.get_width() / 2)
        y = (TILE_SIZE / 2) - (text.get_height() / 2)
        surf.blit(text, (x, y))
        return surf

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'<Tile {self.value}>'


class HeightMap:
    def __init__(self, heights):
        self.tiles = {}
        for y, row in enumerate(heights):
            for x, value in enumerate(row):
                p = Point(x, y)
                self.tiles[p] = Tile(value)
                if value == 0:
                    self.tiles[p].reachable_by.add(p)
        self.size = len(heights)
        self.font = pygame.font.SysFont('Verdana', FONT_SIZE)

    @staticmethod
    def from_file(filename):
        with open(filename) as f:
            heights = [
                [int(x) for x in row]
                for row in f.read().splitlines()
            ]
        return HeightMap(heights)

    def render(self):
        surf_size = self.size * TILE_SIZE
        surf = pygame.surface.Surface([surf_size, surf_size], pygame.SRCALPHA)
        for point, tile in self.tiles.items():
            pos = point.vec.elementwise() * TILE_SIZE
            tile = self.tiles[point].render(self.font)
            surf.blit(tile, pos)
        return surf

    def find_path(self, pos: Point):
        target_value = self.tiles[pos].value + 1
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            check = Point(pos.x + dx, pos.y + dy)
            if check not in self.tiles:
                continue
            if self.tiles[check].value == target_value:
                yield check


class Cursor:
    def __init__(self, pos: Vector2, target: Vector2 = None):
        self.pos = pos
        self.target = target

    def __str__(self):
        pass


class TrailState(Enum):
    IDLE = auto()
    DRAWING = auto()
    DRAWN = auto()


class Trail:
    def __init__(self, path: Collection[Point]):
        self.path: Collection[Point] = path
        self.state = TrailState.IDLE


class Puzzle:
    def __init__(self, filename):
        self.height_map = HeightMap.from_file(filename)
        self.scores: dict[Point, int] = {}
        self.trails = [Trail(t) for t in self.pre_solve()]
        print(f'Solution: {len(self.trails)}')
        self.progress = 0

    def answer(self):
        # Not the actual answer, but the number of trails that have been rendered for part 1
        return sum(1 for t in self.trails if t.state == TrailState.DRAWN)

    def pre_solve(self):
        step_dirs = [
            Point(0, 1),
            Point(0, -1),
            Point(1, 0),
            Point(-1, 0),
        ]

        def valid_neighbors(p: Point):
            value = self.height_map.tiles[p].value
            for d in step_dirs:
                dest = p + d
                if dest not in self.height_map.tiles:
                    continue
                if self.height_map.tiles[dest].value == value + 1:
                    yield dest

        valid_steps = {
            p: list(valid_neighbors(p))
            for p in self.height_map.tiles
        }
        trail_heads = {p for p, tile in self.height_map.tiles.items() if tile.value == 0}
        # Sort in reading order for debugging
        trail_heads = sorted(trail_heads, key=lambda p: (p.y, p.x))

        def find_trails(start_point):
            if self.height_map.tiles[start_point].value == 9:
                yield (start_point,)
            for step in valid_steps[start_point]:
                yield from (
                    (start_point, *trail)
                    for trail in find_trails(step)
                )

        trails = chain.from_iterable(
            find_trails(head) for head in trail_heads
        )

        # Part 1: To make them unique, just select one for each start/end pair
        # yield from sorted({
        #                       (trail[0], trail[-1]): trail
        #                       for trail in trails
        #                   }.values())

        # Part 2: Use the whole list
        yield from trails

    def update(self):
        states = Counter(t.state for t in self.trails)
        if TrailState.DRAWING in states:
            if self.progress > 10:
                # Finished drawing this path
                current_path = [t for t in self.trails if t.state == TrailState.DRAWING][0]
                current_path.state = TrailState.DRAWN
            else:
                # Continue drawing this path
                self.progress += TICK_SIZE
        elif set(states) == {TrailState.DRAWN}:
            # All finished!
            pass
        elif TrailState.IDLE in states:
            # Time to start drawing a new path
            new_path = [t for t in self.trails if t.state == TrailState.IDLE][0]
            new_path.state = TrailState.DRAWING
            self.progress = 0
        else:
            # This should not happen.
            raise RuntimeError('HOW?')

    def render(self):
        hm = self.height_map.render()
        # hm = hm.convert_alpha()
        for trail in self.trails:
            if trail.state == TrailState.DRAWN:
                path = [tile_center(point) for point in trail.path]
                pygame.draw.lines(hm, (128, 128, 128, 30), False, path)
            elif trail.state == TrailState.DRAWING:
                num_points = math.ceil(self.progress) + 1  # Progress of 2.5 should draw 3 lines, i.e. 4 points
                frac, _ = math.modf(self.progress)
                path = [tile_center(point) for point in trail.path][:num_points]
                if self.progress + 1 < len(trail.path) and frac > 0:
                    partial_line = (path[-1] - path[-2]) * frac
                    path[-1] = path[-2] + partial_line
                # Final one is a partial line
                if len(path) > 1:
                    pygame.draw.lines(hm, (0, 0, 0, 255), False, path)
        return hm


def is_quit(event: pygame.event.Event):
    if event.type == pygame.QUIT:
        return True
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return True
    return False


class Animation:
    BEGIN = pygame.USEREVENT + 1

    def __init__(self, window_size):
        pygame.init()
        self.window = pygame.display.set_mode(window_size, pygame.SRCALPHA)
        pygame.display.set_caption('Day 10: Hoof It')
        pygame.display.set_icon(pygame.image.load('assets/aoc_favicon.png'))
        self.running = False
        self.paused = False
        self.animation: Puzzle | None = None
        self.clock = pygame.time.Clock()

    def update(self):
        if not self.paused:
            self.animation.update()

    def render(self):
        self.window.fill(THECOLORS['aliceblue'])
        animation_surf = self.animation.render()
        panel_size = self.window.get_height(), self.window.get_height()
        panel = pygame.transform.scale(animation_surf, panel_size)
        self.window.blit(panel, (0, 0))
        # Also render the solution:
        solution_text = f'Part 1: {self.animation.answer()}'
        solution = pygame.font.SysFont('Verdana', 24).render(solution_text, True, 0)
        solution_pos = self.window.get_height() + 10, 10
        self.window.blit(solution, solution_pos)

    def run(self, input_file):
        self.animation = Puzzle(input_file)
        self.running = True
        self.paused = True
        pygame.time.set_timer(self.BEGIN, 1000, 1)
        while self.running:
            for event in pygame.event.get():
                if is_quit(event):
                    self.running = False
                if event.type == self.BEGIN:
                    self.paused = False
            self.update()
            self.render()
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    # Animation((320 + 150, 320)).run('../inputs/sample10.txt')
    Animation((960 + 200, 960)).run('../inputs/day10.txt')
