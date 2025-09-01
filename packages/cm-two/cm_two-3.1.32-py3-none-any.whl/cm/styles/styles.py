from cm.styles import color_solutions as cs
from cm.styles import fonts
from tkinter.ttk import Style

treeviewfg = '#E2E2E2'
secondColor = '#2B5757'
grey_bg = cs.main_background_color
authWinColor = '#275050'
authWinColorDark = '#192121'

kpp_treeview_style = Style()
kpp_treeview_style.theme_use("clam")

kpp_treeview_style.layout("KPP.Treeview", [
    ("KPP.Treeview", {'sticky': 'nswe'}),
    ("KPP.Treeview", {'sticky': 'nswe', 'children': [
        ("KPP.Treeview", {'sticky': 'nswe', 'children': [
            ("KPP.Treeview", {'side': 'right', 'sticky': ''}),
            ("KPP.Treeview", {'sticky': 'we'}),
        ]})
    ]}),
])

kpp_treeview_style.configure("KPP.Treeview.Heading",
                             background=cs.treeview_bg_color,
                             foreground=cs.kpp_treeview_heading_color,
                             relief="flat",
                             font=fonts.kpp_treeview_heading,
                             fieldbackground=cs.treeview_bg_color, )
kpp_treeview_style.map("KPP.Treeview.Heading",
                       background=[('pressed', '#3E3E3E'),
                                   ('active', '#3E3E3E')]
                       )

kpp_treeview_style.configure("KPP.Treeview",
                             background=cs.treeview_bg_color,
                             foreground=cs.kpp_treeview_heading_color,
                             relief="flat",
                             font=fonts.kpp_treeview_content,
                             fieldbackground=cs.treeview_bg_color,
                             active='red', activebackground='red')
treviewStyle = Style()
treviewStyle.theme_use("clam")

treviewStyle.layout("Custom.Treeview", [
    ("Custom.Treeview", {'sticky': 'nswe'}),
    ("Custom.Treeview", {'sticky': 'nswe', 'children': [
        ("Custom.Treeview", {'sticky': 'nswe', 'children': [
            ("Custom.Treeview", {'side': 'right', 'sticky': ''}),
            ("Custom.Treeview", {'sticky': 'we'}),
        ]})
    ]}),
])

treviewStyle.configure("Custom.Treeview.Heading",
                       background=cs.treeview_bg_color, foreground=treeviewfg,
                       relief="flat",
                       font=fonts.main_tree_font,
                       fieldbackground=cs.treeview_bg_color, )
treviewStyle.map("Custom.Treeview.Heading",
                 background=[('pressed', '#3E3E3E'), ('active', '#3E3E3E')]
                 )

treviewStyle.configure("Custom.Treeview",
                       background=cs.treeview_bg_color, foreground=treeviewfg,
                       relief="flat",
                       font=fonts.main_tree_font,
                       fieldbackground=cs.treeview_bg_color,
                       active='red', activebackground='red')

historyTreeview = Style()
historyTreeview.theme_use("clam")
historyTreeview.layout("History.Treeview", [
    ("Custom.Treeview", {'sticky': 'nswe'}),
    ("Custom.Treeview", {'sticky': 'nswe', 'children': [
        ("Custom.Treeview", {'sticky': 'nswe', 'children': [
            ("Custom.Treeview", {'side': 'right', 'sticky': ''}),
            ("Custom.Treeview", {'sticky': 'we'}),
        ]})
    ]}),
])
historyTreeview.configure("History.Treeview.Heading",
                          background=cs.treeview_bg_color,
                          foreground=treeviewfg, relief="flat",
                          font=fonts.statistic_tree_font,
                          fieldbackground=cs.treeview_bg_color, )
historyTreeview.map("History.Treeview.Heading",
                    background=[('pressed', '#3E3E3E'), ('active', '#3E3E3E')]
                    )
historyTreeview.configure("History.Treeview",
                          background=cs.treeview_bg_color,
                          foreground=treeviewfg, relief="flat",
                          font=fonts.statistic_tree_font,
                          fieldbackground=cs.treeview_bg_color)

s = Style()
s.layout('statwin.TCombobox')
s.configure('statwin.TCombobox', fieldbackground=cs.statistic_win_bg_color,
            selectbackground=cs.statistic_win_bg_color,
            background=cs.statistic_win_bg_color,
            foreground=treeviewfg,
            darkcolor=cs.statistic_win_bg_color,
            bordercolor=cs.statistic_win_bg_color,
            lightcolor=cs.statistic_win_bg_color,
            arrowcolor=treeviewfg, relief="flat",
            font=fonts.statistic_tree_font,
            insertcolor=cs.orup_fg_color)

kpp_s = Style()
kpp_s.layout('kpp_filters.TCombobox')
kpp_s.configure('kpp_filters.TCombobox',
                fieldbackground=cs.statistic_win_bg_color,
                selectbackground=cs.statistic_win_bg_color,
                background=cs.statistic_win_bg_color,
                foreground=cs.kpp_filter_font,
                darkcolor=cs.statistic_win_bg_color,
                bordercolor=cs.statistic_win_bg_color,
                lightcolor=cs.statistic_win_bg_color,
                arrowcolor=cs.kpp_filter_font, relief="flat",
                font=fonts.kpp_filters,
                insertcolor=cs.orup_fg_color)

orupCombo = Style()
orupCombo.layout('orup.TCombobox')
orupCombo.configure('orup.TCombobox', fieldbackground=cs.orup_bg_color,
                    selectbackground=cs.orup_bg_color,
                    background=cs.orup_bg_color, foreground='#BABABA',
                    darkcolor=cs.orup_bg_color, bordercolor=cs.orup_bg_color,
                    lightcolor=cs.orup_bg_color,
                    arrowcolor='#BABABA', relief="flat",
                    font='"Montserrat SemiBold" 11',
                    insertcolor=cs.orup_fg_color, insertbackground='red')

statCombo = Style()
statCombo.layout('stat.TCombobox')
statCombo.configure('stat.TCombobox', fieldbackground=cs.treeview_bg_color,
                    selectbackground=cs.treeview_bg_color,
                    background=cs.treeview_bg_color, foreground='#E2E2E2',
                    darkcolor=cs.treeview_bg_color,
                    bordercolor=cs.treeview_bg_color,
                    lightcolor=cs.treeview_bg_color,
                    arrowcolor='#E2E2E2', relief="flat",
                    font='"Montserrat SemiBold" 11',
                    insertcolor=cs.treeview_bg_color, )

orupCombo.map('orup.TCombobox', fieldbackground=[('readonly', 'red')])
orupCombo.map('orup.TCombobox', selectbackground=[('readonly', 'red')])
# '*TCombobox*Listbox.background', 'yellow'
# orupCombo.map('orup.TCombobox', selectforeground=[('readonly', 'black')])


orupComboIncorrect = Style()
orupComboIncorrect.layout('orupIncorrect.TCombobox')
orupComboIncorrect.configure('orupIncorrect.TCombobox',
                             fieldbackground=cs.orup_bg_color,
                             selectbackground=cs.orup_bg_color,
                             background=cs.orup_bg_color, foreground='#BABABA',
                             darkcolor=cs.orup_bg_color,
                             bordercolor=cs.orup_bg_color, lightcolor='red',
                             arrowcolor=cs.orup_bg_color, relief="flat",
                             font='"Montserrat SemiBold" 11',
                             insertcolor='#BABABA')
# orupCombo.map('orup.TCombobox',
#    highlightthickness=[('incorrect',1), ('correct',0)],
#    highlightcolor=[('incorrect','red'), ('correct', cs.orup_bg_color)]
#    )


orupCombo = Style()
orupCombo.layout('authwin.TCombobox')
orupCombo.configure('authwin.TCombobox',
                    fieldbackground=cs.auth_background_color,
                    selectbackground=cs.auth_background_color,
                    background=cs.auth_background_color, foreground='#BABABA',
                    darkcolor=cs.auth_background_color,
                    bordercolor=cs.auth_background_color,
                    lightcolor=cs.auth_background_color,
                    arrowcolor=treeviewfg, relief="flat",
                    font='"Montserrat SemiBold" 11',
                    insertcolor='#BABABA')

toolbarBtn = Style()
toolbarBtn.layout('toolbarBtn.TButton')
toolbarBtn.configure('toolbarBtn.TButton', background=cs.treeview_bg_color,
                     borderwidth=0,
                     activeforeground='blue')
toolbarBtn.map("toolbarBtn.TButton",
               background=[('!active', cs.treeview_bg_color),
                           ('pressed', cs.treeview_bg_color),
                           ('active', cs.treeview_bg_color)]
               )

# 3D3D3D
onGreyBtn = Style()
onGreyBtn.layout('onGreyBtn.TButton')
onGreyBtn.configure('onGreyBtn.TButton', background=grey_bg,
                    highlightthickness=0, borderwidth=0, bd=0)
onGreyBtn.map("onGreyBtn.TButton",
              background=[('!active', grey_bg), ('pressed', grey_bg),
                          ('active', grey_bg)]
              )

onORUPbtn = Style()
onORUPbtn.layout('onORUPbtn.TButton')
onORUPbtn.configure('onORUPbtn.TButton', background=cs.orup_bg_color,
                    highlightthickness=0, borderwidth=0, bd=0)
onORUPbtn.map("onORUPbtn.TButton",
              background=[('!active', cs.orup_bg_color),
                          ('pressed', cs.orup_bg_color),
                          ('active', cs.orup_bg_color)]
              )

authWinBtn = Style()
authWinBtn.layout('authWinBtn.TButton')
authWinBtn.configure('authWinBtn.TButton', background=cs.auth_background_color,
                     highlightthickness=0, borderwidth=0, bd=0)
authWinBtn.map("authWinBtn.TButton",
               background=[('!active', cs.auth_background_color),
                           ('pressed', cs.auth_background_color),
                           ('active', cs.auth_background_color)]
               )

authWinBtnDark = Style()
authWinBtnDark.layout('authWinBtnDark.TButton')
authWinBtnDark.configure('authWinBtnDark.TButton', background=authWinColorDark,
                         highlightthickness=0, borderwidth=0, bd=0)
authWinBtnDark.map("authWinBtnDark.TButton",
                   background=[('!active', authWinColorDark),
                               ('pressed', authWinColorDark),
                               ('active', authWinColorDark)]
                   )

check_orup = Style()
check_orup.layout('check_orup.TCheckbutton')
check_orup.configure('check_orup.TCheckbutton', background=cs.orup_bg_color,
                     highlightthickness=0, borderwidth=0, border=0)
check_orup.map("check_orup.TCheckbutton",
               background=[('!active', cs.orup_bg_color),
                           ('pressed', cs.orup_bg_color),
                           ('active', cs.orup_bg_color)]
               )

sepStyle = Style()
sepStyle.layout('TSeparator')
sepStyle.configure('TSeparator', background='#246969')
