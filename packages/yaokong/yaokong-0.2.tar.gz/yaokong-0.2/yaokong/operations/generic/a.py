from yaokong.operations.generic.b import B
from yaokong.operations.filesystem.directory import Directory


class A:
    def __init__(self):
        self.b = B()  # Instantiate a unique B object for this tree
        self.changed = False

    def execute(self):
        # r = yield Operation("echo r")
        # # print(f">>>>> Received in A: {r}")
        # yield self.b
        yield Directory(path="/tmp/kimbo1", present=True, sudo=False)
        # r = yield Chown(target="/tmp/kimbo1",group="root",options=["-R"],sudo=True)
        # print(f">>>>> Received in A: {r}")