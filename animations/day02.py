from typing import Literal

import pygame
from pygame import K_ESCAPE, Vector2
from pygame.color import THECOLORS

TEXT_SIZE = 24
FPS = 60
TICK_SPEED = 300

DEFAULT_FONT: pygame.font.Font = None  # noqa


class Report:
    GRAPH_WIDTH = 300

    def __init__(self, nums):
        self.nums = nums

    def check_valid(self, part: Literal[1, 2]) -> tuple[bool, int | None]:
        def check_levels(levels):
            diffs = {a - b for a, b in zip(self.nums, self.nums[1:])}
            if diffs <= {1, 2, 3} or diffs <= {-1, -2, -3}:
                return True

        if check_levels(self.nums):
            return True, None
        elif part == 2:
            for i in range(len(self.nums)):
                if check_levels(self.nums[:i] + self.nums[i + 1:]):
                    return True, i
        return False, None

    def render(self, surface: pygame.Surface, pos: Vector2):
        top = pos.y
        bottom = pos.y + TEXT_SIZE * 3
        max_value = max(self.nums)
        spacing = self.GRAPH_WIDTH / len(self.nums)

        def value_to_coord(value):
            # 0 should map to "bottom" and the max value should map to "top"
            # y = ax+b
            a = (top - bottom) / max_value
            b = bottom
            return a * value + b

        points = [
            Vector2(pos.x + x * spacing, value_to_coord(y))
            for x, y in enumerate(self.nums)
        ]
        left = points[0].x
        right = points[-1].x
        points.extend([
            Vector2(right, bottom),
            Vector2(left, bottom)
        ])
        pygame.draw.polygon(surface, THECOLORS['cadetblue'], points)

        # Get the trend in a lazy way
        ups = downs = 0
        for a,b in zip(self.nums, self.nums[1:]):
            if a<b:
                ups += 1
            elif a>b:
                downs += 1
        trend = 1 if ups >= downs else -1
        for left_point, left_value, right_point, right_value in zip(points, self.nums, points[1:], self.nums[1:]):
            slope = right_value - left_value
            color = THECOLORS['black'] if 1 <= abs(slope) <= 3 else THECOLORS['red']
            if slope * trend < 0:
                color = THECOLORS['red']
            pygame.draw.line(surface, color, left_point, right_point, width=2)


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

    report_pos = Vector2(TEXT_SIZE, TEXT_SIZE*5)
    diff_pos = Vector2(TEXT_SIZE, TEXT_SIZE * 6.5)
    sum_pos = Vector2(TEXT_SIZE, TEXT_SIZE * 9)

    pygame.display.set_caption('Day 2: Red-Nosed Reports')
    pygame.display.set_icon(pygame.image.load('assets/aoc_favicon.png'))

    clock = pygame.time.Clock()

    rendered_report: Report
    report: list[ScreenInt] = []
    diffs: list[ScreenInt] = []
    total = ScreenInt(0, sum_pos)
    report_is_safe = False

    def rendered_texts() -> list[ScreenInt]:
        yield from report
        yield from diffs
        yield total

    def set_current_report(new_report):
        nonlocal rendered_report
        space_width, _ = DEFAULT_FONT.render(' ' * 5, True, THECOLORS['black']).get_size()
        current_x, current_y = report_pos

        def add_item(num):
            nonlocal current_x
            item = ScreenInt(num, Vector2(current_x, current_y))
            current_x += item.rect.width + space_width
            return item

        rendered_report = Report(new_report)
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
                pygame.time.set_timer(make_diffs, TICK_SPEED, 1)
                pygame.time.set_timer(check_diffs, 2 * TICK_SPEED, 1)
                pygame.time.set_timer(add_to_total, 3 * TICK_SPEED, 1)
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
        rendered_report.render(window, Vector2(TEXT_SIZE, TEXT_SIZE))
        for text in rendered_texts():
            text.render(window)
        pygame.display.update()

    pygame.event.post(pygame.event.Event(next_report))
    pygame.time.set_timer(next_report, 5 * TICK_SPEED)
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
