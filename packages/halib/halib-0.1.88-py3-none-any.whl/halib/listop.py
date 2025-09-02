def subtract(list_a, list_b):
    return [item for item in list_a if item not in list_b]


def union(list_a, list_b, no_duplicate=False):
    if no_duplicate:
        return list(set(list_a) | set(list_b))
    else:
        return list_a + list_b


def intersection(list_a, list_b):
    return list(set(list_a) & set(list_b))
