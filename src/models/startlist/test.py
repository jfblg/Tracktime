from itertools import cycle

def createGenerator():
    mylist = range(1,4)
    for i in mylist:
        yield i

people = "fero olo peto milan jozef reto jerome yves".split()

result = []
indexing = createGenerator()
runde = 1
for name in people:
    print("Name: {}".format(name))
    print("Runde: {}".format(runde))
    try:
        print("Starting Line: {}".format(next(indexing)))
    except StopIteration:
        indexing = createGenerator()
        runde += 1
        print("Starting Line: {}".format(next(indexing)))


