# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class NavBar(Component):
    """A NavBar component.
Dashboard navigation bar component
https://mui.com/components/app-bar/

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Component children.

- id (string; default 'navbar'):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    Additional CSS class for the root DOM node.

- title (string; optional):
    Dashboard navigation bar title."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_material_components'
    _type = 'NavBar'
    @_explicitize_args
    def __init__(self, children=None, title=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'title']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(NavBar, self).__init__(children=children, **args)
