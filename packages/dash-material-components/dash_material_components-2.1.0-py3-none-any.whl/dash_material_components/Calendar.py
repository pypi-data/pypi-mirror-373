# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Calendar(Component):
    """A Calendar component.
Calendar component
Wrapper for the lazy loaded calendar component

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Component children.

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    Additional CSS class for the root DOM node.

- disableFuture (boolean; optional):
    If True, future dates will be disabled.

- disablePast (boolean; optional):
    If True, past dates will be disabled.

- disableToolbar (boolean; optional):
    If True, the toolbar of the DatePicker will be hidden.

- disabled (boolean; optional):
    If True, the calendar input will be disabled.

- helperText (string; optional):
    The helper text that appears below the calendar input.

- labelText (string; optional):
    The label text displayed for the calendar input.

- margin (string | number; optional):
    Margin around the calendar box (CSS value as string or number).

- maxDate (string; optional):
    The maximum date that can be selected, in 'yyyy-MM-dd' format.

- minDate (string; optional):
    The minimum date that can be selected, in 'yyyy-MM-dd' format.

- selected (string; optional):
    The currently selected date, in 'yyyy-MM-dd' format.

- width (string | number; optional):
    Width of the calendar box (CSS value as string or number)."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_material_components'
    _type = 'Calendar'
    @_explicitize_args
    def __init__(self, children=None, labelText=Component.UNDEFINED, helperText=Component.UNDEFINED, width=Component.UNDEFINED, margin=Component.UNDEFINED, maxDate=Component.UNDEFINED, minDate=Component.UNDEFINED, disableFuture=Component.UNDEFINED, disablePast=Component.UNDEFINED, selected=Component.UNDEFINED, disableToolbar=Component.UNDEFINED, disabled=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'disableFuture', 'disablePast', 'disableToolbar', 'disabled', 'helperText', 'labelText', 'margin', 'maxDate', 'minDate', 'selected', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'disableFuture', 'disablePast', 'disableToolbar', 'disabled', 'helperText', 'labelText', 'margin', 'maxDate', 'minDate', 'selected', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Calendar, self).__init__(children=children, **args)
