# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Typography(Component):
    """A Typography component.
Typography component from Material UI
https://mui.com/components/typography/

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Component children.

- id (string; default 'text'):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    Additional CSS class for the root DOM node.

- component (boolean | number | string | dict | list; default 'h6'):
    Typography HTML node type.

- text (string; optional):
    Text to display.

- variant (a value equal to: 'button', 'caption', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'subtitle1', 'subtitle2', 'body1', 'body2', 'overline'; default 'h6'):
    Typography variant."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_material_components'
    _type = 'Typography'
    @_explicitize_args
    def __init__(self, children=None, component=Component.UNDEFINED, variant=Component.UNDEFINED, text=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'component', 'text', 'variant']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'component', 'text', 'variant']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Typography, self).__init__(children=children, **args)
