from muse.scanner import Position

class CompileError:
    def __init__(self, msg: str, begin_pos: Position, is_warning=False):
        self.msg = msg
        self.begin_pos = begin_pos
        self.is_warning = is_warning

    def __str__(self):
        return '@{} : {}'.format(self.begin_pos, self.msg)


class RunError:
    def __init__(self, msg: str, begin_pos: Position, is_warning=False):
        self.msg = msg
        self.begin_pos = begin_pos
        self.is_warning = is_warning

    def __str__(self):
        return '@{} : {}'.format(self.begin_pos, self.msg)


if __name__ == '__main__':
    a = [1, 2]
    b = [3, 4]
    print(a + b)
