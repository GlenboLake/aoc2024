from abc import abstractmethod
from typing import NamedTuple

import pygame


class Point(NamedTuple):
    x: int
    y: int

    def __add__(self, other):
        x, y = other
        return Point(self.x + x, self.y + y)

    def __sub__(self, other):
        x, y = other
        return Point(self.x - x, self.y - y)

    def __str__(self):
        return f'({self.x},{self.y})'


class Model:
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self, surface: pygame.Surface):
        pass


def is_quit(event: pygame.event.Event):
    if event.type == pygame.QUIT:
        return True
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return True
    return False


class Animation:
    def __init__(self, caption=None, size=(800, 800), fps=60):
        pygame.init()
        self.window = pygame.display.set_mode(size, flags=pygame.SRCALPHA)
        if caption is not None:
            pygame.display.set_caption(caption)
        pygame.display.set_icon(pygame.image.load('assets/aoc_favicon.png'))
        self.clock = pygame.time.Clock()
        self.model: Model = None  # noqa
        self.fps = fps

    def update(self):
        self.model.update()

    def render(self):
        self.window.fill(0xFFFFFF)
        self.model.render(self.window)

    def run(self, model: Model):
        self.model = model
        running = True
        while running:
            for event in pygame.event.get():
                if is_quit(event):
                    running = False
            self.update()
            self.render()
            pygame.display.update()
            self.clock.tick(self.fps)
        pygame.quit()
