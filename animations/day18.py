import math
import os.path
import sys
from collections import deque, defaultdict
from functools import lru_cache
from itertools import cycle

import pygame

from animations import Point, Model, Animation


@lru_cache
def byte_sprite(tile_size, highlight=False):
    surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
    corner = max(1, tile_size // 10)
    bg_color = (128,128,128,255) if highlight else (0,0,0,255)
    green = 0, 255, 0, 255
    pygame.draw.rect(surface, bg_color, (0, 0, tile_size, tile_size), border_radius=corner)
    pygame.draw.rect(surface, green, (0, 0, tile_size, tile_size), width=1, border_radius=corner)
    pygame.draw.circle(surface, green, (tile_size * .3, tile_size * .4), tile_size / 15)
    pygame.draw.circle(surface, green, (tile_size * .7, tile_size * .4), tile_size / 15)
    pygame.draw.line(surface, green, (tile_size * .25, tile_size * .25), (tile_size * .35, tile_size * .3), 1)
    pygame.draw.line(surface, green, (tile_size * .75, tile_size * .25), (tile_size * .65, tile_size * .3), 1)
    pygame.draw.arc(surface, green, (tile_size * .2, tile_size * .5, tile_size * .6, tile_size * .3), math.pi,
                    2 * math.pi, 1)
    return surface


def parse(incoming_bytes: str):
    if os.path.exists(incoming_bytes):
        with open(incoming_bytes) as f:
            incoming_bytes = f.read()
    for pair in incoming_bytes.splitlines():
        yield Point(*map(int, pair.split(',')))


class Grid(Model):
    def __init__(self, input: str, size: int, init_read=0):
        self.all_points = parse(input)
        self.corruption: set[Point] = set()
        self.last_added: Point = None
        self.size = size
        self.tick_rate = 3  # Tick every n frames
        self.counter = cycle(range(self.tick_rate))
        self.path: list[Point] = []
        self.goal = Point(self.size - 1, self.size - 1)
        self.finished = False
        self.read_points(init_read)
        self.update_path()
        print('Part 1:', len(self.path) - 1)

    def update_path(self):
        seen: set[Point] = set()
        queue = deque([[Point(0, 0)]])
        while queue:
            point, *history = queue.popleft()
            if point in seen:
                continue
            seen.add(point)
            if point == self.goal:
                self.path = [point, *history]
                return
            for diff in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                new_x, new_y = new_point = point + diff
                if 0 <= new_x < self.size and 0 <= new_y < self.size and (new_x, new_y) not in self.corruption:
                    queue.append([new_point, point, *history])
        # No path possible
        self.path = self.flood_fill(Point(0, 0))
        self.finished = True
        print('Part 2:', self.last_added)

    def flood_fill(self, start):
        seen: set[Point] = set()
        queue = deque([start])
        while queue:
            point = queue.popleft()
            if point in seen:
                continue
            seen.add(point)
            queue.extend([
                new_point
                for diff in [(0, 1), (1, 0), (0, -1), (-1, 0)]
                if (
                        (new_point := point + diff) not in self.corruption
                        and 0 <= new_point.x < self.size
                        and 0 <= new_point.y < self.size
                )

            ])
        return list(seen)

    def print_grid(self):
        for y in range(self.size):
            for x in range(self.size):
                print('#' if (x, y) in self.corruption else '.', end='')
            print()

    def read_points(self, n):
        for _ in range(n):
            self.last_added = next(self.all_points)
            self.corruption.add(self.last_added)

    def update(self):
        if self.finished or next(self.counter) > 0:
            return
        if self.path:
            self.read_points(1)
            self.update_path()

    def render(self, surface: pygame.Surface):
        tile_size = surface.get_height() // self.size
        for point in self.path:
            color = (255, 0, 0) if self.finished else (0, 0, 255)
            surface.fill(color, (pygame.Vector2(point).elementwise() * tile_size, (tile_size, tile_size)))
        for i in range(self.size + 1):
            pygame.draw.line(surface, (255, 0, 0, 25), (0, tile_size * i), (tile_size * self.size, tile_size * i), 1)
            pygame.draw.line(surface, (255, 0, 0, 25), (tile_size * i, 0), (tile_size * i, tile_size * self.size), 1)
        for byte in self.corruption:
            blit_pos = pygame.Vector2(byte).elementwise() * tile_size
            surface.blit(byte_sprite(tile_size, highlight=byte==self.last_added), blit_pos)


def solve(filename):
    if 'sample' in filename:
        size = 7
        num_points = 12
    else:
        size = 71
        num_points = 1024
    grid = Grid(filename, size, init_read=num_points)
    Animation(caption='Day 18: RAM Run', fps=240).run(grid)


if __name__ == '__main__':
    solve('../inputs/sample18.txt')
    solve('../inputs/day18.txt')
