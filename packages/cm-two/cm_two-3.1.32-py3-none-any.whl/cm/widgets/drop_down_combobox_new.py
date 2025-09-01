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
            #self.set_completion_list_demo()

    def get(self, no_default=False, *args, **kwargs):
        """ Если включен режим no_default, будет возвращаться None, если значение Comobobox остался по умолчанию """
        value = super(AutocompleteCombobox, self).get()
        if no_default and value == self.default_value:
            return None
        else:
            return value

    def set_completion_list(self, completion_list):
        """Use our completion list as our drop down selection menu, arrows move through menu."""
        self.initial_list = completion_list
        self._completion_list = sorted(completion_list,
                                       key=str.lower)  # Work with a sorted list
        self.start_list = self._completion_list
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<Any-KeyRelease>', self.handle_keyrelease)
        self.bind('<Any-KeyPress>', self.handle_keypress)
        self['values'] = self._completion_list  # Setup our popup menu

    def handle_keypress(self, event):
        if event.keysym == "BackSpace":
            self.user_data = self.user_data[:-1]
        else:
            self.user_data += event.char

    def clear(self):
        self.delete(0, "end")
        self['values'] = self.start_list
        self.user_data = ''

    def set_completion_list_demo(self, completion_list=None):
        """Обновить список значений"""
        value = self.get()
        if not completion_list:
            completion_list = self.start_list
            self._hits = []
            self._hit_index = 0
            self.position = 0
            self.user_data = ''
        if value == '':
            self['values'] = completion_list
        else:
            data = []
            for item in completion_list:
                if value.lower() in item.lower():
                    data.append(item)
            self['values'] = data
        self.select_range(self.position, tkinter.END)

    def check_element(self, get_value, element):
        if (element.lower().startswith(get_value) or (len(
            get_value)) > 2 and get_value in element.lower()):
            return True

    def autocomplete(self, event, delta=0):
        if delta:  # need to delete selection otherwise we would fix the current position
            self.delete(self.position, tkinter.END)
        else:  # set position to end so selection starts where textentry ended
            self.position = len(self.get())
        # collect hits
        _hits = []
        #print(f"ALL {self.all_lists}")
        #print(f"SEARCHING {self.get()} in {self._completion_list}")
        get_value = self.get().lower()
        for element in self._completion_list:
            if self.check_element(get_value, element):
                _hits.append(element)
        if not self.list_changed:
            self.start_list = self._completion_list
            self.list_changed = True
        self.all_lists.append(self._completion_list)
        #print("ALL_LISTS", self.all_lists)
        if len(_hits) > 0:
            self.set_completion_list_demo(_hits)
        # if we have a new hit list, keep this in mind
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        # only allow cycling if we are in a known hit list
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        # now finally perform the auto completion
        if self._hits:
            self.delete(0, tkinter.END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, tkinter.END)
        elif self.user_data != self.get():
            #print("SELF.GET", self.get())
            self.set(self.user_data)
        #else:
            #print("TT18")
            #print(dir(event))
            #self.user_data = self.get()
            #print("USER DATA", self.user_data)
        #print("ANYWAY USER_DATA", self.user_data)

    def handle_keyrelease(self, event):
        """event handler for the keyrelease event on this widget"""
        self.prev_index = self.position
        if event.keysym == "BackSpace":
            self.delete(self.index(tkinter.INSERT), tkinter.END)
            #self.user_data = self.user_data[:-1]
            self.position = self.index(tkinter.END)
            if self.position == 0:
                self.set_completion_list_demo(self.start_list)
            if self.position==self.prev_index:
                return
            try:
                self.set_completion_list_demo(self.all_lists.pop(-1))
            except IndexError:
                self.set_completion_list_demo(self.start_list)
            #if self.position < self.index(tkinter.END):  # delete
        if event.keysym == "Left":
           # self.user_data = self.user_data[:-1] the selection
           #     self.delete(self.position, tkinter.END)
           # else:
                self.position = self.position - 1  # delete one character
                #self.delete(self.position, tkinter.END)
        if event.keysym == "Right":
            self.position = self.index(tkinter.END)  # go to end (no selection)
        if (event.keysym == '??' or len(event.keysym)) == 1 or (platform.system() == "Linux" and event.keysym.startswith("U04")):
            self.autocomplete(event)
        #elif platform.system() == "Linux" and self.sys_keysym in event.keysym:
        #    self.autocomplete(event)
        #if not self.get():
        #    self.user_data = ''
        # No need for up/down, we'll jump to the popup
        # list at the position of the autocompletion

class AutocompleteComboboxCarNumber(AutocompleteCombobox):
    def __init__(self, source_tablename=None, default_value=None, *args,
                 **kwargs):
        super().__init__(source_tablename, default_value, *args, **kwargs)

    def check_element(self, get_value, element):
        if (element.lower().startswith(
                get_value) or (
                get_value[0].isdigit() and len(
            get_value)) > 2 and get_value in element.lower()):
            return True

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
