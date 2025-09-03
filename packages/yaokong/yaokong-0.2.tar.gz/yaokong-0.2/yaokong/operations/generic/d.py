
class D:
    def __init__(self):
        self.x = "g"  # Default value for x
        self.changed = False

    def execute(self):
        r = yield Operation("echo f")
        # print(f">>>>> Received in D: {r}")
        r = yield Operation(f"echo {self.x}")
        # print(f">>>>> Received in D: {r}")
        r = yield Operation("echo h")
        # print(f">>>>> Received in D: {r}")