def parse_input(filename):
    with open(filename) as f:
        return f.read().splitlines()


def part1(filename):
    word_search = parse_input(filename)
    size = len(word_search)

    def check_at(row, column):
        if word_search[row][column] != 'X':
            return 0
        v_search = [0]
        if row >= 3:
            v_search.append(-1)
        if row <= size - 4:
            v_search.append(1)
        h_search = [0]
        if column >= 3:
            h_search.append(-1)
        if column <= size - 4:
            h_search.append(1)
        search_directions = (
            (dr, dc)
            for dr in v_search
            for dc in h_search
            if (dr, dc) != (0, 0)
        )
        matches = 0
        for dr, dc in search_directions:
            for i, letter in enumerate('XMAS', start=0):
                r = row + dr * i
                c = column + dc * i
                if word_search[r][c] != letter:
                    break
            else:
                matches += 1
        return matches

    matches = 0
    for i, line in enumerate(word_search):
        for j, letter in enumerate(line):
            matches += check_at(i, j)
    return matches


def part2(filename):
    word_search = parse_input(filename)
    size = len(word_search)

    def is_xmas(row, column):
        if word_search[row][column] != 'A':
            return False
        if {word_search[row+1][column+1], word_search[row-1][column-1]} != {'M', 'S'}:
            return False
        if {word_search[row+1][column-1], word_search[row-1][column+1]} != {'M', 'S'}:
            return False
        return True

    matches = 0
    for r in range(1, size-1):
        for c in range(1, size-1):
            if is_xmas(r,c):
                matches += 1
    return matches


if __name__ == '__main__':
    assert part1('inputs/sample04.txt') == 18
    print('Part 1:', part1('inputs/day04.txt'))
    assert part2('inputs/sample04.txt') == 9
    print('Part 2:', part2('inputs/day04.txt'))
