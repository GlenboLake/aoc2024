import os.path
from collections import defaultdict
from functools import reduce
from itertools import combinations
from random import randint
from typing import Collection

import pygame
from pygame import Vector2

from animations import Model, Animation


class Network(Model):
    def __init__(self):
        self.computers = defaultdict(set)
        self.positions: dict[str, Vector2] = {}

    @property
    def connections(self):
        return {
            tuple(sorted([a, b]))
            for a, bs in self.computers.items()
            for b in bs
        }

    def scatter(self, surface: pygame.Surface):
        for computer in self.computers:
            self.positions[computer] = Vector2(randint(0, surface.get_width()), randint(0, surface.get_height()))

    def update(self):
        if not self.positions:
            return
        forces = {c: Vector2() for c in self.computers}
        for computer, neighbors in self.computers.items():
            for neighbor in neighbors:
                n_force = self.positions[neighbor] - self.positions[computer]
                # Pull toward a length of 50, but don't move faster than 2px
                strength = min(n_force.magnitude() - 50, 2)
                n_force.scale_to_length(strength)
                forces[computer] += n_force
        for computer, force in forces.items():
            self.positions[computer] += force

    def render(self, surface: pygame.Surface):
        if not self.positions:
            self.scatter(surface)
        for a, b in self.connections:
            pygame.draw.line(surface, 0, self.positions[a], self.positions[b])
        for pos in self.positions.values():
            pygame.draw.circle(surface, 0xFF0000, pos, 5)

    def is_clique(self, *computers):
        first, *others = computers
        if not others:
            return True
        if any(other not in self.computers[first] for other in others):
            return False
        return self.is_clique(*others)

    def find_3_cliques(self):
        possible = {comp for comp, connected in self.computers.items() if len(connected) >= 2}
        found = set()
        for c in possible:
            neighbors = self.computers[c]
            for a, b in combinations(neighbors, 2):
                if self.is_clique(a, b, c):
                    found.add(tuple(sorted([a, b, c])))
        return found

    def find_cliques(self, k):
        return set(self.gen_cliques(k))

    def gen_cliques(self, k):
        if k == 1:
            for c in self.computers:
                yield frozenset({c})
            return
        for k1_clique in self.find_cliques(k - 1):
            connected_to_all = reduce(set.intersection, (self.computers[c] for c in k1_clique))
            for connected in connected_to_all:
                yield frozenset({*k1_clique, connected})

    @staticmethod
    def from_connections(connections: str):
        if os.path.exists(connections):
            with open(connections) as f:
                connections = f.read()
        network = Network()
        for connection in connections.splitlines():
            a, b = connection.split('-')
            network.computers[a].add(b)
            network.computers[b].add(a)
        return network


def part1(filename):
    net = Network.from_connections(filename)
    cliques = net.find_3_cliques()
    return len([
        clique for clique in cliques
        if any(comp.startswith('t') for comp in clique)
    ])


def part2(filename):
    net = Network.from_connections(filename)
    size = max(len(v) for v in net.computers.values())
    found: list[Collection[str]]
    while not (found := list(net.find_cliques(size))):
        size -= 1
    assert len(found) == 1
    return ','.join(sorted(found.pop()))


if __name__ == '__main__':
    assert part1('../inputs/sample23.txt') == 7
    print('Part 1:', part1('../inputs/day23.txt'))
    # Animation('Day 23: LAN party').run(net)
    assert part2('../inputs/sample23.txt') == 'co,de,ka,ta'
    print(part2('../inputs/day23.txt'))
