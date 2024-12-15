import os.path
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum, auto
from functools import reduce
from statistics import variance

import pygame
from pygame import Vector2
from pygame.colordict import THECOLORS

from animations import Model, Point, Animation


def wrap(value: Point, size: tuple[int, int]):
    xsize, ysize = size
    if value.x in range(xsize) and value.y in range(ysize):
        return value
    x, y = value
    while x >= xsize:
        x -= xsize
    while x < 0:
        x += xsize
    while y >= ysize:
        y -= ysize
    while y < 0:
        y += ysize
    return Point(x, y)


class Quadrant(Enum):
    NW = auto()
    NE = auto()
    SW = auto()
    SE = auto()


@dataclass
class Robot:
    pos: Point
    vel: Point

    def move(self, bounds: Point | tuple[int, int]):
        self.pos += self.vel
        self.pos = wrap(self.pos, bounds)


class BathroomSecurity(Model):
    def __init__(self, robots: str, size=(101, 103)):
        self.robots = list(self.parse_input(robots))
        self.size = Point(*size)
        self.elapsed_time = 0
        self.pause_frames = 0
        self.part1 = self.part2 = 0

    def is_likely_tree(self):
        xs = [robot.pos.x for robot in self.robots]
        ys = [robot.pos.y for robot in self.robots]
        xv = variance(xs)
        yv = variance(ys)

        # if xv < 500:
        #     print(f'X variance at {self.elapsed_time}: {xv}')
        # if yv < 500:
        #     print(f'Y variance at {self.elapsed_time}: {yv}')
        return xv < 500 and yv < 500

    def get_safety_factor(self):
        x_mid = self.size.x // 2
        y_mid = self.size.y // 2
        quadrants = defaultdict(int)
        for robot in self.robots:
            if robot.pos.x < x_mid:
                if robot.pos.y < y_mid:
                    quadrants[Quadrant.NW] += 1
                if robot.pos.y > y_mid:
                    quadrants[Quadrant.SW] += 1
            if robot.pos.x > x_mid:
                if robot.pos.y < y_mid:
                    quadrants[Quadrant.NE] += 1
                if robot.pos.y > y_mid:
                    quadrants[Quadrant.SE] += 1
        return reduce(int.__mul__, quadrants.values(), 1)

    @staticmethod
    def parse_input(robots: str):
        if os.path.exists(robots):
            with open(robots) as f:
                robots = f.read()
        for line in robots.splitlines():
            px, py, vx, vy = map(int, re.findall(r'-?\d+', line))
            yield Robot(Point(px, py), Point(vx, vy))

    def update(self):
        if self.pause_frames:
            self.pause_frames -= 1
            return
        self.elapsed_time += 1
        for robot in self.robots:
            robot.move(self.size)
        if self.elapsed_time == 100:
            self.part1 = self.get_safety_factor()
            self.pause_frames = 120
        if self.is_likely_tree():
            self.part2 = self.elapsed_time
            self.pause_frames = sys.maxsize

    def render(self, surface: pygame.Surface):
        avail_height = surface.get_height()
        num_tiles = self.size.y
        scale = avail_height // num_tiles
        surface.fill(0, (0, 0, self.size.x * scale, self.size.y * scale))
        for robot in self.robots:
            pygame.draw.rect(surface, THECOLORS['forestgreen'], (Vector2(robot.pos) * scale, Vector2(scale, scale)))
        text_pos = Vector2((self.size.x + 1) * scale, scale)
        font = pygame.font.SysFont('Verdana', 16)
        text = font.render(str(self.elapsed_time), True, 0)
        surface.blit(text, text_pos)
        if self.part1:
            surface.blit(font.render(f'Part 1: {self.part1}', True, 0), text_pos + (0, 20))
        if self.part2:
            surface.blit(font.render(f'Part 2: {self.part2}', True, 0), text_pos + (0, 40))

    def print(self):
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                count = sum(1 for r in self.robots if r.pos == (x, y))
                print(count or '.', end='')
            print()



if __name__ == '__main__':
    # Animation('Day 14: Sample').run(BathroomSecurity('../inputs/sample14.txt', size=(11, 7)))
    runner = BathroomSecurity('../inputs/day14.txt')
    animation = Animation('Day 14: Restroom Redoubt', size=(900, 721), fps=240)
    animation.run(runner)
