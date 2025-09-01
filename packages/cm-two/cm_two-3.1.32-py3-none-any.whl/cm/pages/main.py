import threading

from gtki_module_treeview.main import CurrentTreeview

from cm.pages.superpage import SuperPage
from cm.styles import fonts, color_solutions as cs


class MainPage(SuperPage):
    def __init__(self, root, settings, operator, can):
        super(MainPage, self).__init__(root, settings, operator, can)
        self.name = 'MainPage'
        self.buttons = settings.gateBtns + settings.manual_gate_control_btn
        self.barriers = {}
        self.count = 0
        self.orupState = False
        self.errorShown = False
        self.chosenTrashCat = 'deff'
        self.tree = self.create_tree()
        self.win_widgets.append(self.tree)
        self.btn_name = self.settings.mainLogoBtn
        self.make_abort_unactive()
        self.page_buttons = self.create_btns_and_hide(self.buttons)
        self.cameras = ["auto_exit", "cad_gross", "main"]


    def cam_zoom_callback(self, cam_type=None):
        self.tree.lower()
        self.abort_round_btn.lower()
        super(MainPage, self).cam_zoom_callback(cam_type)
        self.hide_widgets(self.hide_while_cam_zoom_widgets)

    def cam_hide_callback(self, cam_type=None):
        super(MainPage, self).cam_hide_callback(cam_type)
        self.operator.turn_cams()
        self.operator.currentPage.abort_round_btn.lift()
        self.operator.currentPage.tree.lift()

    def draw_set_arrow(self, arrow_attr, *args, **kwargs):
        if (
                self.operator.current == 'MainPage' or self.operator.current == 'ManualGateControl') and \
                self.operator.currentPage.blockImgDrawn == False:
            super().draw_set_arrow(arrow_attr, *args, **kwargs)

    def create_tree(self):
        self.tar = CurrentTreeview(self.root, self.operator, height=18)
        self.tar.createTree()
        self.tree = self.tar.get_tree()
        self.tree.bind("<Double-Button-1>", self.OnDoubleClick)
        return self.tree

    def rebind_btns_after_orup_close(self):
        self.tree.bind("<Double-Button-1>", self.OnDoubleClick)

    def create_abort_round_btn(self):
        self.can.create_window(self.settings.abort_round[0][1],
                               self.settings.abort_round[0][2],
                               window=self.abort_round_btn,
                               tag='winBtn')

    def make_abort_active(self):
        btn = self.abort_round_btn
        btn['state'] = 'normal'

    def make_abort_unactive(self):
        btn = self.abort_round_btn
        btn['state'] = 'disabled'

    def drawMainTree(self):
        self.operator.ar_qdk.get_unfinished_records()
        self.can.create_window(self.w / 1.495, self.h / 2.8, window=self.tree,
                               tag='tree')
        # self.tar.sortId(self.tree, '#0', reverse=True)

    def fill_current_treeview(self, info):
        """
        Обновляет ttk.Treeview без мерцания.
        • Не прячет виджет (нет lower/lift)
        • Не очищает полностью (нет clearTree)
        • Обновляет/добавляет/удаляет только затронутые строки
        """
        tree = self.tree
        fmt_date = self.tar.getFrmtDate  # ← берём форматтер там же, где fillTree
        existing = set(tree.get_children())  # iids уже в таблице
        processed = set()
        first_even = False  # для тега ('evenrow',)
        #tree.lift()
        for rec in info:
            act_id = int(rec['act_number']) if rec['package_id'] else rec['id']
            iid = str(rec['id'])  # treeview.iid должен быть строкой

            # подготовка значений — те же, что fillTree запишет
            trash_cat = self.operator.get_trash_cat_repr(rec['trash_cat'])
            values = (
                fmt_date(rec['time_in'] or '-'),
                rec['brutto'] if rec['brutto'] is not None else '-',
                rec['tara'] if rec['tara'] is not None else '-',
                rec['cargo'] if rec['cargo'] is not None else '-',
                trash_cat,
                rec['car_number'],
                rec['full_notes'],
            )
            tags = () if (not rec['time_out'] or first_even) else ('evenrow',)
            if tags:
                first_even = True

            if iid in existing:
                # 1) строка уже есть — обновляем только если что-то изменилось
                item = tree.item(iid)
                if item["text"] != act_id or item["values"] != values \
                        or set(item["tags"]) != set(tags):
                    tree.item(iid, text=act_id, values=values, tags=tags)
            else:
                # 2) новой строки нет — добавляем через прежний fillTree
                self.tar.fillTree(id=act_id,
                                  brutto=rec['brutto'],
                                  tara=rec['tara'],
                                  cargo=rec['cargo'],
                                  time_in=rec['time_in'],
                                  trash_cat=trash_cat,
                                  car_number=rec['car_number'],
                                  notes=rec['full_notes'],
                                  tags=tags,
                                  record_id=rec['id'])

            processed.add(iid)

        # 3) удаляем строки, которых больше нет в info
        for iid in existing - processed:
            tree.delete(iid)

        # 4) сортировка остаётся прежней
        self.tar.sortId(tree, '#0', reverse=True)

    def drawing(self):
        super().drawing(self)
        self.operator.ar_qdk.get_status()
        self.drawMainTree()
        self.drawWin('win', 'road', 'order', 'currentEvents',
                     'entry_gate_base', 'exit_gate_base')

    def drawRegWin(self):
        self.draw_block_win(self, 'regwin')

    def updateTree(self):
        self.operator.ar_qdk.get_unfinished_records()

    def OnDoubleClick(self, event):
        """ Реакция на дабл-клик по текущему заезду """
        self.record_id = self.tree.selection()[0]
        self.chosenStr = self.tree.item(self.record_id, "values")
        if self.chosenStr[2] == '-':
            self.draw_rec_close_win()
        else:
            self.draw_cancel_tare()

    def draw_rec_close_win(self):
        btnsname = 'closeRecBtns'
        self.initBlockImg(name='ensureCloseRec', btnsname=btnsname,
                          seconds=('second'),
                          hide_widgets=self.win_widgets)
        self.root.bind('<Return>', lambda event: self.operator.close_record(
            self.record_id))
        self.root.bind('<Escape>',
                       lambda event: self.destroyBlockImg(mode="total"))

    def operate_new_plate_recognition_trying(self, current_try, max_tries,
                                             side):
        # self.can.delete("plate_recognise_status")
        text = f"Пытаемся распознать... ({current_try}/{max_tries})"
        if side == "external":
            camera_type = "kpp_cam_external"
            tag = "plate_recognise_status_external"
            self.can.delete("cad_color_external")
        else:
            camera_type = "kpp_cam_internal"
            tag = "plate_recognise_status_internal"
            self.can.delete("cad_color_internal")
        camera_inst = self.operator.get_camera_inst(camera_type)
        if not camera_inst:
            return
        x = camera_inst.place_x
        y = camera_inst.place_y - camera_inst.video_height / 2.5  # Что бы текст был над видео
        self.can.delete(tag)
        if (self.blockImgDrawn and not self.orupState) or self.cam_zoom:
            return
        self.can.create_text(
            x, y, text=text, font=fonts.cad_work_font,
            fill=cs.orup_fg_color, tags=(tag,))
        threading.Thread(
            target=self.operator.tag_timeout_deleter, args=(tag, 4), daemon=True).start()


    def draw_cancel_tare(self):
        btnsname = 'cancel_tare_btns'
        self.initBlockImg(name='cancel_tare', btnsname=btnsname,
                          seconds=('second'),
                          hide_widgets=self.win_widgets)
        self.root.bind('<Escape>',
                       lambda event: self.destroyBlockImg(mode="total"))

    def initBlockImg(self, name, btnsname=None, slice='shadow', mode='new',
                     seconds=[], hide_widgets=[], picture=None, **kwargs):
        super(MainPage, self).initBlockImg(name, btnsname)
        self.hide_widgets(self.page_buttons)
        self.hide_main_navbar_btns()

    def place_car_detect_text(self, side_name):
        self.operator.place_car_detect_text(
            side_name,
            self.operator.cam_meta["cad_gross"]["xpos"],
            self.operator.cam_meta["cad_gross"]["ypos"],
            self.operator.cam_meta["auto_exit"]["xpos"],
            self.operator.cam_meta["auto_exit"]["ypos"],
            self.operator.cam_meta["auto_exit"]["v_width"],
            self.operator.cam_meta["auto_exit"]["v_height"],
        )

    def destroyBlockImg(self, mode='total'):
        super(MainPage, self).destroyBlockImg()
        self.drawMainTree()
        self.show_main_navbar_btns()
        self.show_time()
        self.draw_weight()
        self.abort_round_btn.lift()
        self.operator.draw_road_anim()
        self.operator.turn_cams(True)
        self.tree.lift()

    def openWin(self):
        super(MainPage, self).openWin()
        # cams_zoom = [cam['name']+cam['zoom'] for cam in self.operator.cameras_info]
        if not self.cam_zoom:
            self.hide_zoomed_cam(True)
        # self.operator.turn_cams(True)
        # self.operator.ar_qdk.execute_method("get_gates_states")
        self.operator.draw_road_anim()
        self.draw_gate_arrows()
        self.draw_weight()
        self.abort_round_btn.lift()
        self.create_abort_round_btn()
        self.show_main_navbar_btns()
        self.turn_on_cameras()

    def page_close_operations(self):
        super(MainPage, self).page_close_operations()
        self.can.delete('win', 'statusel', 'tree', 'road', 'order',
                        'currentEvents', 'entry_gate_base', 'exit_gate_base',
                        "car_icon")
        self.operator.turn_cams(False)
        self.abort_round_btn.lower()
        self.unbindArrows()
        self.hide_main_navbar_btns()
        self.hide_weight()
