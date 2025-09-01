from tkinter import Entry, END


class PasswordEntry(Entry):
    def __init__(self, *args, **kwargs):
        super(PasswordEntry, self).__init__(show='\u2022', *args, **kwargs)
        self.bind("<Button-1>", self.on_click)
        self.bind("<BackSpace>", self.on_click)

    def on_click(self, event):
        event.widget.delete(0, END)
        self.config(show='\u2022')

    def incorrect_login_act(self, error_text="Неправильный пароль!"):
        self.config(show="", highlightthickness=1, highlightcolor='red')
        self.delete(0, END)
        self.insert(END, error_text)

