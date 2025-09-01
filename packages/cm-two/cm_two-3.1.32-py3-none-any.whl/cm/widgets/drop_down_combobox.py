import tkinter
from tkinter.ttk import Combobox
from traceback import format_exc
import platform


class AutocompleteCombobox(Combobox):
    def __init__(self, source_tablename=None, default_value=None, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.all_lists = []
        self.list_changed = False
        self.start_list = []
        self.default_value = default_value
        self.user_data = ''
        if platform.system() == "Windows":
            self.sys_keysym = "??"
        elif platform.system() == "Linux":
            self.sys_keysym = "U04"
        self.source_tablename = source_tablename
        if default_value:
            self.set_default_value()

    def set_alert(self):
        self.config({'show':"", 'highlightthickness':1, 'highlightcolor':'red'})

    def remove_alert(self):
        self.config({'highlightthickness': 0})

    def get_source_tablename(self):
        return self.source_tablename

    def set_default_value(self, *args, **kwargs):
        if self.default_value != None:
            self.set(self.default_value)

    def get(self, no_default=False, *args, **kwargs):
        value = super(AutocompleteCombobox, self).get()
        if no_default and value == self.default_value:
            return None
        else:
            return value

    def set_completion_list(self, completion_list):
        if not completion_list:
            completion_list = []
        self.initial_list = completion_list
        try:
            self._completion_list = sorted(
                completion_list, key=str.lower)  # Work with a sorted list
        except TypeError:
            self._completion_list = completion_list
        self.start_list = self._completion_list
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<Any-KeyRelease>', self.handle_keyrelease)
        self.bind('<Any-KeyPress>', self.handle_keypress)
        self['values'] = self._completion_list  # Setup our popup menu

    def clear(self):
        self.delete(0, "end")
        self['values'] = self.initial_list
        self.user_data = ''

    def check_element(self, get_value, element):
        get_value = get_value.lower()
        element = element.lower()
        if not get_value:
            return
        if get_value[0].isdigit():
            if len(get_value) > 2 and get_value in element:
                return True
        else:
            if element.startswith(get_value):
                return True
            if len(get_value) > 2 and get_value in element:
                return True

    def get_suggestions(self):
        value = self.user_data
        suggestions = []
        for item in self.initial_list:
            if self.check_element(value, item):
                suggestions.append(item)
        return suggestions

    def handle_keypress(self, event):
        if event.keysym == "BackSpace":
            if self.get() == self.user_data:
                od = self.user_data
                self.user_data = self.user_data[:-1]
                self.set(od)
            else:
                self.user_data = self.user_data[:-1]
                #self.set(self.user_data)
        else:
            self.user_data += event.char

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        if event.keysym in ("BackSpace", "Left", "Right", "Shift_R", "Shift_L"):
            return
        self.react(event)
        if not self.get():
            self.clear()

    def react(self, event):
        user_data_index = len(self.user_data)
        if not user_data_index:
            return
        suggestions = self.get_suggestions()
        self['values'] = suggestions
        if suggestions:
            self.set(suggestions[0])
            self.select_range(user_data_index, tkinter.END)
        else:
            self.no_suggestions()
        if not self.get():
            self.clear()

    def no_suggestions(self):
        self.set(self.user_data)

class AutocompleteComboboxCarNumber(AutocompleteCombobox):
    def __init__(self, source_tablename=None, default_value=None, *args,
                 **kwargs):
        super().__init__(source_tablename, default_value, *args, **kwargs)

    def check_element(self, get_value, element):
        get_value = get_value.lower()
        element = element.lower()
        if (element.startswith(
                get_value) or (
                get_value[0].isdigit() and len(
            get_value)) > 2 and get_value in element):
            return True

    #def no_suggestions(self):
    #    pass

def test(test_list):
    """Run a mini application to test the AutocompleteEntry Widget."""
    root = tkinter.Tk(className='AutocompleteCombobox')

    combo = AutocompleteCombobox(root)
    combo.set_completion_list(test_list)
    combo.pack()
    combo.focus_set()
    # I used a tiling WM with no controls, added a shortcut to quit
    root.bind('<Control-Q>', lambda event=None: root.destroy())
    root.bind('<Control-q>', lambda event=None: root.destroy())
    root.mainloop()


if __name__ == '__main__':
    test_list = ('АБВ', 'ВБС', 'Альянс групп', 'Юпитер', 'Озон',
                 'Тестовая организация', 'Soda', 'Strawberry', 'Башко',
                 'Башка', 'Башмо', 'Баштел', 'Башэн', 'Башорг')
    test(test_list)
