# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Section(Component):
    """A Section component.
Section component
Dashboard > Page > Section

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Component children.

- id (string; default 'section'):
    Unique ID to identify this component in Dash callbacks.

- cards (list of dicts; required):
    Array of cards to render as component children.

    `cards` is a list of dicts with keys:

    - title (string; required):
        Card title.

    - size (number; required):
        Card size (0 < size <= 12).

    - downloadable (boolean; required):
        Card downloadable.

- className (string; optional):
    Additional CSS class for the root DOM node.

- downloaded (number; default 0):
    Section download counter.

- orientation (a value equal to: 'columns', 'rows'; default 'rows'):
    Section general orientation (rows or columns).

- size (number; optional):
    Section container size (0 < size <= 12)."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_material_components'
    _type = 'Section'
    @_explicitize_args
    def __init__(self, children=None, cards=Component.REQUIRED, size=Component.UNDEFINED, orientation=Component.UNDEFINED, downloaded=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'cards', 'className', 'downloaded', 'orientation', 'size']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'cards', 'className', 'downloaded', 'orientation', 'size']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['cards']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Section, self).__init__(children=children, **args)
