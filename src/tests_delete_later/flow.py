
# TODO generate random times
# TODO algoritmus to realocate last 2 runs in a category

import random

# 12:23.4456

def main():
    print(generate_time())


def generate_time():
    """
    Generates a pseudo-random time and returns it as a string
    Only temporary solution until not integrated with timy

    :return:
    string
    """
    minutes = random.randrange(12, 15)
    seconds = round(random.uniform(10.0, 60.0), 4)
    return "{0:01d}:{1}".format(minutes, seconds)


if __name__ == "__main__":
    main()