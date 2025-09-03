

class C:
    def __init__(self):
        self.changed = False
        pass

    def execute(self):
        r = yield Operation("echo c")
        # print(f">>>>> Received in C: {r}")
        r = yield Operation("echo d")
        # print(f">>>>> Received in C: {r}")
        r = yield Operation("echo e")
        # print(f">>>>> Received in C: {r}")