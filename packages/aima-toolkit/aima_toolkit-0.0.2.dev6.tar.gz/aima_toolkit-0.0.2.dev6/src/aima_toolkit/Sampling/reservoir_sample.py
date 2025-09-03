import random

def reservoir_sample(iterable):
    choice = None
    for i, x in enumerate(iterable, 1):
        if random.randrange(i) == 0:  # probability 1/i
            choice = x
    return choice

def reservoir_sample_k(iterable, k : int) -> list:
    assert k > 0, "k must be greater than 0"
    reservoir = []

    for i, x in enumerate(iterable):
        if i < k:
            reservoir.append(x)
        else:
            j = random.randint(0, i)
            if j < k:
                reservoir[j] = x
    return reservoir