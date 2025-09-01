from typing import List, Dict, Any, Optional, Union

class Component:
    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError("Must implement to_dict method.")

class Header(Component):
    def __init__(self, title: str, subtitle: Optional[str] = None, logo: Optional[str] = None):
        self.title = title
        self.subtitle = subtitle
        self.logo = logo

    def to_dict(self):
        return {
            'type': 'header',
            'properties': {
                'title': self.title,
                'subtitle': self.subtitle,
                'logo': self.logo,
            },
        }

class Footer(Component):
    def __init__(self, content: str):
        self.content = content

    def to_dict(self):
        return {
            'type': 'footer',
            'properties': {
                'content': self.content,
            },
        }

class Sidebar(Component):
    def __init__(self, items: List[str]):
        self.items = items

    def to_dict(self):
        return {
            'type': 'sidebar',
            'properties': {
                'items': self.items,
            },
        }

class MainContent(Component):
    def __init__(self, children: List[Component]):
        self.children = children

    def to_dict(self):
        return {
            'type': 'main-content',
            'children': [child.to_dict() for child in self.children],
        }


class ChatWindow(Component):
    def __init__(self, placeholder: str = 'Type your message...', send_button_label: str = 'Send', endpoint_url: str = '/api/chat'):
        self.placeholder = placeholder
        self.send_button_label = send_button_label
        self.endpoint_url = endpoint_url

    def to_dict(self):
        return {
            'type': 'chat-window',
            'properties': {
                'placeholder': self.placeholder,
                'sendButtonLabel': self.send_button_label,
                'endpointUrl': self.endpoint_url,
            },
        }

class DataTable(Component):
    def __init__(
            self,             
            columns: List[Dict[str, Any]], 
            data_source: str, 
            actions: Optional[List[Dict[str, Any]]] = None,
            row_selection: Optional[bool] = False,
            selected_row_keys: Optional[List[str]] = None,
            on_selection_change: Optional[str] = None,
            title: Optional[str] = None,
        ):
        self.title = title
        self.columns = columns
        self.data_source = data_source  # Should be a reference to data in dataContext
        self.actions = actions or []
        self.row_selection = row_selection
        self.selected_row_keys = selected_row_keys
        self.on_selection_change = on_selection_change

    def to_dict(self):
        return {
            'type': 'data-table',
            'properties': {
                'title': self.title,
                'columns': self.columns,
                'dataSource': self.data_source,  # Should be in the form '{{dataKey}}'
                'actions': self.actions,
                'rowSelection': self.row_selection,
                'selectedRowKeys': self.selected_row_keys,
                'onSelectionChange': self.on_selection_change,
            },
        }

class Chart(Component):
    def __init__(self, chart_type: str, data_source: str, options: Optional[Dict[str, Any]] = None):
        self.chart_type = chart_type
        self.data_source = data_source
        self.options = options or {}

    def to_dict(self):
        return {
            'type': 'chart',
            'properties': {
                'chartType': self.chart_type,
                'dataSource': self.data_source,
                'options': self.options,
            },
        }

class Form(Component):
    def __init__(self, children: List[Component], on_submit: List[str]):
        self.children = children
        self.on_submit = on_submit

    def to_dict(self):
        return {
            'type': 'form',
            'properties': {
                'onSubmit': self.on_submit,
            },
            'children': [child.to_dict() for child in self.children],
        }

class FormItem(Component):
    def __init__(self, label: str, children: List[Component], visible: bool = True):
        self.label = label
        self.children = children
        self.visible = visible

    def to_dict(self):
        return {
            'type': 'form-item',
            'properties': {
                'label': self.label,
                'visible': self.visible,
            },
            'children': [child.to_dict() for child in self.children],
        }

class Input(Component):
    def __init__(self, name: str, type: str = 'text', placeholder: str = '', required: bool = False, value: str = None, checked: bool = False):
        self.name = name
        self.type = type
        self.placeholder = placeholder
        self.required = required
        self.value = value
        self.checked = checked

    def to_dict(self):
        return {
            'type': 'input',
            'properties': {
                'name': self.name,
                'type': self.type,
                'placeholder': self.placeholder,
                'required': self.required,
                'value': self.value,
                'checked': self.checked,
            },
        }

class TextArea(Component):
    def __init__(self, name: str, placeholder: str = '', value: str = None, required: bool = False, rows: int = 3):
        self.name = name
        self.placeholder = placeholder
        self.value = value
        self.required = required
        self.rows = rows

    def to_dict(self):
        return {
            'type': 'textarea',
            'properties': {
                'name': self.name,
                'placeholder': self.placeholder,
                'value': self.value,
                'required': self.required,
                'rows': self.rows,
            },
        }

class Upload(Component):
    def __init__(self, name: str, required: bool, multiple: bool = False):
        self.name = name
        self.required = required
        self.multiple = multiple

    def to_dict(self):
        return {
            'type': 'upload',
            'properties': {
                'name': self.name,
                'required': self.required,
                'multiple': self.multiple,
            },
        }

class Button:
    def __init__(
        self,
        label: str = '',
        on_click: str = None,
        button_type: str = 'button',
        condition: str = None,
        confirm: bool = False,
        confirmMessage: str = '',
        style: dict = None,
        icon: str = None,
        disabled: bool = False,
        btn_class: str = 'btn btn-secondary',
    ):
        self.label = label
        self.on_click = on_click
        self.button_type = button_type
        self.condition = condition
        self.confirm = confirm
        self.confirmMessage = confirmMessage
        self.style = style or {}
        self.icon = icon
        self.disabled = disabled
        self.btn_class = btn_class

    def to_dict(self):
        return {
            'type': 'button',
            'properties': {
                'label': self.label,
                'onClick': self.on_click,
                'buttonType': self.button_type,
                'condition': self.condition,
                'confirm': self.confirm,
                'confirmMessage': self.confirmMessage,
                'style': self.style,
                'icon': self.icon,
                'disabled': self.disabled,
                'btnClass': self.btn_class,
            },            
        }

class Text(Component):
    def __init__(self, content: Union[str, List[Dict[str, Any]]], style: Optional[Dict[str, Any]] = None):
        self.content = content
        self.style = style

    def to_dict(self):
        return {
            'type': 'text',
            'properties': {
                'content': self.content,
                'style': self.style,
            },
        }

class Select(Component):
    def __init__(
            self, 
            name: str, 
            options: List[Dict[str, Any]], 
            multiple: bool = False, 
            required: bool = False,
            placeholder: Optional[str] = None,
            label_field: Optional[str] = 'label',
            value_field: Optional[str] = 'value',
            on_change: Optional[str] = None,
            value: Optional[str] = None,
        ):
        self.name = name
        self.options = options
        self.multiple = multiple
        self.required = required
        self.placeholder = placeholder
        self.value_field = value_field
        self.label_field = label_field
        self.on_change = on_change
        self.value = value


    def to_dict(self):
        return {
            'type': 'select',
            'properties': {
                'name': self.name,
                'options': self.options,
                'multiple': self.multiple,
                'required': self.required,
                'placeholder': self.placeholder,
                'labelField': self.label_field,
                'valueField': self.value_field,
                'onChange': self.on_change,
                'value': self.value,
            },
        }

class Checkbox(Component):
    def __init__(self, name: str, label: Optional[str] = None, checked: bool = False):
        self.name = name
        self.label = label
        self.checked = checked

    def to_dict(self):
        return {
            'type': 'checkbox',
            'properties': {
                'name': self.name,
                'label': self.label,
                'checked': self.checked,
            },
        }

class Tabs(Component):
    def __init__(self, children: List['Tab']):
        self.children = children

    def to_dict(self):
        return {
            'type': 'tabs',
            'children': [child.to_dict() for child in self.children],
        }

class Tab(Component):
    def __init__(self, label: str, children: List[Component]):
        self.label = label
        self.children = children

    def to_dict(self):
        return {
            'type': 'tab',
            'properties': {
                'label': self.label,
            },
            'children': [child.to_dict() for child in self.children],
        }

class ModalDialog(Component):
    def __init__(
        self,
        name: str,
        title: str,
        content: List[Component],
        visible: bool = False,
        on_close: Optional[str] = None,
    ):
        self.name = name
        self.title = title
        self.content = content
        self.visible = visible
        self.on_close = on_close

    def to_dict(self):
        return {
            'type': 'modal-dialog',
            'properties': {
                'name': self.name,
                'title': self.title,
                'visible': self.visible,
                'onClose': self.on_close,
            },
            'children': [component.to_dict() for component in self.content],
        }

class Page(Component):
    def __init__(self, name: str, label: str, main: bool, path: str, components: List[Component], on_load: Optional[str] = None):
        self.name = name
        self.label = label
        self.main = main
        self.path = path
        self.components = components
        self.on_load = on_load

    def to_dict(self):
        return {
            'type': 'page',
            'properties': {
                'name': self.name,
                'path': self.path,
                'label': self.label,
                'main': self.main,
                'onLoad': self.on_load,
            },
            'children': [component.to_dict() for component in self.components],
        }

class Action:
    def __init__(
        self,
        action_type: str,
        method: str,
        url: Optional[str] = None,
        data: Optional[Any] = None,
        content_type: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        state: Optional[str] = None,
        before_action: Optional[str] = None,
        on_success: Optional[Any] = None,
        on_error: Optional[Any] = None,
        actions: Optional[List[Union['Action', str]]] = None,
    ):
        self.action_type = action_type
        self.method = method
        self.url = url
        self.data = data
        self.content_type = content_type
        self.params = params
        self.state = state
        self.before_action = before_action
        self.on_success = on_success
        self.on_error = on_error
        self.actions = actions or []

    def to_dict(self):
        return {
            'type': self.action_type,
            'method': self.method,
            'url': self.url,
            'data': self.data,
            'contentType': self.content_type,
            'params': self.params,
            'state': self.state,
            'beforeAction': self.before_action,
            'onSuccess': self.on_success,
            'onError': self.on_error,
            'actions': [action.to_dict() if isinstance(action, Action) else action for action in self.actions],
        }


class CustomInputOutputContent(Component):
    def __init__(
        self,        
        data_source: str,
        actions: Optional[List[Dict[str, Any]]] = None,
    ):        
        self.data_source = data_source
        self.actions = actions or []

    def to_dict(self):
        return {
            'type': 'custom-input-output-content',
            'properties': {                
                'dataSource': self.data_source,
                'actions': self.actions,
            },
        }

def render(
    layout: str,
    components: List[Component],
    actions: Optional[Dict[str, Action]] = None,
    initial_actions: Optional[List[str]] = None,
    pages: Optional[List['Page']] = None,
) -> Dict[str, Any]:
    render_def = {
        'layout': layout,
        'components': [component.to_dict() for component in components],
        'actions': {name: action.to_dict() for name, action in (actions or {}).items()},
        'initialActions': initial_actions or [],
    }
    if pages:
        render_def['pages'] = [page.to_dict() for page in pages]
    return render_def
