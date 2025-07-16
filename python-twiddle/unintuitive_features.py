def while_else() -> None:
    i: int = 3
    while i > 0:
        print(f'{i} > 0')
        i -= 1
        break # also try without
    else:
        print(f'{i} <= 0')

class Thingie:

    def __init__(self, name: str, id: int) -> None:
        self.name = name
        self.id: int = id

    def __eq__(self, other):
        return self.id == other.id

def class_eq() -> None:
    first_thing = Thingie('one', 1)
    second_thing = Thingie('two', 2)
    zweites_ding = Thingie('zwei', 2)
    print(first_thing == second_thing)
    print(second_thing == zweites_ding)

def for_in_range() -> None:
    i: int = 1000
    for i in range(3):
        print(f'i = {i} in loop')
    print(f'i = {i} outside of loop')

    e = 1000
    try:
        print(1/0)
    except ZeroDivisionError as e:
        print(f'e = {repr(e)} in try')
    # print(f'e = {repr(e)} outside of try') e is not accessible anymore

def list_index():
    numbers: list[int|str] = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    numbers[2] = 100
    numbers[5:4] = ['A', 'B', 'C', 'D', 'E']
    print(numbers)

def bad_add_to_list(item: str, target: list[str] = []): # dangerous default!
    target.append(item)
    return target

def good_add_to_list(item: str, target: list[str]|None = None):
    if target is None:
        return [item]
    else:
        target.append(item)
        return target

def adding_to_list():
    l1: list[str] = bad_add_to_list('one') # also try with `(..., [])`
    bad_add_to_list('two', l1)
    print(l1)

    l2: list[str] = bad_add_to_list('three')
    print(l2)

    l1: list[str] = good_add_to_list('one') # also try with `(..., [])`
    good_add_to_list('two', l1)
    print(l1)

    l2: list[str] = good_add_to_list('three')
    print(l2)

if __name__ == '__main__':
    while_else()

