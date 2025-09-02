from functools import reduce


def ilen(iterable):
    return reduce(lambda sum, element: sum + 1, iterable, 0)


def leaf_subclasses(parent_class):
    if subclasses := parent_class.__subclasses__():
        for sub_class in subclasses:
            yield from leaf_subclasses(sub_class)
    else:
        yield parent_class
