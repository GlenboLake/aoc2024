import os.path
from functools import lru_cache, reduce
from itertools import pairwise


@lru_cache
def next_secret(n):
    n = (n ^ (n * 64)) % 16777216
    n = (n ^ (n // 32)) % 16777216
    n = (n ^ (n * 2048)) % 16777216
    return n


def get_nth_secret(num, n):
    for _ in range(n):
        num = next_secret(num)
    return num


def part1(data):
    if os.path.exists(data):
        with open(data) as f:
            data = f.read()
    return sum(get_nth_secret(int(num), 2000) for num in data.splitlines())


def part2(data):
    if os.path.exists(data):
        with open(data) as f:
            data = f.read()

    def gen_secrets(seed):
        value = int(seed)
        yield value
        while True:
            value = next_secret(value)
            yield value

    buyers = []
    for init_secret in data.splitlines():
        print('.', end='')
        secrets = gen_secrets(init_secret)
        secret_history = [next(secrets) for _ in range(2001)]
        prices = [secret % 10 for secret in secret_history]
        diffs = [b - a for a, b in pairwise(prices)]
        diff_seqs = list(zip(diffs, diffs[1:], diffs[2:], diffs[3:]))
        price_per_seq = dict(list(zip(diff_seqs, prices[4:]))[::-1])
        buyers.append(price_per_seq)
    all_sequences = reduce(set.union, buyers, set())
    return max(
        sum(buyer.get(seq, 0) for buyer in buyers)
        for seq in all_sequences
    )


if __name__ == '__main__':
    assert part1('1\n10\n100\n2024') == 37327623
    print('Part 1:', part1('inputs/day22.txt'))
    assert part2('1\n2\n3\n2024') == 23
    print('Part 2:', part2('inputs/day22.txt'))
