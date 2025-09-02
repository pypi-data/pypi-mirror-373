# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Tab(Component):
    """A Tab component.
Tab component
Dashboard > Page > Section > Card > Tab
https://github.com/danielfrg/jupyter-flex/blob/main/js/src/Section/index.js

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Component children.

- id (string; default 'tab'):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    Additional CSS class for the root DOM node.

- tabs (list of dicts; required):
    Array of tabs to render as component children.

    `tabs` is a list of dicts with keys:

    - label (string; required):
        Element label."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_material_components'
    _type = 'Tab'
    @_explicitize_args
    def __init__(self, children=None, tabs=Component.REQUIRED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'tabs']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'tabs']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['tabs']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Tab, self).__init__(children=children, **args)
