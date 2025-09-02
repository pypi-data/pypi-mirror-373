# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Table(Component):
    """A Table component.
Table component

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Component children.

- id (string; default 'table'):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    Additional CSS class for the root DOM node.

- columns (list of dicts; required):
    Array of table columns to render.

    `columns` is a list of dicts with keys:

    - field (string; required):
        Column field.

    - width (number; required):
        Column width.

- rows (list of dicts with strings as keys and values of type string | number; required):
    Array of table rows to render.

- rowsPerPageOptions (list of numbers; default [10, 25, 50]):
    Table pagination setting.

- tableStyle (dict; optional):
    Custom sx styles for TableContainer -
    https://mui.com/system/getting-started/the-sx-prop/."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_material_components'
    _type = 'Table'
    @_explicitize_args
    def __init__(self, children=None, columns=Component.REQUIRED, rows=Component.REQUIRED, rowsPerPageOptions=Component.UNDEFINED, tableStyle=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'columns', 'rows', 'rowsPerPageOptions', 'tableStyle']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'columns', 'rows', 'rowsPerPageOptions', 'tableStyle']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['columns', 'rows']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Table, self).__init__(children=children, **args)
