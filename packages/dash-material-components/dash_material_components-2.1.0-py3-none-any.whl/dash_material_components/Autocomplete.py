# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Autocomplete(Component):
    """An Autocomplete component.
Autocomplete component

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Component children.

- id (string; default 'autocomplete'):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    Additional CSS class for the root DOM node.

- debounceSeconds (number; optional):
    Seconds to wait to fire Dash callback.

- disabled (boolean; default False):
    If True, the autocomplete input will be disabled.

- freeSolo (boolean; default False):
    Allow the user to enter a value not included in the options.

- groupByField (string; optional):
    Field in the option object to group options by in the list.

- labelText (string; optional):
    The label text displayed for the autocomplete input.

- limitTags (number; optional):
    Limit the number of tags displayed when `multiple` is enabled.

- margin (string | number; default 2):
    Margin around the autocomplete box (CSS value as string or
    number).

- multiple (boolean; default False):
    Allow multiple selections.

- options (list of dicts; required):
    Options available for selection in the autocomplete.

    `options` is a list of dicts with keys:

    - label (string; required)

    - value (string; required)

- selected (dict; optional):
    Currently selected option(s), can be a single option or an array
    of options.

    `selected` is a dict with keys:

    - label (string; required)

    - value (string; required) | list of dicts with keys:

    - label (string; required)

    - value (string; required)

- size (a value equal to: 'small', 'medium'; default 'small'):
    The size of the autocomplete input, can be 'small' or 'medium'.

- variant (a value equal to: 'filled', 'outlined', 'standard'; default 'outlined'):
    The variant of the autocomplete input, can be 'filled',
    'outlined', or 'standard'.

- width (string; default '100%'):
    Width of the autocomplete box (CSS value as string)."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_material_components'
    _type = 'Autocomplete'
    @_explicitize_args
    def __init__(self, children=None, labelText=Component.UNDEFINED, size=Component.UNDEFINED, variant=Component.UNDEFINED, selected=Component.UNDEFINED, options=Component.REQUIRED, limitTags=Component.UNDEFINED, freeSolo=Component.UNDEFINED, groupByField=Component.UNDEFINED, multiple=Component.UNDEFINED, width=Component.UNDEFINED, margin=Component.UNDEFINED, disabled=Component.UNDEFINED, debounceSeconds=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'debounceSeconds', 'disabled', 'freeSolo', 'groupByField', 'labelText', 'limitTags', 'margin', 'multiple', 'options', 'selected', 'size', 'variant', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'debounceSeconds', 'disabled', 'freeSolo', 'groupByField', 'labelText', 'limitTags', 'margin', 'multiple', 'options', 'selected', 'size', 'variant', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        for k in ['options']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Autocomplete, self).__init__(children=children, **args)
