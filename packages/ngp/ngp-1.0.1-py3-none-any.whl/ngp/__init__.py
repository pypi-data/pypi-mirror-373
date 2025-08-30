__version__ = "1.0.1"

import random
import sys

LEFT = list("qwertasdfgzxcv")
RIGHT = list("yuiophjklbnm")

def generate(options):
    length = random.randrange(options['min-length'], options['max-length'] + 1)

    result = ''
    current = LEFT + RIGHT
    for i in range(length):
        char = random.choice(current)
        result += char

        if char in LEFT:
            current = RIGHT
        else:
            current = LEFT
    return result


def main():
    args = sys.argv[1:]
    options = {
        'count': 20,
        'min-length': 3,
        'max-length': 7,
    }

    for arg in args:
        if '=' not in arg:
            usage_args = ' '.join([f"[--{key}={key.upper().replace('-', '_')}]" for key in options.keys()])
            exit(f"Usage: {sys.argv[0]} {usage_args}\n\nGenerate phrases that are easy to type when using QWERTY")

        key, val = arg.lstrip('-').split('=')
        key = key.lower()
        options[key] = type(options[key])(val)

    assert options['min-length'] <= options['max-length'], "max-length can't be shorter than min-length"

    for _ in range(options['count']):
        print(generate(options))
