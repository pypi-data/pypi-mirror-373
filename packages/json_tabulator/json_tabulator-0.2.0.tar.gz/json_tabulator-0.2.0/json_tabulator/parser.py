
from .expression import Expression, STAR, KEY, PATH

from parsy import string, regex, eof, alt, seq, ParseError


dot = string('.').then(eof.should_fail('expression to continue'))
star = string('*').result(STAR)
root = string('$')
forbidden = ''.join(['"', "'", '.', '$', '*', '@'])
end_of_segment = eof | dot
at = string('@')

def make_quoted_key(q: str):
    return string(q) >> regex(f'({2 * q}|[^{q}])+') << string(q)


key = regex(f'[^{forbidden}]+')
quoted_key = (make_quoted_key('"') | make_quoted_key("'"))
number = regex(r'\d+').map(int)
func_key = at >> string('key').result(KEY)
func_path = at >> string('path').result(PATH)
function = alt(func_key, func_path)


segment = alt(
    (star.skip(dot)).then(function.map(lambda x: [STAR, x])).skip(eof),
    *[p.skip(dot | eof) for p in [number, quoted_key, star, key]]
)


def concat_list(*args):
    res = []
    for a in args:
        if isinstance(a, list):
            res += a
        else:
            res.append(a)
    return res


expression = alt(
    root.optional().then(eof).result([]),
    seq(root, dot).optional().then(segment.many()).combine(concat_list),
)


class InvalidExpression(ValueError):
    pass


def parse_expression(string: str) -> Expression:
    try:
        return Expression(expression.parse(string))
    except ParseError:
        raise InvalidExpression(string)
