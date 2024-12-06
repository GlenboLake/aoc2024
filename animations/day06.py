import math
from enum import StrEnum, auto

import pygame
from pygame import Vector2
from pygame.color import THECOLORS

TILE_SIZE = Vector2(6, 6)
# TILE_SIZE = Vector2(48, 48)
TILESET = pygame.image.load('assets/Top-Down_Retro_Interior/TopDownHouse_SmallItems.png')
BOX = pygame.Surface((16, 16))
BOX.blit(TILESET, (0, 0), (16 * 7, 16 * 2, 16, 16))

BOX = pygame.transform.scale(BOX, TILE_SIZE)

ARROW = pygame.Surface(TILE_SIZE, pygame.SRCALPHA)
arrowhead_points = [
    # Bottom left
    Vector2(TILE_SIZE.x / 4, TILE_SIZE.y / 2),
    # Top middle
    Vector2(TILE_SIZE.x / 2, TILE_SIZE.y / 8),
    # Bottom right
    Vector2(TILE_SIZE.x * 3 / 4, TILE_SIZE.y / 2),
]
pygame.draw.polygon(ARROW, THECOLORS['darkgreen'], arrowhead_points)
pygame.draw.line(
    ARROW, THECOLORS['darkgreen'],
    Vector2(TILE_SIZE.x / 2, TILE_SIZE.y / 2),
    Vector2(TILE_SIZE.x / 2, TILE_SIZE.y * 7 / 8),
    3
)

clock = pygame.time.Clock()

USER_EVENTS = [
    CHECK := pygame.USEREVENT + 1,
]


class GuardState(StrEnum):
    IDLE = auto()
    TURNING = auto()
    MOVING = auto()


SPEED = 1  # Frame for each movement
PAUSE = 1  # ms to pause after each movement


class Guard:
    def __init__(self, pos: Vector2):
        self.pos = pos
        self.visited = {tuple(map(round, pos))}
        # 0 is up, 90 is left, 180 is down, 270 is right
        self.dir = 0
        # State can be idle, moving with a destination, or turning with an angle
        self.state = GuardState.IDLE, None

    @property
    def movement(self):
        return Vector2(
            -math.sin(math.radians(self.dir)),
            -math.cos(math.radians(self.dir)),
        )

    def update(self):
        match self.state:
            case GuardState.MOVING, target:
                # print(f'moving to {target}')
                self.pos += self.movement.elementwise() / SPEED
                if self.pos == target:
                    self.state = GuardState.IDLE, None
                    pygame.time.set_timer(CHECK, PAUSE, 1)
                    # print('Reached target')
                    self.visited.add(tuple(map(round, target)))
            case GuardState.TURNING, angle:
                # print(f'Turning to {angle}')
                self.dir = (self.dir - 90 / SPEED) % 360
                if self.dir == angle:
                    self.state = GuardState.IDLE, None
                    pygame.time.set_timer(CHECK, PAUSE, 1)
                    # print('Reached angle')

    def render(self):
        surface = pygame.transform.rotate(ARROW, self.dir)
        return surface


class Map:
    def __init__(self, grid: list[str]):
        self.grid_size = (len(grid[0]), len(grid))
        print(f'Loading {self.grid_size[0]}x{self.grid_size} grid')
        self.obstacles = []
        for r, row in enumerate(grid):
            for c, cell in enumerate(row):
                if cell == '#':
                    self.obstacles.append(Vector2(c, r))
                elif cell == '^':
                    self.guard = Guard(Vector2(c, r))

    def __contains__(self, item):
        x, y = map(round, item)
        return 0 <= x < self.grid_size[0] and 0 <= y < self.grid_size[1]

    @staticmethod
    def from_file(filename):
        with open(filename) as f:
            return Map(f.read().rstrip().splitlines())

    def handle_event(self, event):
        if event.type == CHECK:
            # print('Checking')
            if self.guard.pos not in self:
                print('Done!')
                return
            target_position = self.guard.pos + self.guard.movement
            if target_position in self.obstacles:
                print(f"There's something at {target_position}, turning")
                self.guard.state = GuardState.TURNING, (self.guard.dir - 90) % 360
            else:
                # print(f'Moving to {target_position}')
                self.guard.state = GuardState.MOVING, target_position

    def update(self):
        self.guard.update()

    @property
    def visited_cells(self):
        return len({pos for pos in self.guard.visited if pos in self})

    def render(self):
        surface = pygame.Surface(TILE_SIZE.elementwise() * Vector2(self.grid_size) + Vector2(1, 1), pygame.SRCALPHA)
        surface.fill(THECOLORS['beige'])
        num_cols, num_rows = self.grid_size
        for visited in self.guard.visited:
            pygame.draw.rect(surface, (0, 0, 0, 30), pygame.Rect(TILE_SIZE.elementwise() * visited, TILE_SIZE))
        for obstacle in self.obstacles:
            surface.blit(BOX, obstacle.elementwise() * TILE_SIZE)
        for i in range(num_rows + 1):
            y = i * TILE_SIZE[1]
            pygame.draw.line(surface, (0, 0, 0, 128), (0, y), (surface.get_rect().right, y))
        for i in range(num_cols + 1):
            x = i * TILE_SIZE[0]
            pygame.draw.line(surface, (0, 0, 0, 128), (x, 0), (x, surface.get_rect().bottom))
        # Since the guard surface turning changes its size, some math to align it properly is necessary
        guard_surface = self.guard.render()
        guard_center = self.guard.pos.elementwise() * TILE_SIZE + TILE_SIZE.elementwise() / 2
        blit_pos = guard_center.elementwise() - Vector2(guard_surface.get_size()).elementwise() / 2
        surface.blit(guard_surface, blit_pos)
        return surface


def is_quit(event: pygame.event.Event):
    if event.type == pygame.QUIT:
        return True
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        return True
    return False


def main(filename):
    pygame.init()

    window = pygame.display.set_mode((1300, 1040))
    pygame.display.set_caption('Day 6: Guard Gallivant')
    pygame.display.set_icon(pygame.image.load('assets/aoc_favicon.png'))
    map_ = Map.from_file(filename)
    running = True
    pygame.time.set_timer(CHECK, 500, 1)
    font = pygame.font.SysFont('Verdana', 24)
    while running:
        # Check for events
        for event in pygame.event.get():
            if is_quit(event):
                running = False
            if event.type in USER_EVENTS:
                map_.handle_event(event)
        # Update state
        map_.update()
        # Update display
        window.fill(THECOLORS['white'])
        grid = map_.render()
        screen_center = window.get_rect().center
        blit_pos = Vector2(screen_center) - Vector2(grid.get_size()) / 2
        window.blit(grid, blit_pos)
        text_pos = blit_pos + Vector2(grid.get_width()+5, 0)
        window.blit(font.render(f'Visited: {map_.visited_cells}', True, THECOLORS['black']), text_pos)
        pygame.display.update()
        clock.tick(30)
    pygame.quit()


if __name__ == '__main__':
    # main('../inputs/sample06.txt')
    main('../inputs/day06.txt')
