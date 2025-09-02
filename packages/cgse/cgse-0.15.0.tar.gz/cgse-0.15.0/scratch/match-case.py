class Car:
    __match_args__ = ('key', 'name')

    def __init__(self, key, name):
        self.key = key
        self.name = name


def main():
    expr = eval(input('Expr: '))
    match expr:
        case (0, x):              # seq of 2 elems with first 0
            print(f'(0, {x})')    # (new variable x set to second elem)
        case ['a', x, 'c']:       # seq of 3 elems: 'a', anything, 'c'
            print(f"'a', {x!r}, 'c'")
        case {'foo': bar}:        # dict with key 'foo' (may have others)
            print(f"{{'foo': {bar}}}")
        case [1, 2, *rest]:       # seq of: 1, 2, ... other elements
            print(f'[1, 2, *{rest}]')
        case {'x': x, **kw}:      # dict with key 'x' (others go to kw)
            print(f"{{'x': {x}, **{kw}}}")
        case Car(key=key, name='Tesla'):  # Car with name 'Tesla' (any key)
            print(f"Car({key!r}, 'TESLA!')")
        case Car(key, name):      # similar to above, but use __match_args__
            print(f"Car({key!r}, {name!r})")
        case 1 | 'one' | 'I':     # int 1 or str 'one' or 'I'
            print('one')
        case ['a'|'b' as ab, c]:  # seq of 2 elems with first 'a' or 'b'
            print(f'{ab!r}, {c!r}')
        case (x, y) if x == y:    # seq of 2 elems with first equal to second
            print(f'({x}, {y}) with x==y')
        case _:
            print('no match')
            return "Quit"


if __name__ == '__main__':

    while True:
        if main() == "Quit":
            break
