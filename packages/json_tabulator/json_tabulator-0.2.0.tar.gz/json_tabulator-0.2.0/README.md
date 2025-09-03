# json_tabulator

A simple query language for extracting tables from JSON-like objects.

Working with tabular data is much easier than working with nested documents. json-tables helps to extract tables from JSON-like objects in a simple, declarative manner. All further processing is left to the many powerful tools that exist for working with tables, such as Spark or Pandas.


## Installation

Install from pypi:

```shell
pip install json_tabulator
```

## Quickstart

The `json_tabulator` module provides tools to extract a JSON document into a set of related tables. Let's start with a simple document

```python
data = {
    'id': 'doc-1',
    'table': [
        {'id': 1, 'name': 'row-1'},
        {'id': 2, 'name': 'row-2'}
    ]
}
```

The document consists of a document-level value `id` as well as a nested sub-table `table`. We want to extract it into a single table, with the global value folded into the table.

To do this, we write a query that defines the conversion into a table like this:

```python
from json_tabulator import tabulate

query = tabulate({
    'document_id': 'id',
    'row_id': 'table.*.id',
    'row_name': 'table.*.name'
})

rows = query.get_rows(data)
```

This returns an iterator of rows, where each row is a dict `{<column_name>: <value>}`:

```python
>>> list(rows)
[
    {'document_id': 'doc-1', 'row_id': 1, 'row_name': 'row-1'},
    {'document_id': 'doc-1', 'row_id': 2, 'row_name': 'row-2'}
]
```

### Path Syntax

The syntax for path expressions is similar to JSON Path. A path consists of an optional root element `'$'` followed by zero or more segments separated by `'.'`.

#### Dict key

Can be any string. Key values can be quoted with single or double quotes. Within quoted strings, the quote character must be doubled to escape it. For example, `"say ""hello""" -> say hello`.

Keys _must_ be quoted if they
* contain any of the characters `*$@.'"`, or if the
* contain only digits (these cases would be interpreted as array indices otherwise)

#### Array index

Array indices are entered as numbers without quotes, e.g. `123`. Mostly useful for debugging, usually arrays are iterated over when tabulating data.

#### Wildcard `*`

An asterisk `*` is interpreted as a wildcard. Iterates over dict values or array items. Note that wildcards _must_ be entered explicitly, there is no implicit iteration over arrays.

#### `@key` and `@path` directives.

The `@key` and `@path` directives are used to get information about the current key (dict key or array index) or the full path, respectively.

Both must follow after a wildcard, and must be the last segment in the path. For example `*.@key` is valid, but `a.@key` and `*.@key.b` are not.

The output of `@path` can be used as a primary key within the scope of the parsed object.

### Data Extraction

#### Query Semantics

Values for all attributes in a query are combined into individual rows. Attributes from different parts of the document are combined by "joining" on the lowest common ancestor.

For this reason, all wildcards for all attributes must lie on a common path. Violating this condition would lead to implicit cross joins and the associated data blow-up.

For example, the paths `$.a.*` and `$.b.*` cannot be combined because the wildcards are not on the same path. On the other hand, `$.a` and `$.b.*.c` can be combined.

Queries are analysed and compiled independent of the data to be queried

If you think you need to get a combination of attributes that is not allowed, think again. If you still think so just run multiple queries and do the join afterwards.

## Related Projects

- [jsontable](https://pypi.org/project/jsontable/) has the same purpose but is not maintained.
- [jsonpath-ng](https://github.com/bridgecrewio/jsonpath-ng) and other jsonpath implementation are much more flexible but more cumbersome to extract nested tables.
