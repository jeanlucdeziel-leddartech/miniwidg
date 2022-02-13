import tkinter as tk
from tkinter import ttk
from typing import Optional, Any, List, Callable, Tuple
from pynput import keyboard


class ControlPanel(tk.Frame):

    def __init__(self, title:str='Control', offset:Tuple[int, int]=(0,0)):

        master = tk.Tk()
        super().__init__(master)
        master.title(title)
        master.geometry(f"+{offset[0]}+{offset[1]}")
        self.master = master
        self.title = title
        self.grid()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.parent = None

        self.widgets = {}
        self.containers = {}


    def add_exit_callback(self, func:callable):
        self.master.protocol("WM_DELETE_WINDOW", func)


    def __set_widget_position(self, widget:tk.Widget):
        widget.grid(sticky=tk.NSEW)

        for container in self.containers.values():
            if container['open']:
                container['childs'].append(widget)


    def __add_hotkey(self, key:str, widget:tk.Widget):

        if not hasattr(self, 'hotkeys'):
            self.hotkeys = KeyboardHotkeys()

        self.hotkeys.bindings[key] = [False, widget]


    def update(self) -> None:

        if len(self.widgets) == 0:
            self.master.destroy()
            return

        for name in self.containers:
            if not self.containers[name]['initialized']:
                self.widgets[name].invoke()
                self.widgets[name].invoke()
                self.containers[name]['initialized'] = True
                
        if hasattr(self, 'hotkeys'):
            for _, binding in self.hotkeys.bindings.items():
                if binding[0]:
                    binding[1].invoke()
                    binding[0] = False

        return super().update()


    def create_button(self, name:str, callback:Optional[Callable[[],None]]=None, hotkey:str=None):

        self.widgets[name] = tk.Button(self, command=callback)
        self.widgets[name]["text"] = name

        self.__set_widget_position(self.widgets[name])

        if hotkey is not None:
            self.__add_hotkey(hotkey, self.widgets[name])
            self.widgets[name]["text"] = f'{name} ({hotkey})'


    def create_check_button(self, name:str, default:bool=False, callback:Optional[Callable[[bool],None]]=None, hotkey:str=None):

        self.widgets[name] = ttk.Checkbutton(self)
        self.widgets[name]["text"] = name
        self.__set_widget_position(self.widgets[name])

        self.widgets[name].invoke()
        if not default: self.widgets[name].invoke()

        if callback is not None:
            self.widgets[name]["command"] = lambda: callback(self.get_state(name))

        if hotkey is not None:
            self.__add_hotkey(hotkey, self.widgets[name])
            self.widgets[name]["text"] = f'{name} ({hotkey})'


    def create_menu(self, name:str, choices:List[Any], callback:Optional[Callable[[Any],None]]=None):

        self.widgets[f'{name}_variable'] = tk.StringVar(self)
        self.widgets[f'{name}_variable'].set(choices[0]) # default value

        self.__set_widget_position(tk.Label(self, text=name))

        self.widgets[name] = tk.OptionMenu(self, self.widgets[f'{name}_variable'], *choices, command=callback)

        self.__set_widget_position(self.widgets[name])

    
    def create_slider(self, name:str, start:float=0.0, end:float=1.0, step:float=0.01, default:float=None, show_value:bool=True, callback:Optional[Callable[[Any],None]]=None):
        
        self.widgets[name] = tk.Scale(self, label=name, from_=start, to=end, resolution=step, orient=tk.HORIZONTAL, showvalue=show_value, command=callback)

        default = start if default is None else default
        self.widgets[name].set(default)

        self.__set_widget_position(self.widgets[name])


    def start_container(self, name:str, default:bool=False):
        self.create_check_button(name, default)
        self.containers[name] = {'open': True, 'childs': [], 'default': default, 'initialized': False}


    def end_container(self, name:str):
        self.containers[name]['open'] = False

        def toggle(state):
            for child in self.containers[name]['childs']:
                if state: child.grid()
                else: child.grid_remove()
        
        self.widgets[name]['command'] = lambda: toggle(self.get_state(name))


    def add_separator(self):
        separator = ttk.Separator(self, orient='horizontal')
        self.__set_widget_position(separator)


    def get_state(self, name:str) -> Any:

        try:
            widget = self.widgets[name]
        except KeyError:
            raise KeyError(f"The widget with name '{name}' does not exist.")

        if isinstance(widget, ttk.Checkbutton):
            return widget.instate(['selected'])

        elif isinstance(widget, tk.OptionMenu):
            return self.widgets[f'{name}_variable'].get()

        elif isinstance(widget, tk.Scale):
            return widget.get()
            
        raise NotImplementedError


    def attach(self, other:'ControlPanel'):
        other.parent = self
        other.hide()

        def toggle(state):
            if state: other.unhide()
            else: other.hide()

        self.create_check_button(other.title)
        self.widgets[other.title]['command'] = lambda: toggle(self.get_state(other.title))


    def hide(self):
        self.master.withdraw()

    def unhide(self):
        self.master.deiconify()

    def on_closing(self):
        if self.parent:
            self.parent.widgets[self.title].state(['!selected'])
        self.hide()


class KeyboardHotkeys:

    def __init__(self):

        self.bindings = {}

        self.keyboard_listener = keyboard.Listener(on_press=self.__on_key_press)
        self.keyboard_listener.start()

    def __on_key_press(self, key:keyboard.KeyCode):
        
        if not isinstance(key, keyboard.KeyCode):
            return

        if key.char in self.bindings:
            self.bindings[key.char][0] = True