from yaokong.operation import Operation


class Chown:
    def __init__(self, target: str,
                 user: str | None = None,
                 group: str | None = None,
                 options=None,
                 sudo: bool = False):

        command = "chown"
        user_group = None

        if user and group:
            user_group = "{0}:{1}".format(user, group)

        elif user:
            user_group = user

        elif group:
            command = "chgrp"
            user_group = group

        op=[]
        op.append(command)
        op.extend(options)
        op.append(user_group)
        op.append(target)

        self.chown = " ".join(op)
        self.target = target
        self.sudo = sudo

    def execute(self):
        _sudo = "sudo -S " if self.sudo else ""
        r0 = yield Operation(f"{_sudo}ls -ld {self.target}")

        r1 = yield Operation(f"{_sudo}{self.chown}")

        r2 = yield Operation(f"{_sudo}ls -ld {self.target}")

        if r0.cp.stdout != r2.cp.stdout:
            r1.changed=True
