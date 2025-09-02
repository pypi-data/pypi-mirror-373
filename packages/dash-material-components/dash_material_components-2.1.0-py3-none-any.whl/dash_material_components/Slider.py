# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Slider(Component):
    """A Slider component.
Slider component

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Component children.

- id (string; default 'slider'):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    Additional CSS class for the root DOM node.

- disabled (boolean; default False):
    Disable the component.

- inputLeftAdornment (string; optional):
    InputText LEFT adornment.

- inputRightAdornment (string; optional):
    InputText RIGHT adornment.

- inputType (a value equal to: 'integer', 'float'; optional):
    Input type, if set an input text is displayed alongside the
    slider.

- labelText (string; optional):
    Text to display above the slider form.

- margin (string | number; default 2):
    Margin of the component.

- marks (list of dicts; optional):
    Array of selection marks to display below the slider form.

    `marks` is a list of dicts with keys:

    - value (number; required)

    - label (string; required)

- maxValue (number; default 100):
    Maximum selection allowed in the slider.

- minValue (number; default 0):
    Minimum selection allowed in the slider.

- precision (number; default 2):
    Number of decimal places.

- selected (number; default 50):
    Active slider selection.

- stepValue (number; default 10):
    Slider selection increment.

- width (string | number; default '100%'):
    Width of slider form."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_material_components'
    _type = 'Slider'
    @_explicitize_args
    def __init__(self, children=None, labelText=Component.UNDEFINED, width=Component.UNDEFINED, margin=Component.UNDEFINED, maxValue=Component.UNDEFINED, minValue=Component.UNDEFINED, stepValue=Component.UNDEFINED, marks=Component.UNDEFINED, selected=Component.UNDEFINED, inputType=Component.UNDEFINED, precision=Component.UNDEFINED, inputLeftAdornment=Component.UNDEFINED, inputRightAdornment=Component.UNDEFINED, disabled=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'disabled', 'inputLeftAdornment', 'inputRightAdornment', 'inputType', 'labelText', 'margin', 'marks', 'maxValue', 'minValue', 'precision', 'selected', 'stepValue', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'disabled', 'inputLeftAdornment', 'inputRightAdornment', 'inputType', 'labelText', 'margin', 'marks', 'maxValue', 'minValue', 'precision', 'selected', 'stepValue', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(Slider, self).__init__(children=children, **args)
