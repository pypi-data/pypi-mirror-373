import os
from typing import Any, List

curdir = os.path.dirname(os.path.realpath(__file__))

DOUBLE_THR = 1e-6


def to_abs(path):
    return os.path.join(curdir, path)


def is_float(inp: Any) -> bool:
    if isinstance(inp, str):
        is_float = False
        try:
            float(inp)
            is_float = True
        except:
            pass
        return is_float
    else:
        return isinstance(inp, float) or isinstance(inp, int)


def is_int(inp: Any) -> bool:
    if isinstance(inp, str):
        is_int = False
        try:
            int(inp)
            is_int = True
        except:
            pass
        return is_int
    else:
        return isinstance(inp, int)


def match_lists(a: List, b: List) -> bool:
    # print("{} vs. {}".format(repr(a), repr(b)))
    if len(a) != len(b):
        return False

    if len(a) == 0:
        print("Len {} vs. {}".format(repr(a), repr(b)))
        return True
    okay = True
    for item_a, item_b in zip(a, b):
        if isinstance(item_a, list) and isinstance(item_b, list):
            # if not match_lists(item_a, item_b):
            #     print("Lists {} vs. {}".format(repr(item_a), repr(item_b)))
            okay = okay and match_lists(item_a, item_b)
        elif is_int(item_a) and is_int(item_b):
            # if not a == b:
            #     print("Ints {} vs. {}".format(repr(item_a), repr(item_b)))
            okay = okay and (a == b)
        elif is_float(item_a) and is_float(item_b):
            if not (abs(item_a - item_b) < DOUBLE_THR):
                print("Floats {} vs. {}".format(repr(item_a), repr(item_b)))
            okay = okay and (abs(item_a - item_b) < DOUBLE_THR)
        else:
            raise RuntimeError("Unexpected types of {} and {}".format(
                repr(a), repr(b)))
    return okay
