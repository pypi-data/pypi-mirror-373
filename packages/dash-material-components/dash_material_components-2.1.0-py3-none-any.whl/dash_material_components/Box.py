# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Box(Component):
    """A Box component.
Box component from Material UI
https://mui.com/components/box/

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Component children.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    Additional CSS class for the root DOM node.

- sx (dict; optional):
    All Material system properties are available via the `sx prop`
    Allow additional css styles to be applied to the component."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_material_components'
    _type = 'Box'
    @_explicitize_args
    def __init__(self, children=None, sx=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'sx']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'sx']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Box, self).__init__(children=children, **args)
