import math
import os.path
import sys
from collections import deque, defaultdict
from functools import lru_cache
from itertools import cycle

import pygame

from animations import Point, Model, Animation


@lru_cache
def byte_sprite(tile_size):
    surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    corner = tile_size // 10
    green = 0, 255, 0, 255
    pygame.draw.rect(surface, (0, 0, 0, 255), (0, 0, tile_size, tile_size), border_radius=corner)
    pygame.draw.rect(surface, green, (0, 0, tile_size, tile_size), width=5, border_radius=corner)
    pygame.draw.circle(surface, green, (tile_size * .3, tile_size * .4), tile_size / 15)
    pygame.draw.circle(surface, green, (tile_size * .7, tile_size * .4), tile_size / 15)
    pygame.draw.line(surface, green, (tile_size * .25, tile_size * .25), (tile_size * .35, tile_size * .3), 2)
    pygame.draw.line(surface, green, (tile_size * .75, tile_size * .25), (tile_size * .65, tile_size * .3), 2)
    pygame.draw.arc(surface, green, (tile_size * .2, tile_size * .5, tile_size * .6, tile_size * .3), math.pi,
                    2 * math.pi, 2)
    return surface


def parse(incoming_bytes: str):
    if os.path.exists(incoming_bytes):
        with open(incoming_bytes) as f:
            incoming_bytes = f.read()
    for pair in incoming_bytes.splitlines():
        yield Point(*map(int, pair.split(',')))


class Grid(Model):
    def __init__(self, input: str, size: int):
        self.all_points = parse(input)
        self.corruption: set[Point] = set()
        self.size = size
        self.tick_rate = 2  # Tick every n frames
        self.counter = cycle(range(self.tick_rate))
        # BFS stuff
        self.dead_ends: set[Point] = set()
        self.step_history: dict[Point, set[Point] | None] = defaultdict(set)
        self.search_history: dict[Point, int] = {}
        self.queue = deque()
        self.goal = Point(self.size - 1, self.size - 1)
        self.finished = False

    def on_path(self, point):
        if point == self.goal:
            return True
        if point in self.dead_ends:
            return False
        reached = self.step_history[point]
        if reached is None:
            result = False
        elif len(reached) == 0:  # Empty set means it's probably on the queue
            result = True
        else:
            result = any(self.on_path(p) for p in reached)
        if not result:
            self.dead_ends.add(point)
        return result

    def print_grid(self):
        for y in range(self.size):
            for x in range(self.size):
                print('#' if (x, y) in self.corruption else '.', end='')
            print()

    def tick_bfs(self):
        if not self.finished and self.goal in self.search_history:
            self.finished = True
            print('Part 1:', self.search_history[self.goal])
        if self.queue:
            point, score = self.queue.popleft()
            dead_end = True
            for diff in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
                new_x, new_y = new_point = point + diff
                if 0 <= new_x < self.size and 0 <= new_y < self.size and (new_x, new_y) not in self.corruption:
                    new_score = score + 1
                    if self.search_history.get(new_point, sys.maxsize) > new_score:
                        dead_end = False
                        self.queue.append((new_point, new_score))
                        self.search_history[new_point] = new_score
                        self.step_history[point].add(new_point)
            if dead_end:
                self.step_history[point] = None

        elif not self.search_history:
            # We haven't even started.
            self.search_history[Point(0, 0)] = 0
            self.queue.append((Point(0, 0), 0))

    def read_points(self, n):
        for _ in range(n):
            self.corruption.add(next(self.all_points))

    def update(self):
        if next(self.counter) > 0:
            return
        if not self.finished:
            self.tick_bfs()

    def render(self, surface: pygame.Surface):
        tile_size = surface.get_height() // self.size
        for point in self.search_history:
            color = (0, 0, 255) if self.on_path(point) else (255, 0, 0)
            surface.fill(color, (pygame.Vector2(point).elementwise() * tile_size, (tile_size, tile_size)))
        for i in range(self.size + 1):
            pygame.draw.line(surface, (255, 0, 0, 25), (0, tile_size * i), (tile_size * self.size, tile_size * i), 3)
            pygame.draw.line(surface, (255, 0, 0, 25), (tile_size * i, 0), (tile_size * i, tile_size * self.size), 3)
        for byte in self.corruption:
            blit_pos = pygame.Vector2(byte).elementwise() * tile_size
            surface.blit(byte_sprite(tile_size), blit_pos)


def part1(filename):
    if 'sample' in filename:
        size = 7
        num_points = 12
    else:
        size = 71
        num_points = 1024
    grid = Grid(filename, size)
    grid.read_points(num_points)
    grid.print_grid()
    Animation(caption='Day 18: RAM Run').run(grid)


if __name__ == '__main__':
    part1('../inputs/sample18.txt')
    part1('../inputs/day18.txt')
