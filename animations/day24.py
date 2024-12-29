from abc import abstractmethod
from collections import Counter
from functools import cached_property
from itertools import cycle
from typing import Type

import pygame
from pygame import Vector2

from animations import Model, Animation


class Gate:
    def __init__(self, a, b, output, network):
        self.a = a
        self.b = b
        self.output = output
        self.network = network
        self.rank = 0

    @abstractmethod
    def op(self):
        pass


class AndGate(Gate):
    def op(self):
        return self.network[self.a].value and self.network[self.b].value

    def __str__(self):
        return f'{self.a} AND {self.b} -> {self.output}'


class OrGate(Gate):
    def op(self):
        return self.network[self.a].value or self.network[self.b].value

    def __str__(self):
        return f'{self.a} OR {self.b} -> {self.output}'


class XorGate(Gate):
    def op(self):
        return self.network[self.a].value ^ self.network[self.b].value

    def __str__(self):
        return f'{self.a} XOR {self.b} -> {self.output}'


class Label:
    def __init__(self, name: str, init_value: bool = None, rank=0):
        self.name = name
        self.value = init_value
        self.rank = rank

    @cached_property
    def font(self):
        return pygame.font.SysFont('Verdana', 12)

    def render(self):
        return self.font.render(self.name, True, 0x0)


class LogicSystem(Model):
    def __init__(self):
        self.labels: dict[str, Label] = {}
        self.gates: list[Gate] = []
        self.timer = cycle(range(5))

    def load(self, filename):
        gates: dict[str, Type[Gate]] = {
            'AND': AndGate,
            'OR': OrGate,
            'XOR': XorGate,
        }
        with open(filename) as f:
            for line in f:
                if ':' in line:
                    label, value = line.split(': ')
                    self.labels[label] = Label(label, init_value=bool(int(value)), rank=1)
                elif '->' in line:
                    in1, op, in2, _, out = line.split()
                    gate_class = gates[op]
                    self.labels.setdefault(in1, Label(in1))
                    self.labels.setdefault(in2, Label(in2))
                    self.labels.setdefault(out, Label(out))
                    self.gates.append(gate_class(in1, in2, out, self.labels))
        while any(gate.rank == 0 for gate in self.gates):
            for gate in self.gates:
                if gate.rank:
                    continue
                inputs = self.labels[gate.a], self.labels[gate.b]
                if all(label.rank for label in inputs):
                    rank = max(label.rank for label in inputs)
                    gate.rank = rank
                    self.labels[gate.output].rank = rank + 1
        return self

    def update(self):
        if next(self.timer) == 0:
            # Pick and update one gate
            solvable_gates = [
                gate for gate in self.gates
                if (
                        self.labels[gate.a].value is not None and
                        self.labels[gate.b].value is not None and
                        self.labels[gate.output].value is None
                )
            ]
            if solvable_gates:
                gate = solvable_gates.pop()
                self.labels[gate.output].value = gate.op()

    @property
    def part1(self):
        z_labels = [label for label in self.labels.values() if label.name.startswith('z')]
        if any(label.value is None for label in z_labels):
            return None
        return sum(
            label.value << int(label.name.lstrip('z0') or '0')
            for label in z_labels
        )

    def render(self, surface: pygame.Surface):
        rects: dict[str, pygame.Rect] = {}
        num_ranks = max(l.rank for l in self.labels.values()) + 1
        h_spacing = surface.get_width() // (num_ranks - 1)
        rank_sizes = Counter(l.rank for l in self.labels.values())
        v_spacing = surface.get_height() // max(rank_sizes.values())
        colors = {
            True: 0x00FF00,
            False: 0xFF0000,
            None: 0xAAAAAA,
        }
        line_colors = {
            True: 0x00FF00,
            False: 0xFF0000,
            None: 0x000000,
        }
        for rank in range(num_ranks):
            label_x = 10 + h_spacing * (rank - 1)
            label: Label
            labels_in_rank = sorted([l for l in self.labels.values() if l.rank == rank], key=lambda l: l.name)
            for i, label in enumerate(labels_in_rank):
                text = label.render()
                pos = Vector2(label_x, v_spacing * i)
                pygame.draw.rect(surface, colors[label.value], (pos, text.get_size()))
                surface.blit(text, pos)
                rects[label.name] = pygame.Rect(pos, text.get_size())
                if label.name.startswith('z') and label.value is not None:
                    value = str(int(label.value))
                    text = label.font.render(value, True, 0)
                    surface.blit(text, pos + Vector2(text.get_width() + 20, 0))
        gate_font = pygame.font.SysFont('Courier', 12)
        for rank in range(num_ranks):
            gate: Gate
            gate_x = 10 + h_spacing * (rank - 0.5)
            for i, gate in enumerate(filter(lambda g: g.rank == rank, self.gates)):
                gate_name = gate.__class__.__name__[:-4].upper()
                text = gate_font.render(gate_name, True, 0x0)
                pos = Vector2(gate_x, v_spacing * i)
                pygame.draw.rect(surface, 0xAAAAAA, (pos, text.get_size()))
                surface.blit(text, pos)
                rect = pygame.Rect(pos, text.get_size())
                pygame.draw.line(surface, line_colors[self.labels[gate.a].value], rects[gate.a].midright, rect.topleft,
                                 2)
                pygame.draw.line(surface, line_colors[self.labels[gate.b].value], rects[gate.b].midright,
                                 rect.bottomleft, 2)
                pygame.draw.line(surface, line_colors[self.labels[gate.output].value], rect.midright,
                                 rects[gate.output].midleft, 2)
        if solution := self.part1:
            text = pygame.font.SysFont('Verdana', 24).render(str(solution), 0, 0x0)
            surface.blit(text, Vector2(surface.get_size()) - Vector2(10,10) - text.get_size())


if __name__ == '__main__':
    system = LogicSystem().load('../inputs/day24.txt')
    Animation('Day 24: Crossed Wires').run(system)
