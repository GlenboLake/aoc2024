from typing import Callable, Collection

type GateMap = dict[str, tuple[Callable[[int, int], int], Collection[str]]]


def parse(filename):
    with open(filename) as f:
        labels = {}
        gates: GateMap = {}
        for line in f:
            if line.isspace():
                break
            label, value = line.split(': ')
            labels[label] = int(value)
        ops = {
            'AND': int.__and__,
            'OR': int.__or__,
            'XOR': int.__xor__,
        }
        for line in f:
            a, op, b, _, out = line.split()
            gates[out] = ops[op], {a, b}
    return labels, gates


def solve_system(labels, gates: GateMap):
    labels = labels.copy()
    required = {out for out in gates if out.startswith('z')}
    while not required.issubset(labels):
        unsolved_gates = {g for g in gates if g not in labels}
        for gate in unsolved_gates:
            op, (a, b) = gates[gate]
            if a in labels and b in labels:
                labels[gate] = op(labels[a], labels[b])
    return [labels[z] for z in sorted(required)]


def part1(input):
    labels, gates = parse(input)
    result = solve_system(labels, gates)
    return sum(value << i for i, value in enumerate(result))


def part2(input):
    labels, gates_by_output = parse(input)
    gates_by_input: dict[tuple[str, str], dict[str, str]] = {}
    for output, (op, inputs) in gates_by_output.items():
        op_name = op.__name__[2:-2].upper()
        a, b = sorted(inputs)
        gates_by_input.setdefault((a, b), {})[op_name] = output

    swaps: dict[str, str] = {}  # At the end, this should have 8 entries, with 4 of them being reverses of the other 4
    detected_carries: dict[str, str] = {}

    def find_gate(op: str, expected_inputs: Collection[str], expected_output: str):
        matching_gates = [
            (inputs, output)
            for inputs, gates in gates_by_input.items()
            for op_name, output in gates.items()
            if op_name == op and (
                    output == expected_output
                    or (set(inputs) & set(expected_inputs))
            )
        ]
        assert len(matching_gates) == 1
        return matching_gates[0]

    def get_wire(name_or_alias):
        if name_or_alias in detected_carries:
            return detected_carries[name_or_alias]
        if name_or_alias in swaps:
            return swaps[name_or_alias]
        return name_or_alias

    def detect_half_adder(zi):
        """
        For a given result bit zi, validate half adder calculation

        Find the corresponding xi and yi inputs, validate and detect carry output

        :return: The wire holding the carry_out value of the adder
        """
        xi = zi.replace('z', 'x')
        yi = zi.replace('z', 'y')
        # Check sum
        sum_wire = None
        try:
            sum_wire = gates_by_input[xi, yi]['XOR']
            assert sum_wire == zi
        except KeyError:
            print(f'Gate {xi} XOR {yi} not found')
        except AssertionError:
            print(f'{xi} XOR {yi} -> {sum_wire} (instead of {zi})')
        # Check carry
        try:
            return gates_by_input[xi, yi]['AND']
        except KeyError:
            print(f'Gate {xi} AND {yi} not found')

    def detect_full_adder(zi):
        """
        Detect a full-adder for a given zi

        For an input xi, yi with carry ci, the following gates are expected:

        zi = ci XOR (xi XOR yi)
        carry_out = (xi AND yi) OR (ci AND (xi XOR yi)

        Notation of wires in this function
        xi XOR yi: simple_sum, since this is the sum value in a half-adder
        xi AND yi: simple_carry, since this is the carry value in a half-adder
        ci AND (xi XOR yi): intermediate_carry

        If any wires don't match the label they ought to have,
        the mismatch is recorded in the swaps dict

        :return: The wire holding the carry_out value of the adder
        """
        xi = zi.replace('z', 'x')
        yi = zi.replace('z', 'y')
        ci = zi.replace('z', 'c')  # This is the _input_ carry, and should be in detected_carries
        # The output of 2 full-adder gates can be guaranteed, since the
        # problem states that two gate outputs are switched and these
        # inputs are known.
        simple_carry = gates_by_input[xi, yi]['AND']
        simple_sum = gates_by_input[xi, yi]['XOR']
        # Try to confirm that ci XOR sc -> zi
        expected_inputs = {get_wire(ci), simple_sum}
        zi_inputs, detected_zi = find_gate('XOR', expected_inputs, zi)
        # If it's the wrong zi, that's a swap
        if zi != detected_zi:
            swaps[zi] = detected_zi
            swaps[detected_zi] = zi
        # Check both inputs
        if set(zi_inputs) != expected_inputs:
            a, b = set(zi_inputs) ^ expected_inputs
            swaps[a] = b
            swaps[b] = a

        # The two inputs to zi's XOR should also go to an AND gate, producing intermediate_carry
        ic_input, intermediate_carry = find_gate('AND', zi_inputs, '')
        # Since outputs, not inputs, have been swapped, this assert should be safe
        assert set(ic_input) == set(zi_inputs)

        # The result of the above AND gate and simple_carry go to an OR gate, producing carry_out
        expected_carry_out_inputs = {simple_carry, intermediate_carry}
        carry_out_inputs, carry_out = find_gate('OR', expected_carry_out_inputs, '')
        # Validate that the inputs aren't part of a new swap
        carry_out_inputs = {get_wire(wire) for wire in carry_out_inputs}
        if carry_out_inputs != expected_carry_out_inputs:
            a, b = carry_out_inputs ^ expected_carry_out_inputs
            swaps[a] = b
            swaps[b] = a
        return get_wire(carry_out)

    result_wires = sorted(g for g in gates_by_output if g.startswith('z'))
    assert result_wires[0] == 'z00'
    assert [wire.lstrip('z') for wire in result_wires[1:]] == [f'{i:02}' for i in range(1, len(result_wires))]

    detected_carries['c01'] = detect_half_adder(result_wires[0])
    for i, wire in enumerate(result_wires[1:-1], start=2):
        carry_name = f'c{i:02}'
        carry = detect_full_adder(wire)
        if carry:
            detected_carries[carry_name] = carry
    # Final carry should be the final z
    last_carry = max(detected_carries)
    assert detected_carries[last_carry] == last_carry.replace('c', 'z')
    return ','.join(sorted(swaps))


if __name__ == '__main__':
    assert part1('inputs/sample24.txt') == 2024
    print('Part 1:', part1('inputs/day24.txt'))
    print('Part 2:', part2('inputs/day24.txt'))
