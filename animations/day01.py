import pygame
from pygame import Vector2
from pygame.color import THECOLORS

ITEM_HEIGHT = 30
X_SCALE = 5

LIST_REGISTRY = set()
FPS = 60


class ListItem:
    MAX_VELOCITY = 7.5

    def __init__(self, value, pos: Vector2):
        self.value = value
        self.position = pos
        self.target_position = pos.copy()
        LIST_REGISTRY.add(self)

    def __str__(self):
        if self.moving:
            return f'<{self.value}@{self.position} to {self.target_position}>'
        else:
            return f'<{self.value}@{self.position}>'

    @property
    def moving(self):
        return self.position != self.target_position

    def update(self):
        if not self.moving:
            return
        move_vec = self.target_position - self.position
        speed = pygame.math.clamp(move_vec.magnitude(), 0, self.MAX_VELOCITY)
        scale = speed / move_vec.magnitude()
        self.position += move_vec * scale

    def render(self, window: pygame.Surface, font: pygame.font.Font):
        text = font.render(str(self.value), True, THECOLORS['black'])
        window.blit(text, self.position)


def sort_list(items: list[ListItem]):
    # print('SORTING!')
    positions = [item.position.copy() for item in items]
    items.sort(key=lambda i: i.value)
    for item, target in zip(items, positions):
        item.target_position = target
        # print(f'{item} moving to {item.target_position}')


def read_input(filename):
    with open(filename) as f:
        pairs = (map(int, line.split()) for line in f.read().splitlines())
        left, right = zip(*pairs)

        return left, right


def main(filename):
    pygame.init()

    font = pygame.font.SysFont('Verdana', ITEM_HEIGHT - 2)
    window = pygame.display.set_mode((1024, 768))

    pygame.display.set_caption('Day 1: Historian Hysteria')
    pygame.display.set_icon(pygame.image.load('assets/aoc_favicon.png'))

    clock = pygame.time.Clock()
    running = True

    PROCEED = pygame.USEREVENT + 1
    WAIT_FOR_MOVEMENT_STOP = pygame.USEREVENT + 2

    left_values, right_values = read_input(filename)
    left: list[ListItem] = [
        ListItem(value, Vector2(2 * ITEM_HEIGHT, i * ITEM_HEIGHT))
        for i, value in enumerate(left_values, start=1)
    ]
    right: list[ListItem] = [
        ListItem(value, Vector2(10 * ITEM_HEIGHT, i * ITEM_HEIGHT))
        for i, value in enumerate(right_values, start=1)
    ]
    diffs: list[ListItem] = []
    static: list[ListItem] = []

    # Animation functions
    def all_items_still():
        return all(
            not item.moving
            for item in left + right + diffs
        )

    def sort_lists():
        sort_list(left)
        sort_list(right)

    def calc_diffs():
        for a, b in zip(left, right):
            d = abs(a.value - b.value)
            minus_pos = (a.position + b.position).elementwise() / 2
            minus = ListItem('-', minus_pos)
            equals_pos = b.position + Vector2(2 * ITEM_HEIGHT, 0)
            equals = ListItem('=', equals_pos)
            diff_pos = equals_pos + Vector2(2 * ITEM_HEIGHT, 0)
            diff = ListItem(d, diff_pos)
            # To force movement that triggers the next step... This part could be handled better
            diff.position.x -= 1
            static.extend([minus, equals])
            diffs.append(diff)

    def sum_diffs():
        solution = sum(d.value for d in diffs)
        bottom = max((d.position for d in diffs), key=lambda pos: pos.y)

        solution_position = bottom + Vector2(0, 2*ITEM_HEIGHT)
        static.append(ListItem(solution, solution_position))

    animation_steps = iter([
        # Sort lists
        sort_lists,
        calc_diffs,
        sum_diffs,
    ])

    def process_input():
        nonlocal running, PROCEED, WAIT_FOR_MOVEMENT_STOP
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    running = False
                    break
            if event.type == pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_ESCAPE:
                            running = False
                            break
            if event.type == PROCEED:
                    try:
                        next(animation_steps)()
                        pygame.time.set_timer(WAIT_FOR_MOVEMENT_STOP, 100)
                    except StopIteration:
                        pygame.time.set_timer(pygame.QUIT, 2000)
            if event.type == WAIT_FOR_MOVEMENT_STOP:
                    if all_items_still():
                        pygame.time.set_timer(WAIT_FOR_MOVEMENT_STOP, 0)
                        pygame.time.set_timer(PROCEED, 500, loops=1)


    def update():
        for item in left + right + diffs:
            item.update()

    def render():
        nonlocal left, right
        window.fill(THECOLORS['white'])
        for item in left + right + diffs + static:
            item.render(window, font)
        pygame.display.update()

    # Main loop
    pygame.time.set_timer(PROCEED, 500, loops=1)
    while running:
        process_input()
        update()
        render()
        clock.tick(FPS)


if __name__ == '__main__':
    main('../inputs/sample01.txt')
    # main('../inputs/day01.txt')
