from yaokong.operations.generic.c import C
from yaokong.operations.generic.d import D

class B:
    def __init__(self):
        self.c = C()  # Instantiate a unique C object for this tree
        self.d = D()  # Instantiate a unique D object for this tree
        self.changed = False

    def execute(self):
        yield self.c
        r = yield Operation("echo a")
        # print(f">>>>> Received in B: {r}")
        yield self.d