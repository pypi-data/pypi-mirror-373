from dataclasses import dataclass
from .expression import Expression
from .query import QueryPlan
from .parser import parse_expression


@dataclass
class Attribute:
    name: str
    expression: Expression


@dataclass
class Tabulator:
    attributes: list[Attribute]
    plan: QueryPlan
    omit_missing_attributes: bool

    def get_rows(self, data):
        return self.plan.execute(data, omit_missing_attributes=self.omit_missing_attributes)


def tabulate(
        attributes: dict[str, str],
        omit_missing_attributes: bool = False
) -> Tabulator:
    if isinstance(attributes, dict):
        attributes = [
            Attribute(name, expression=parse_expression(expr))
            for name, expr in attributes.items()
        ]
    else:
        raise ValueError(f'Query not understood: {attributes}')
    plan = QueryPlan.from_dict({a.name: a.expression for a in attributes})
    return Tabulator(attributes, plan, omit_missing_attributes=omit_missing_attributes)
