import os.path
from itertools import cycle, count

import pygame
from pygame import Vector2

from animations import Animation, Model, Point

FPS = 200
TICK_SPEED = 1
TILE_SIZE = 16

BACKGROUND = pygame.image.load('assets/Top-Down_Retro_Interior/TopDownHouse_FloorsAndWalls.png')
TILESET = pygame.image.load('assets/Top-Down_Retro_Interior/TopDownHouse_SmallItems.png')
SMALL_BOX = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
SMALL_BOX.blit(TILESET, (0, 0), (TILE_SIZE * 6, TILE_SIZE * 2, TILE_SIZE, TILE_SIZE))
STRETCHED_BOX = pygame.transform.scale(SMALL_BOX, (2 * TILE_SIZE, TILE_SIZE))
BIG_BOX = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
BIG_BOX.blit(TILESET, (0, 0), (TILE_SIZE * 7, TILE_SIZE * 2, TILE_SIZE, TILE_SIZE))
ROBOT = pygame.Surface((TILE_SIZE * 4, TILE_SIZE), pygame.SRCALPHA)
ROBOT.blit(pygame.image.load('assets/FloatingRobot.png'), (0, 0))


actor_id = count()

class Actor:
    def __init__(self, pos: Point, sprite: pygame.Surface = None):
        self._id = next(actor_id)
        self.pos = pos
        self._sprite = sprite

    def __hash__(self):
        return self._id

    def __repr__(self):
        return f'<{self.__class__.__name__} at {self.pos}>'

    @property
    def rect(self):
        return pygame.rect.Rect(Vector2(self.pos).elementwise() * TILE_SIZE, (TILE_SIZE, TILE_SIZE))

    @property
    def sprite(self):
        return self._sprite

    @property
    def gps(self):
        return 100 * self.pos.y + self.pos.x

    def move(self, direction):
        self.pos += direction

    def check_move(self, direction, others):
        """
        :type direction: Point
        :type others: list[Actor]
        """
        new_pos = self.rect.move(direction)
        result = {self}
        collided = [
            o for o in others
            if o is not self and new_pos.colliderect(o.rect)
        ]
        for c in collided:
            cascade = c.check_move(direction, others)
            if not cascade:
                return []
            result.update(cascade)
        unique = {id(obj) for obj in result}
        assert len(result) == len(unique)
        return result

    def render(self, surface):
        surface.blit(self.sprite, Vector2(self.pos) * TILE_SIZE)


class Robot(Actor):
    def __init__(self, pos):
        self.sprite_sheet = ROBOT
        self.sprite_index = 0
        self.animation_speed = FPS // 8
        self.counter = cycle(range(self.animation_speed))
        super().__init__(pos, sprite=ROBOT)

    @property
    def sprite(self):
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.blit(self.sprite_sheet, (0, 0), (TILE_SIZE * self.sprite_index, 0, TILE_SIZE, TILE_SIZE))
        return surf

    def render(self, surface):
        if next(self.counter) == 0:
            self.sprite_index = (self.sprite_index + 1) % 4
        super().render(surface)


class Box(Actor):
    sprite = SMALL_BOX

    def __init__(self, pos):
        super().__init__(pos)


class WideBox(Box):
    sprite = STRETCHED_BOX

    def __init__(self, pos):
        super().__init__(pos)

    @property
    def rect(self):
        return pygame.rect.Rect(Vector2(self.pos).elementwise() * TILE_SIZE, (TILE_SIZE * 2, TILE_SIZE))


class Wall(Actor):
    def __init__(self, pos):
        super().__init__(pos, sprite=BIG_BOX)

    def check_move(self, direction, others):
        return []


def parse(filename, expand):
    if os.path.exists(filename):
        with open(filename) as f:
            content = f.read()
    else:
        content = filename

    grid, path = content.split('\n\n')
    actors = []
    for y, row in enumerate(grid.splitlines()):
        for x, ch in enumerate(row):
            if expand:
                x *= 2
            if ch == '#':
                if expand:
                    actors.extend([Wall(Point(x, y)), Wall(Point(x + 1, y))])
                else:
                    actors.append(Wall(Point(x, y)))
            elif ch == 'O':
                if expand:
                    actors.append(WideBox(Point(x, y)))
                else:
                    actors.append(Box(Point(x, y)))
            elif ch == '@':
                actors.append(Robot(Point(x, y)))

    return actors, path.rstrip()


move_dir = {
    '^': Point(0, -1),
    'v': Point(0, 1),
    '<': Point(-1, 0),
    '>': Point(1, 0),
}


class Warehouse(Model):
    def __init__(self, objects, path):
        self.objects = objects
        self.path = path
        self.robot = [o for o in self.objects if isinstance(o, Robot)].pop()
        self.movements = [ch for ch in self.path if ch in move_dir]
        self.progress = -1
        self.background = pygame.Surface((1600, 800), pygame.SRCALPHA)
        bg_tile_width = 62
        bg_tile_height = 31
        background_area = (17, 81, bg_tile_width, bg_tile_height)
        for x in range(0, self.background.get_width(), bg_tile_width):
            for y in range(0, self.background.get_height(), bg_tile_height):
                self.background.blit(BACKGROUND, (x, y), background_area)
        self.animation_speed = TICK_SPEED
        self.counter = cycle(range(self.animation_speed))
        self.finished = False

    def update(self):
        if next(self.counter) != 0:
            return
        if not self.finished:
            try:
                self.progress += 1
                movement = self.movements[self.progress]
                print(self.progress)
                delta = move_dir[movement]
                moving = self.robot.check_move(delta, self.objects)
                for actor in moving:
                    actor.move(delta)
            except IndexError:
                gps = sum(obj.gps for obj in self.objects if isinstance(obj, Box))
                self.finished = True
                print(f'Finished! Total GPS: {gps}')

    def render(self, surface: pygame.Surface):
        surface.blit(self.background, (0, 0))
        for obj in self.objects:
            obj.render(surface)
        progress_font = pygame.font.SysFont('Verdana', 36)
        progress = self.progress * 100 / len(self.movements)
        surface.blit(
            progress_font.render(f'{progress:.2f}%', True, (0, 0, 0, 20)),
            (5, 5)
        )


def run(filename, expand=False):
    objects, path = parse(filename, expand=expand)
    model = Warehouse(objects, path)
    size = (1600, 800) if expand else (800, 800)
    Animation('Day 15: Warehouse Woes', size=size, fps=FPS).run(model)


small_sample = '''\
########
#..O.O.#
##@.O..#
#...O..#
#.#.O..#
#...O..#
#......#
########

<^^>>>vv<v>>v<<'''

if __name__ == '__main__':
    # run(small_sample)
    # run('../inputs/sample15.txt', expand=True)
    run('../inputs/day15.txt', expand=True)
