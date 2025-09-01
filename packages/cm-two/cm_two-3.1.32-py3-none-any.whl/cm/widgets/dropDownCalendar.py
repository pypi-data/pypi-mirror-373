import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import date


class MyDateEntry(DateEntry):
    def _setup_style(self, event=None):
        """Style configuration to make the DateEntry look like a Combobbox."""
        self.style.layout('DateEntry', self.style.layout('TCombobox'))
        self.update_idletasks()
        conf = self.style.configure('TCombobox')
        if conf:
            self.style.configure('DateEntry', **conf)
        maps = self.style.map('TCombobox')
        if maps:
            try:
                self.style.map('DateEntry', **maps)
            except tk.TclError:
                # temporary fix for issue #61 and https://bugs.python.org/issue38661
                return
        try:
            self.after_cancel(self._determine_downarrow_name_after_id)
        except ValueError:
            # nothing to cancel
            pass
        self._determine_downarrow_name_after_id = self.after(10,
                                                             self._determine_downarrow_name)

    def __init__(self, master=None, **kw):
        DateEntry.__init__(self, master=None, **kw)
        # add black border around drop-down calendar
        self._top_cal.configure(bg='black', bd=1)
        # add label displaying today's date below
        tk.Label(self._top_cal, bg='gray90', anchor='w',
                 text='Сегодня: %s' % date.today().strftime('%x')).pack(
            fill='x')
