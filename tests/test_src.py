import time


def f() -> 'result1':
    time.sleep(1)
    return 123


def g() -> 'result2':
    time.sleep(1)
    return 345


def h(x: 'result1', y: 'result2') -> 'result3':
    time.sleep(1)
    return [x, y]


def a(x: 'result3') -> 'result4':
    time.sleep(1)
    return x + [567]


def b(y: 'result3') -> 'result5':
    time.sleep(1)
    return y + [789]


def c(x: 'result4', y: 'result5'):
    time.sleep(1)
    return x + y
