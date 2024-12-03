import pygame
from pygame import K_ESCAPE, Vector2
from pygame.color import THECOLORS

TEXT_SIZE = 24
FPS = 60

DEFAULT_FONT: pygame.font.Font = None  # noqa


class ScreenInt:
    def __init__(self, value: int, pos=Vector2(0, 0)):
        self._value = value
        self.pos = pos
        self.font = DEFAULT_FONT
        self._color = THECOLORS['black']
        self._remake_surface()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self._remake_surface()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value
        self._remake_surface()

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f'<{self}@{self.pos}>'

    @property
    def rect(self):
        rect = self.surf.get_rect()
        return rect.move(*self.pos)

    def _remake_surface(self):
        self.surf = self.font.render(str(self.value), True, self.color)

    def render(self, window):
        window.blit(self.surf, self.pos)


def main(filename):
    global DEFAULT_FONT

    def get_lines():
        nonlocal filename
        with open(filename) as f:
            for line_no, line in enumerate(f, start=1):
                print(f'Report #{line_no}: {line.strip()}')
                yield [int(x) for x in line.split()]

    pygame.init()

    DEFAULT_FONT = pygame.font.SysFont('Verdana', TEXT_SIZE)
    window = pygame.display.set_mode((1024, 768))

    report_pos = Vector2(TEXT_SIZE, TEXT_SIZE)
    diff_pos = Vector2(TEXT_SIZE, TEXT_SIZE * 2.5)
    sum_pos = Vector2(TEXT_SIZE, TEXT_SIZE * 5)

    pygame.display.set_caption('Day 2: Red-Nosed Reports')
    pygame.display.set_icon(pygame.image.load('assets/aoc_favicon.png'))

    clock = pygame.time.Clock()

    report: list[ScreenInt] = []
    diffs: list[ScreenInt] = []
    total = ScreenInt(0, sum_pos)
    report_is_safe = False

    def rendered_texts() -> list[ScreenInt]:
        yield from report
        yield from diffs
        yield total

    def set_current_report(new_report):
        space_width, _ = DEFAULT_FONT.render(' ' * 5, True, THECOLORS['black']).get_size()
        current_x, current_y = report_pos

        def add_item(num):
            nonlocal current_x
            item = ScreenInt(num, Vector2(current_x, current_y))
            current_x += item.rect.width + space_width
            return item

        return [add_item(n) for n in new_report]

    def calc_diffs():
        def make_diff(left, right):
            value = right.value - left.value
            position = (left.rect.right + right.rect.left) / 2
            text = ScreenInt(value, diff_pos.copy())
            text.pos.x = position - text.rect.width / 2
            return text

        return [make_diff(a, b) for a, b in zip(report, report[1:])]

    def color_diffs():
        nonlocal report_is_safe
        values = {diff.value for diff in diffs}
        report_is_safe = values <= {1, 2, 3} or values <= {-1, -2, -3}
        for diff in diffs:
            diff.color = THECOLORS['green'] if report_is_safe else THECOLORS['red']

    def adjust_total():
        nonlocal total
        if report_is_safe:
            total.value += 1

    next_report = pygame.USEREVENT + 1
    make_diffs = pygame.USEREVENT + 2
    check_diffs = pygame.USEREVENT + 3
    add_to_total = pygame.USEREVENT + 4
    reports = get_lines()

    tick_speed = 100
    running = True

    def process_events():
        nonlocal running, report, diffs
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                running = False
            if event.type == next_report:
                # print('next report')
                report = set_current_report(next(reports))
                diffs.clear()
                pygame.time.set_timer(make_diffs, tick_speed, 1)
                pygame.time.set_timer(check_diffs, 2*tick_speed, 1)
                pygame.time.set_timer(add_to_total, 3*tick_speed, 1)
            if event.type == make_diffs:
                # print('diffs')
                diffs = calc_diffs()
            if event.type == check_diffs:
                # print('check')
                color_diffs()
            if event.type == add_to_total:
                # print('add')
                adjust_total()

    def render():
        window.fill(THECOLORS['aliceblue'])
        for text in rendered_texts():
            text.render(window)
        pygame.display.update()

    pygame.event.post(pygame.event.Event(next_report))
    pygame.time.set_timer(next_report, 5*tick_speed)
    while running:
        try:
            process_events()
        except StopIteration:
            pygame.time.set_timer(next_report, 0)
        render()
        clock.tick(FPS)


if __name__ == '__main__':
    # main('../inputs/sample02.txt')
    main('../inputs/day02.txt')
