import itertools as it
import enum


class Segment(enum.Enum):
    star = enum.auto()
    key = enum.auto()
    path = enum.auto()


STAR = Segment.star
KEY = Segment.key
PATH = Segment.path


def is_function(path: tuple):
    if len(path) != 1:
        return False
    return path[0] in (KEY, PATH)


class Expression(tuple):
    def __repr__(self):
        return f'Expression({self.to_string()})'

    def to_string(self):
        def render_element(seg):
            if seg is STAR:
                return '*'
            elif seg in (PATH, KEY):
                return f'@{seg.name}'
            elif isinstance(seg, str):
                return quote(seg)
            elif isinstance(seg, int):
                return str(seg)
            else:
                raise ValueError(f'Not a path segment: {seg}')

        return '.'.join(it.chain(['$'], map(render_element, self)))

    def __str__(self):
        return self.to_string()

    def get_table(self):
        idx = -1
        for i, seg in enumerate(self):
            if seg is STAR:
                idx = i
        return Expression(self[:idx + 1])

    def coincides_with(self, other):
        return all(a == b for a, b in zip(self, other))

    def is_concrete(self):
        return not any(seg is STAR for seg in self)

    def __add__(self, other):
        return Expression(super().__add__(other))


def expression(*args) -> Expression:
    if len(args) == 1 and isinstance(args[0], (tuple, list)):
        return Expression(args[0])
    return Expression(args)


def quote(s: str) -> str:
    require_quote = (
        s.isdigit()
        or s == '*'
        or '.' in s
    )
    if require_quote:
        return f'"{s}"'
    return s
