import os.path
import re
from itertools import batched

op_name = ['adv', 'bxl', 'bst', 'jnz', 'bxc', 'out', 'bdv', 'cdv']


def translate_program(program: list[int]):
    combos = ['adv', 'bst', 'out', 'bdv', 'cdv']
    for opcode, operand in batched(program, 2):
        op = op_name[opcode]
        if op in combos:
            if operand > 3:
                operand = {
                    4: 'a',
                    5: 'b',
                    6: 'c',
                }[operand]
        elif op == 'jnz':
            operand = ''
        print(f'{op} {operand}')


class Computer:
    def __init__(self, input: str):
        if os.path.exists(input):
            with open(input) as f:
                input = f.read()
        self.a, self.b, self.c, *self.ops = (int(match) for match in re.findall(r'\d+', input))
        self.instruction_pointer = 0
        self.halted = True
        self.output = []

    def parse_combo_op(self):
        value = self.ops[self.instruction_pointer + 1]
        return [0, 1, 2, 3, self.a, self.b, self.c][value]

    def run_next_instruction(self):
        op = op_name[self.ops[self.instruction_pointer]]
        if op == 'adv':  # Divide register A by combo op
            self.a = self.a // (2 ** self.parse_combo_op())
            self.instruction_pointer += 2
        elif op == 'bdv':  # Divide register B by combo op
            self.b = self.a // (2 ** self.parse_combo_op())
            self.instruction_pointer += 2
        elif op == 'cdv':  # Divide register C by combo op
            self.c = self.a // (2 ** self.parse_combo_op())
            self.instruction_pointer += 2
        elif op == 'bxl':  # Bitwise XOR of register B and literal
            self.b ^= self.ops[self.instruction_pointer + 1]
            self.instruction_pointer += 2
        elif op == 'bst':  # Store combo op in register B
            self.b = self.parse_combo_op() % 8
            self.instruction_pointer += 2
        elif op == 'jnz':  # Jump if A not zero
            if self.a != 0:
                self.instruction_pointer = self.ops[self.instruction_pointer + 1]
            else:
                self.instruction_pointer += 2
        elif op == 'bxc':  # Bitwise XOR of registers B and C, stored in B
            self.b = self.b ^ self.c
            self.instruction_pointer += 2
        elif op == 'out':  # Output combo operand
            self.output.append(self.parse_combo_op() % 8)
            self.instruction_pointer += 2
        else:
            raise RuntimeError('Invalid op!')

    def run(self):
        self.halted = False
        self.instruction_pointer = 0
        self.output = []
        while not self.halted:
            try:
                self.run_next_instruction()
            except IndexError:
                self.halted = True
        return self


def test():
    assert Computer('0,0,9 -- 2,6').run().b == 1
    assert Computer('10,0,0 -- 5,0,5,1,5,4').run().output == [0, 1, 2]
    assert Computer('2024,0,0 -- 0,1,5,4,3,0').run().output == [4, 2, 5, 6, 7, 7, 7, 7, 3, 1, 0]
    assert Computer('2024,0,0 -- 0,1,5,4,3,0').run().a == 0
    assert Computer('0,29,0 -- 1,7').run().b == 26
    assert Computer('0,2024,43690 -- 4,0').run().b == 44354


def part1(filename):
    return ','.join(map(str, Computer(filename).run().output))


def part2(filename):
    computer = Computer(filename)
    desired_output = computer.ops

    results = [0]
    for i in range(len(desired_output)):
        candidates = range(0o10)
        new_results = set()
        for c in candidates:
            for n in results:
                value = n * 8 + c
                computer.a = value
                computer.b = computer.c = 0
                result = computer.run().output
                if not result:
                    continue
                if result == desired_output[-i-1:]:
                    new_results.add(value)
        results = new_results
    return min(results)


if __name__ == '__main__':
    test()
    assert part1('inputs/sample17a.txt') == '4,6,3,5,6,3,5,2,1,0'
    print('Part 1:', part1('inputs/day17.txt'))
    assert part2('inputs/sample17b.txt') == 117440
    print('Part 2', part2('inputs/day17.txt'))
