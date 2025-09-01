from cm.pages.superpage import SuperPage


class ManualGateControl(SuperPage):
    def __init__(self, root, settings, operator, can):
        super(ManualGateControl, self).__init__(root, settings, operator, can)
        self.name = 'ManualGateControl'
        self.buttons = self.settings.auto_gate_control_btn + self.settings.manual_open_internal_gate_btn + self.settings.manual_close_internal_gate_btn + \
                       self.settings.manual_open_external_gate_btn + self.settings.manual_close_external_gate_btn + self.settings.null_weight_btn
        self.btn_name = self.settings.mainLogoBtn
        self.external_gate_state = 'close'
        self.enternal_gate_state = 'close'
        self.page_buttons = self.create_btns_and_hide(self.buttons)
        self.cameras = ["auto_exit", "cad_gross"]

    def draw_set_arrow(self, arrow_attr, *args, **kwargs):
        if (
                self.operator.current == 'MainPage' or self.operator.current == 'ManualGateControl') and \
                self.operator.currentPage.blurDrawn == False:
            super().draw_set_arrow(arrow_attr, *args, **kwargs)

    def drawing(self):
        super().drawing(self)
        self.drawWin('maincanv', 'road', 'manual_control_info_bar',
                     'entry_gate_base', 'exit_gate_base')

    def initBlockImg(self, name, btnsname=None, slice='shadow', mode='new',
                     seconds=[], hide_widgets=[], picture=None, **kwargs):
        super(ManualGateControl, self).initBlockImg(name, btnsname)
        self.hide_buttons(self.page_buttons)
        self.hide_main_navbar_btns()

    def destroyBlockImg(self, mode='total'):
        super(ManualGateControl, self).destroyBlockImg()
        self.show_time()
        self.show_buttons(self.page_buttons)
        self.show_main_navbar_btns()

    def openWin(self):
        super(ManualGateControl, self).openWin()
        self.operator.draw_road_anim()
        self.draw_gate_arrows()
        self.draw_weight()
        self.root.bind('<Escape>',
                       lambda event: self.operator.mainPage.openWin())
        self.show_main_navbar_btns()

    def page_close_operations(self):
        super(ManualGateControl, self).page_close_operations()
        self.root.unbind("Escape")
        self.can.delete('win', 'statusel', 'tree')
        self.hide_main_navbar_btns()
