# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Alert(Component):
    """An Alert component.
Alert component

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Component children.

- id (string; default 'alert'):
    Unique ID to identify this component in Dash callbacks.

- autoHide (number; default 5000):
    Automatically hide the alert (in ms).

- className (string; optional):
    Additional CSS class for the root DOM node.

- message (string; optional):
    Message to display.

- severity (a value equal to: 'success', 'info', 'warning', 'error'; default 'error'):
    Alert type."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_material_components'
    _type = 'Alert'
    @_explicitize_args
    def __init__(self, children=None, severity=Component.UNDEFINED, autoHide=Component.UNDEFINED, message=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'autoHide', 'className', 'message', 'severity']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'autoHide', 'className', 'message', 'severity']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Alert, self).__init__(children=children, **args)
