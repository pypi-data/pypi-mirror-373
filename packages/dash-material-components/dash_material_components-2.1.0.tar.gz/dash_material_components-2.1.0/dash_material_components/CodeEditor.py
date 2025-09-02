# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class CodeEditor(Component):
    """A CodeEditor component.
 component (gets export

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    Component children.

- id (string; default 'code-editor'):
    Unique ID to identify this component in Dash callbacks.

- className (string; optional):
    Additional CSS class for the root DOM node.

- darkTheme (boolean; default False):
    If True, use dark theme instead of light theme.

- height (string; default '400px'):
    The height of the editor.

- highlightActiveLine (boolean; default True):
    If True, the active line will be highlighted.

- lineNumbers (boolean; default True):
    If True, shows line numbers.

- margin (string | number; default 2):
    Margin around the editor.

- moduleDefinitions (dict; optional):
    Module definitions for code completion.

    `moduleDefinitions` is a dict with strings as keys and values of
    type dict with keys:

    - importName (string; optional)

    - items (dict; required)

        `items` is a dict with strings as keys and values of type dict
        with keys:

        - label (string; required)

        - type (a value equal to: 'object', 'function', 'class', 'method', 'property', 'variable', 'module', 'attribute'; required)

        - info (string; optional)

        - returns (string; optional)

        - items (boolean | number | string | dict | list; optional)

- readOnly (boolean; default False):
    If True, the editor will be read-only.

- tabSize (number; default 2):
    Number of spaces for tabs.

- value (string; default ''):
    The initial value of the editor.

- width (string; default '100%'):
    The width of the editor."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_material_components'
    _type = 'CodeEditor'
    @_explicitize_args
    def __init__(self, children=None, value=Component.UNDEFINED, height=Component.UNDEFINED, width=Component.UNDEFINED, margin=Component.UNDEFINED, readOnly=Component.UNDEFINED, lineNumbers=Component.UNDEFINED, tabSize=Component.UNDEFINED, highlightActiveLine=Component.UNDEFINED, darkTheme=Component.UNDEFINED, moduleDefinitions=Component.UNDEFINED, id=Component.UNDEFINED, className=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'className', 'darkTheme', 'height', 'highlightActiveLine', 'lineNumbers', 'margin', 'moduleDefinitions', 'readOnly', 'tabSize', 'value', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'className', 'darkTheme', 'height', 'highlightActiveLine', 'lineNumbers', 'margin', 'moduleDefinitions', 'readOnly', 'tabSize', 'value', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}

        super(CodeEditor, self).__init__(children=children, **args)
