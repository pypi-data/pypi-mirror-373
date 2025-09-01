from tkinter import StringVar

from cm.pages.superpage import SuperPage
from cm.styles import element_sizes as el_sizes, color_solutions as cs
from cm.widgets.drop_down_combobox import AutocompleteCombobox
from cm.widgets.password_entry import PasswordEntry


class AuthWin(SuperPage):
    '''Окно авторизации'''

    def __init__(self, root, settings, operator, can):
        super(AuthWin, self).__init__(root, settings, operator, can)
        self.name = 'AuthWin'
        self.buttons = settings.authBtns
        self.right_corner_sys_buttons_objs = self.create_btns_and_hide([
            self.settings.minimize_btn, self.settings.exitBtnAuth])
        self.s = settings
        self.r = root
        self.currentUser = 'Андрей'
        self.font = '"Montserrat Regular" 14'
        self.page_buttons = self.create_btns_and_hide(self.buttons)

    def send_auth_command(self):
        """ Отправить команду на авторизацию """
        pw = self.auth_page_password_entry.get()
        login = self.auth_page_login_var.get()
        self.operator.ar_qdk.try_auth_user(username=login, password=pw)
        self.currentUser = login

    def createPasswordEntry(self):
        var = StringVar(self.r)
        pwEntry = PasswordEntry(self.r, border=0,
                                width=
                                el_sizes.entrys['authwin.password'][
                                    self.screensize][
                                    'width'],
                                textvariable=var, bg=cs.auth_background_color,
                                font=self.font, fg='#BABABA',
                                insertbackground='#BABABA',
                                highlightthickness=0)
        return pwEntry

    def incorrect_login_act(self):
        self.auth_page_password_entry.incorrect_login_act()

    def get_login_type_cb(self):
        self.auth_page_login_var = StringVar()
        self.usersComboBox = AutocompleteCombobox(self.root,
                                                  textvariable=self.auth_page_login_var)
        self.usersComboBox['style'] = 'authwin.TCombobox'
        self.configure_combobox(self.usersComboBox)
        users = self.operator.get_users_reprs()
        self.usersComboBox.set_completion_list(users)
        if len(users) == 1:
            self.usersComboBox.set(users[0])
        self.usersComboBox.config(
            width=el_sizes.comboboxes['authwin.login'][self.screensize][
                'width'],
            height=el_sizes.comboboxes['authwin.login'][self.screensize][
                'height'],
            font=self.font)
        self.usersComboBox.bind('<Return>',
                                lambda event: self.send_auth_command())
        return self.usersComboBox

    def rebinding(self):
        self.usersComboBox.unbind('<Return>')
        self.auth_page_password_entry.unbind('<Return>')
        self.bindArrows()

    def drawing(self):
        super().drawing(self)
        self.create_auth_entries()
        self.drawSlices(mode=self.name)

    def create_auth_entries(self):
        self.auth_page_password_entry = self.createPasswordEntry()
        self.auth_page_password_entry.bind('<Return>', lambda
            event: self.send_auth_command())
        self.usersChooseMenu = self.get_login_type_cb()
        self.can.create_window(self.s.w / 2, self.s.h / 1.61,
                               window=self.auth_page_password_entry,
                               tags=('maincanv', 'pw_win'))
        self.can.create_window(self.s.w / 2, self.s.h / 1.96,
                               window=self.usersChooseMenu, tag='maincanv')

    def initBlockImg(self, name, btnsname=None, slice='shadow', mode='new',
                     seconds=[], hide_widgets=[], picture=None, **kwargs):
        super(AuthWin, self).initBlockImg(name, btnsname)
        self.auth_page_password_entry.lower()
        self.usersChooseMenu.lower()
        self.hide_buttons(self.page_buttons)

    def destroyBlockImg(self, mode='total'):
        super(AuthWin, self).destroyBlockImg()
        self.auth_page_password_entry.lift()
        self.usersChooseMenu.lift()
        self.show_buttons(self.page_buttons)

    def openWin(self):
        super(AuthWin, self).openWin()
        self.drawWin('maincanv', 'start_background', 'login', 'password')
        # self.hide_buttons(self.right_corner_sys_buttons_objs)
        self.can.delete("clockel")
        self.can.itemconfigure('btn', state='hidden')
        self.auth_page_password_entry.config(show='\u2022',
                                             highlightthickness=0)

    def page_close_operations(self):
        super(AuthWin, self).page_close_operations()
        self.can.itemconfigure('btn', state='normal')
