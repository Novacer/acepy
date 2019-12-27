
def f() -> 'result1':
    return 123


def g() -> 'result2':
    return 345


def h(x: 'result1', y: 'result2') -> 'result3':
    return [x, y]


def a(x: 'result3') -> 'result4':
    return x + [567]


def b(y: 'result3') -> 'result5':
    return y + [789]


def c(x: 'result4', y: 'result5'):
    return x + y
