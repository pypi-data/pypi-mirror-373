import datetime
import re
import threading
import PIL
import time
from tkinter import StringVar, END

from Cython.Compiler.Naming import self_cname
from gtki_module_treeview.main import KPPTreeview
from cm.pages.superpage import SuperPage
from cm.styles import fonts, color_solutions as cs
from cm.widgets.dropDownCalendar import MyDateEntry
from cm.widgets.drop_down_combobox import AutocompleteComboboxCarNumber, \
    AutocompleteCombobox


class KPP(SuperPage):
    def __init__(self, root, settings, operator, can):
        super(KPP, self).__init__(root, settings, operator, can)
        self.name = 'KPP'
        self.status = {}
        self.chosen_arrival_id = None
        self.kpp_pass_win_opened = False
        self.chosen_arrival = None
        self.kpp_info = {}
        self.ok_btn = self.create_button_and_hide(self.settings.kpp_ok_btn)
        self.abort_btn = self.create_button_and_hide(
            self.settings.kpp_abort_btn)
        self.break_recognition_btn = self.create_button_and_hide(
            self.settings.kpp_break_recognistion_btn)
        self.kpp_lift_up_btn = self.create_button_and_hide(
            self.settings.kpp_lift_up_btn)
        self.kpp_lift_down_btn = self.create_button_and_hide(
            self.settings.kpp_lift_down_btn)
        self.other_footer_btns = self.create_btns_and_hide(
            self.settings.kpp_internal_btn + self.settings.kpp_external_btn)
        self.other_footer_btns.append(self.kpp_lift_up_btn)
        self.other_footer_btns.append(self.kpp_lift_down_btn)
        self.page_buttons = [self.ok_btn,
                             self.abort_btn] + self.other_footer_btns
        self.btn_name = self.settings.kpp_icon
        self.gate_state = 'close'
        self.arrivals = []
        self.plase_kpp_tree_btns()
        self.tree = self.create_tree()
        self.draw_elements = ["kpp_road", "kpp_main_background",
                              "kpp_barrier_base"]
        self.barriers = {"kpp_barrier":
                             {"tags": [],
                              "pos": 80, "img": ...,
                              "img_obj": ...,
                              "settings_object": "kpp_barrier_base"}}
        if "kpp_barrier_arrow" not in self.operator.road_anim_info:
            self.operator.road_anim_info["kpp_barrier_arrow"] = {
                "img_id": None,
                "img_tag": "kpp_barrier_arrow",
                "busy": False,
                "pos": 0  # начальная позиция стрелки
            }
        self.info = {}
        # self.cameras = {"external": {},
        #                "internal": {}}
        self.kpp_get_info()
        self.kpp_preloader_tags = ["foo", "bar"]
        self.kpp_preloader_img = PIL.Image.open(
            self.settings.imgsysdir + 'kpp_preloader_img.png')
        self.plate_recognition_in_progress = False
        self.kpp_success_recognition = PIL.ImageTk.PhotoImage(PIL.Image.open(
            self.settings.imgsysdir + 'kpp_recognition_success.png'))
        self.kpp_failed_recognition = PIL.ImageTk.PhotoImage(PIL.Image.open(
            self.settings.imgsysdir + 'kpp_recognition_failed.png'))
        self.close_arrival_without_pass_out = False
        self.pass_out_without_time_in = False
        self.hide_while_cam_zoom_widgets = []
        self.arriving_in_progress = False
        self.hide_kpp_tree_btns()
        self.cameras = ["kpp_cam_external", "kpp_cam_internal"]
        self.abort_photocell_waiting_btn = self.create_button_and_hide(
            self.settings.kpp_abort_photocell_waiting)

    # def set_kpp_lift_btn(self):
    #    barrier_is_open = self.operator.barrier_states["kpp_barrier"]["open"]
    #    self.show_lift_btn("down")
    #    else:
    #        self.show_lift_btn("up")

    def show_lift_btn(self, type: str):
        if type == "up":
            self.kpp_lift_down_btn.lower()
            self.kpp_lift_up_btn.lift()
        else:
            self.kpp_lift_down_btn.lift()
            self.kpp_lift_up_btn.lower()

    def show_gate_open_status(self):
        self.set_arriving_status(
            text="Шлагбаум открыт",
            tags=("kpp_status", "arriving_in_progress"))

    def get_kpp_status(self):
        self.operator.ar_qdk.execute_method("get_kpp_status")

    def lift_up_btn(self):
        if self.check_kpp_busy():
            return
        # Логгировать нажатие
        if self.kpp_info["recognise"]:
            self.initBlockImg("kpp_lift_up_win", "kpp_lift_up_win_btns")
            self.root.bind('<Return>', lambda event: self.send_auth_lift_up())
            self.root.bind('<Escape>', lambda event: self.destroyBlockImg())
            self.turn_on_cameras()
        else:
            self.operator.ar_qdk.execute_method("kpp_lift_up")
            self.show_lift_btn("down")

    def lift_down_btn(self):
        if self.status["arrival_in_progress"]:
            self.trying_start_new_arrival_while_current(
                text="Ожидается проезд авто",
                tags=("kpp_status", "arrival_in_progress"))
            return
        self.operator.ar_qdk.execute_method("kpp_lift_down")
        #self.show_lift_btn("up")

    def send_auth_lift_up(self):
        self.operator.ar_qdk.execute_method("kpp_lift_up")
        self.destroyBlockImg()
        self.show_lift_btn("down")
        # self.show_lift_btn("down")
        # password = self.kpp_password_entry.get()
        # self.operator.ar_qdk.execute_method(
        #    "kpp_send_auth_lift_up",
        #    username=self.operator.username, password=password)

    def lets_recognise(self, side_name):
        self.operator.ar_qdk.execute_method("kpp_lets_recognise",
                                            side_name=side_name)

    def lift_up_auth_success(self, username):
        self.destroyBlockImg()
        self.hide_kpp_tree_btns()
        self.operator.kpp_lift_page.openWin()

    def lift_up_incorrect_password(self):
        self.kpp_password_entry.incorrect_login_act(
            f"Неправильный пароль для {self.operator.username}")

    def trying_start_new_arrival_while_current(self, text, tags):
        threading.Thread(target=self.kpp_arriving_attention_thread,
                         kwargs={"text": text, "tags": tags},
                         daemon=True).start()

    def kpp_arriving_attention_thread(
            self, text="Ожидается проезд авто", tags=("kpp_status",)):
        init_font = fonts.kpp_status
        init_font_size = int(re.findall(r'\d+', init_font)[0])
        current_font_size = init_font_size
        max_font = 18
        anim_speed = 0.02
        font_animation_speed = 1
        color = "#F0B33E"
        while current_font_size < max_font:
            new_font = init_font.replace(
                str(init_font_size), str(current_font_size))
            current_font_size += font_animation_speed
            self.set_arriving_status(
                font=new_font, fill=color, text=text, tags=tags)
            time.sleep(anim_speed)
        while current_font_size != init_font_size:
            new_font = init_font.replace(
                str(init_font_size), str(current_font_size))
            current_font_size -= font_animation_speed
            self.set_arriving_status(
                font=new_font, fill=color, text=text, tags=tags)
            time.sleep(anim_speed)
        while current_font_size < max_font:
            new_font = init_font.replace(
                str(init_font_size), str(current_font_size))
            current_font_size += font_animation_speed
            self.set_arriving_status(
                font=new_font, fill=color, text=text, tags=tags)
            time.sleep(anim_speed)
        while current_font_size != init_font_size:
            new_font = init_font.replace(
                str(init_font_size), str(current_font_size))
            current_font_size -= font_animation_speed
            self.set_arriving_status(
                font=new_font, fill=color, text=text, tags=tags)
            time.sleep(anim_speed)
        self.set_arriving_status(
            font=init_font, fill=color, text=text, tags=tags)
        # ime.sleep(1)
        # self.can.delete("kpp_status")
        # if self.status["arrival_in_progress"] or self.:
        #    self.set_arriving_status(text=text)

    def set_arriving_status(
            self, font=fonts.kpp_status, fill="#E4A731",
            text="Ожидается проезд авто", tags=("kpp_status",), ):
        self.can.delete(*tags)
        self.can.create_text(
            1038.24, 710,
            tags=tags,
            text=text,
            fill=fill,
            font=font,
            anchor='center')
        if text.lower() == "ожидается проезд авто":
            self.arriving_in_progress = True
            self.create_abort_photocell_waiting_btn()
        elif text.lower() == "авто проехало":
            if self.kpp_pass_win_opened and self.operator.current == "KPP":
                self.destroyBlockImg()
            self.delete_abort_photocell_waiting_btn()
        elif text.lower() == "время ожидания истекло":
            if self.kpp_pass_win_opened and self.operator.current == "KPP":
                self.destroyBlockImg()
            self.delete_abort_photocell_waiting_btn()

    def external_button_pressed(self):
        if self.check_kpp_busy():
            return
        if self.kpp_info["recognise"]:
            self.draw_preloader_recognition()
            self.lets_recognise("external")
        else:
            self.draw_manual_pass_entry()

    def check_kpp_busy(self):
        if self.status["barrier_open"]:
            self.trying_start_new_arrival_while_current(
                text="Шлагбаум открыт",
                tags=("kpp_status", "kpp_lift_up_in_progress_status"))
            return True
        elif self.status["arrival_in_progress"]:
            self.trying_start_new_arrival_while_current(
                text="Ожидается проезд авто",
                tags=("kpp_status", "arrival_in_progress"))
            return True

    def internal_button_pressed(self):
        if self.check_kpp_busy():
            return
        if self.kpp_info["recognise"]:
            self.draw_preloader_recognition()
            self.lets_recognise("internal")
        else:
            self.draw_manual_pass_exit()

    def draw_preloader_recognition(self):
        self.drawBlurScreen()
        self.can.delete("kpp_barrier_arrow")
        self.hide_buttons(self.right_corner_sys_buttons_objs)
        self.can.create_text(
            960, 620, text="Пытаемся распознать гос. номер",
            font=fonts.kpp_preloader_text, fill="#F2F2F2", tags=("trying_text",
                                                                 "plate_recognition"))
        self.operator.turn_cams(False)
        self.break_recognition_btn.lift()
        self.plate_recognition_in_progress = True
        self.hide_kpp_tree_btns()
        self.hide_widgets(self.page_buttons)
        self.hide_main_navbar_btns()
        self.delete_abort_photocell_waiting_btn()
        self.kpp_lift_up_btn.lower()
        threading.Thread(target=self.rotate_preloader, daemon=True).start()

    def break_recognition_proc(self):
        self.can.delete("plate_recognition")
        self.destroyBlockImg()

    def set_recognition_count(self, count, max_count=3):
        self.can.delete("try_count")
        self.can.create_text(
            960, 675, text=f"{count}/{max_count}",
            font=fonts.kpp_preloader_text, fill="#F2F2F2", tags=("trying_text",
                                                                 "plate_recognition",
                                                                 "try_count"))

    def draw_recognition_success(self):
        # self.drawBlurScreen()
        self.plate_recognition_in_progress = False
        self.can.delete("plate_recognition")
        self.can.create_text(
            960, 620, text="Гос. номер распознан",
            font=fonts.kpp_preloader_text, fill="#F2F2F2",
            tags=("success_text",
                  "plate_recognition"))
        self.break_recognition_btn.lower()
        self.can.create_image(960, 516, image=self.kpp_success_recognition,
                              tags=("preloader_circle",
                                    "plate_recognition"))

    def draw_recognition_failed(self):
        if not (self.plate_recognition_in_progress and self.blurDrawn and not self.blockImgDrawn):
            return
        print("HEEEEERE!" )
        # self.drawBlurScreen()
        self.can.delete("plate_recognition")
        self.can.create_text(
            960, 620, text="Гос. номер не распознан!",
            font=fonts.kpp_preloader_text, fill="#F2F2F2",
            tags=("success_text",
                  "plate_recognition"))
        self.break_recognition_btn.lower()
        self.can.create_image(960, 516, image=self.kpp_failed_recognition,
                              tags=("preloader_circle",
                                    "plate_recognition"))


    def destroy_recognition_win(self):
        self.can.delete("plate_recognition")
        self.destroyBlockImg()

    def rotate_preloader(self):
        start_pos = 0
        cur_pos = start_pos
        self.el_list = []
        while self.plate_recognition_in_progress:
            if not self.operator.currentPage == self or self.operator.currentPage.blockImgDrawn:
                self.can.delete("plate_recognition")
                time.sleep(0.1)
                continue
            tkimage = PIL.ImageTk.PhotoImage(
                self.kpp_preloader_img.rotate(cur_pos, expand=True))
            # center=(start_pos, end_pos)))
            self.el_list.append(tkimage)
            cur_pos += 1.5
            self.can.create_image(960, 516, image=tkimage,
                                  tags=("preloader_circle",
                                        "plate_recognition"))
            try:
                self.el_list = self.el_list[-5:]
            except IndexError:
                pass
            time.sleep(0.001)

        self.turn_on_cameras()

    def kpp_get_info(self):
        self.operator.ar_qdk.execute_method("kpp_get_info")

    def draw_gate_arrows(self):
        self.draw_set_arrow("kpp_barrier_arrow")

    def open_barrier(self):
        threading.Thread(target=self.rotate_gate_arrow, args=(
            "kpp_barrier_arrow", 'open', 'OUT', 1, 85), daemon=True).start()

    def close_barrier(self):
        threading.Thread(target=self.rotate_gate_arrow, args=(
            "kpp_barrier_arrow", 'close', 'OUT', -1, 0), daemon=True).start()

        # self.plase_kpp_tree_btns()
        # threading.Thread(target=self.test).start()

    def create_abort_photocell_waiting_btn(self):
        if self.arriving_in_progress:
            self.abort_photocell_waiting_btn.lift()

    def delete_abort_photocell_waiting_btn(self):
        self.abort_photocell_waiting_btn.lower()

    def abort_photocell_waiting_pressed(self):
        # make_log
        # self.draw_block_win()
        self.operator.ar_qdk.execute_method(
            "log_event",
            event="Оператор нажал на кнопку прерывания ожидания фотоэлементов")
        # self.abort_photocell_waiting_btn.lower()
        self.initBlockImg('kpp_abort_photocell_waiting_confirmation_win',
                          "kpp_abort_photocell_waiting_win_btns")
        self.photocell_waiting_abort_note = self.getText(
            h=2, w=32, bg=cs.orup_bg_color, font=fonts.orup_font,
            tags=("block_win_els",))
        self.can.create_window(1072, 600,
                               window=self.photocell_waiting_abort_note,
                               tag='block_win_els')
        self.delete_abort_photocell_waiting_btn()
        # self.can.delete("kpp_status")

    def continue_photocell_waiting(self):
        self.operator.ar_qdk.execute_method(
            "log_event",
            event="Оператор решил продолжить ожидание пересечения фотоэлементов")
        self.destroyBlockImg()
        if self.arriving_in_progress:
            # print("TT11. FROM CONTINUE PH WA")
            self.create_abort_photocell_waiting_btn()

    def abort_photocell_waiting(self):
        # self.operator.ar_qdk.execute_method(
        #    "log_event",
        #    event="Оператор прервал ожидание фотоэлементов вручную!",
        #    level="warning")
        operator_comment = self.photocell_waiting_abort_note.get(
            "1.0", 'end-1c')
        if len(operator_comment) == 0:
            self.photocell_waiting_abort_note["highlightcolor"] = "#E14B50"
            self.photocell_waiting_abort_note["highlightthickness"] = 1
            return
        self.operator.ar_qdk.execute_method(
            "kpp_break_photocell_waiting",
            comment=operator_comment)
        self.destroyBlockImg()
        self.arriving_in_progress = False
        self.delete_abort_photocell_waiting_btn()
        self.can.delete("kpp_status")

    def abort_round(self):
        operator_comment = self.photocell_waiting_abort_note.get(
            "1.0", 'end-1c')
        if len(operator_comment) == 0:
            self.photocell_waiting_abort_note["highlightcolor"] = "#E14B50"
            self.photocell_waiting_abort_note["highlightthickness"] = 1
            return
        self.operator.ar_qdk.execute_method(
            "kpp_abort_arriving",
            comment=operator_comment)
        self.destroyBlockImg()
        self.arriving_in_progress = False
        self.delete_abort_photocell_waiting_btn()
        self.can.delete("kpp_status")

    # def init_photocell_waiting_abort_window(self):
    #    self.initBlockImg('kpp_abort_photocell_waiting_confirmation_win')

    def plase_kpp_tree_btns(self):
        self.place_car_number_combobox()
        self.place_clients_combobox()
        self.place_carriers_combobox()
        self.place_calendars()

    def hide_kpp_tree_btns(self):
        self.kpp_tree_carnum_cb.lower()
        self.kpp_tree_carriers_cb.lower()
        self.kpp_tree_clients_cb.lower()
        self.kpp_end_calendar.lower()
        self.kpp_start_calendar.lower()

    def show_kpp_tree_btns(self):
        self.kpp_tree_carnum_cb.lift()
        self.kpp_tree_carriers_cb.lift()
        self.kpp_tree_clients_cb.lift()
        self.kpp_end_calendar.lift()
        self.kpp_start_calendar.lift()

    def configure_combobox(self, om):
        om.master.option_add('*TCombobox*Listbox.background', '#3D3D3D')
        om.master.option_add('*TCombobox*Listbox.foreground',
                             cs.kpp_filter_font)
        om.master.option_add('*TCombobox*Listbox.selectBackground',
                             cs.orup_active_color)
        om.master.option_add('*TCombobox*Listbox.font',
                             fonts.kpp_filters_content)
        om.config(font=fonts.kpp_filters)
        om['style'] = 'kpp_filters.TCombobox'

    def update_car_number_combobox(self):
        listname = self.operator.get_auto_reprs()
        self.kpp_tree_carnum_cb.set_completion_list(listname)

    def place_car_number_combobox(self):
        listname = self.operator.get_auto_reprs()
        self.kpp_tree_carnum_cb = AutocompleteComboboxCarNumber(
            self.root, default_value="Гос. номер")
        self.kpp_tree_carnum_cb.set_completion_list(listname)
        self.configure_combobox(self.kpp_tree_carnum_cb)
        self.kpp_tree_carnum_cb.config(width=10, height=21)
        self.can.create_window(348, 186.5,
                               window=self.kpp_tree_carnum_cb,
                               tags=(
                                   'kpp_carnum_cb', 'kpp_filter'))
        self.hide_while_cam_zoom_widgets.append(self.kpp_tree_carnum_cb)
        self.page_widgets.append(self.kpp_tree_carnum_cb)

    def place_clients_combobox(self):
        self.kpp_tree_clients_cb = AutocompleteCombobox(
            self.root, default_value='Клиенты')
        self.configure_combobox(self.kpp_tree_clients_cb)
        self.kpp_tree_clients_cb.set_completion_list(
            self.operator.get_clients_reprs())
        self.kpp_tree_clients_cb['style'] = 'orup.TCombobox'
        self.configure_combobox(self.kpp_tree_clients_cb)
        self.kpp_tree_clients_cb.config(width=20, height=21)
        self.can.create_window(530, 186.5,
                               window=self.kpp_tree_clients_cb,
                               tags=(
                                   "kpp_filter", 'typeCombobox'))

    def place_carriers_combobox(self):
        self.kpp_tree_carriers_cb = AutocompleteCombobox(
            self.root, default_value='Перевозчики')
        self.configure_combobox(self.kpp_tree_carriers_cb)
        self.kpp_tree_carriers_cb.set_completion_list(
            self.operator.get_clients_reprs())
        self.kpp_tree_carriers_cb['style'] = 'orup.TCombobox'
        self.configure_combobox(self.kpp_tree_carriers_cb)
        self.kpp_tree_carriers_cb.config(width=20, height=21)
        self.can.create_window(750, 186.5,
                               window=self.kpp_tree_carriers_cb,
                               tags=(
                                   "kpp_filter", 'typeCombobox'))

    def place_calendars(self):
        self.kpp_start_calendar = MyDateEntry(self.root,
                                              date_pattern='dd.mm.Y')
        self.kpp_start_calendar.config(width=9, font=fonts.kpp_calendar)
        self.kpp_end_calendar = MyDateEntry(self.root, date_pattern='dd.mm.Y')
        self.kpp_end_calendar.config(width=9, font=fonts.kpp_calendar)
        self.kpp_start_calendar['style'] = 'kpp_filters.TCombobox'
        self.kpp_end_calendar['style'] = 'kpp_filters.TCombobox'
        self.can.create_window(1108, 186.5,
                               window=self.kpp_start_calendar,
                               tags=(
                                   "kpp_filter", "kpp_calendar"))
        self.can.create_window(1285, 186.5,
                               window=self.kpp_end_calendar,
                               tags=(
                                   "kpp_filter", "kpp_calendar"))

    def get_cars_inside_full_info(self):
        if not self.arrivals:
            return []
        return [car for car in self.arrivals if car['opened']]

    def draw_manual_pass_exit(
            self, car_number=None, note=None,
            alert_text="Гос.номер не обнаружен!\n"
                       "Если машина есть, выберите ее из списка въехавших ранее.\n"
                       "Такой пропуск будет отмечен как пропуск без распознавания.\n",
            without_time_in=False):
        self.kpp_pass_win_opened = True
        self.pass_out_without_time_in = without_time_in
        self.kpp_internal_init_carnum = car_number
        self.initBlockImg(name='kpp_manual_pass_internal_win',
                          btnsname="kpp_manual_pass_internal_btns")
        # creating car number combobox
        self.kpp_cars_inside = self.get_cars_inside_full_info()
        car_numbers = [car['car_number'] for car in self.kpp_cars_inside if
                       car["car_number"]]
        self.kpp_manual_pass_internal_number_var = StringVar()
        self.kpp_manual_pass_internal_number_var.trace_add(
            'write', self.manual_pass_internal_number_react)
        self.kpp_car_number_internal = self.create_orup_combobox(
            500, 172,
            textvariable=self.kpp_manual_pass_internal_number_var,
            width=36, height=7, tags=("block_win_els",))
        if car_numbers:
            self.kpp_car_number_internal.set_completion_list(car_numbers)
            # f not car_number:
            #    self.kpp_manual_pass_internal_number_var.set(car_numbers[0])
        self.kpp_manual_pass_internal_number_var.trace_add(
            'write', self.manual_pass_internal_number_change_react)
        if car_number:
            self.kpp_manual_pass_internal_number_var.set(car_number)
            alert_text = f"Въезд {car_number} не был зарегистрирован!\n" \
                         "Вы можете выпустить ее, но это будет зафиксировано в системе.\n" \
                         "Если же считало неправильно, пожалуйста, исправьте гос.номер.\n"
        elif not car_number and not car_numbers:
            alert_text = f"Гос.номер не распознан!\nТак же в системе не зафиксированы машины на территории." \
                         f"\nЕсли действительно есть машина, укажите ее гос.номер перед выпуском."
        elif not car_number and car_number:
            alert_text = f"Гос.номер не распознан!\nНо в системе зафиксированы другие машины." \
                         f"\nПроверьте, может гос.номер распознан неверно?."
        self.manual_pass_note_internal = self.getText(
            h=3, w=32, bg=cs.orup_bg_color, font=fonts.orup_font,
            tags=("block_win_els",))
        if note:
            self.manual_pass_note_internal.insert(1.0, note)
        self.can.create_window(500, 250,
                               window=self.manual_pass_note_internal,
                               tag='block_win_els')
        self.can.create_text(385, 390,
                             text=alert_text,
                             font=fonts.general_text_font,
                             tags=('block_win_els', 'statusel'),
                             fill=self.textcolor, anchor='n',
                             justify='center')
        self.turn_on_cameras()
        self.unbindArrows()
        self.root.bind('<Escape>',
                       lambda event: self.destroy_internal_orup())
        self.root.bind('<Return>',
                       lambda event: self.kpp_manual_pass_internal())
        self.show_camera("kpp_cam_internal")
        self.root.after(1000, self.capture_kpp_win_opened)


    def kpp_manual_pass_internal(self):
        valid_entries = self.validate_internal_entries()
        if not valid_entries:
            return
        self.operator.ar_qdk.execute_method(
            "kpp_close_arrival",
            car_number=self.kpp_manual_pass_internal_number_var.get().capitalize(),
            note=self.manual_pass_note_internal.get("1.0", "end-1c"),
            pass_out_without_time_in=self.pass_out_without_time_in,
            init_car_number=self.kpp_internal_init_carnum)
        self.hide_camera("kpp_cam_internal")
        self.destroyBlockImg()

    def manual_pass_internal_number_change_react(self, *args):
        for car in self.kpp_cars_inside:
            if self.kpp_manual_pass_internal_number_var.get() == self.operator.get_auto_repr(
                    car["auto_id"]):
                if car["note"]:
                    self.manual_pass_note_internal.delete(1.0, END)
                    self.manual_pass_note_internal.insert(1.0, car["note"])
                else:
                    self.manual_pass_note_internal.delete(1.0, END)

    def draw_manual_pass_entry(
            self, car_number=None, client_id=None,
            carrier_id=None, notes=None,
            alert_text="Гос.номер не распознан. Если машина есть, укажите гос.номер сами."
                       "\nВ системе такой проезд будет отмечен как пропуск без распознавания.",
            close_opened_id=False):
        self.kpp_pass_win_opened = True
        self.kpp_external_init_carnum = car_number
        self.close_arrival_without_pass_out = close_opened_id
        self.initBlockImg(name='kpp_manual_pass_win',
                          btnsname="kpp_manual_pass_entry_btns")
        # creating car number combobox
        self.kpp_manual_pass_number_string = StringVar()
        self.manual_pass_entry_number_cb = self.create_orup_combobox(
            500, 172, textvariable=self.kpp_manual_pass_number_string,
            width=36, height=7, tags=("block_win_els",))
        self.kpp_manual_pass_number_string.trace_add(
            'write', self.manual_pass_external_number_react)
        self.manual_pass_entry_number_cb.set_completion_list(
            self.operator.get_auto_reprs())
        if car_number:
            self.manual_pass_entry_number_cb.set(car_number)
        # creating client combobox
        self.manual_pass_entry_client_cb = self.create_orup_combobox(
            500, 235, width=36, height=7, tags=("block_win_els",))
        self.manual_pass_entry_client_cb.set_completion_list(
            self.operator.get_clients_reprs())
        if client_id:
            self.manual_pass_entry_client_cb.set(
                self.operator.get_client_repr(client_id))
        # creating carrier combobox
        self.manual_pass_entry_carrier_cb = self.create_orup_combobox(
            500, 298, width=36, height=7, tags=("block_win_els",))
        self.manual_pass_entry_carrier_cb.set_completion_list(
            self.operator.get_clients_reprs())
        if carrier_id:
            self.manual_pass_entry_client_cb.set(
                self.operator.get_client_repr(carrier_id))
        self.manual_pass_note = self.getText(
            h=3, w=32, bg=cs.orup_bg_color, font=fonts.orup_font,
            tags=("block_win_els",))
        if notes:
            self.manual_pass_note.insert(1.0, notes)
        self.can.create_window(500, 378,
                               window=self.manual_pass_note,
                               tags=("block_win_els", 'orupentry'))
        self.can.create_text(385, 530,
                             text=alert_text,
                             font=fonts.general_text_font,
                             tags=('block_win_els', 'statusel'),
                             fill=self.textcolor, anchor='n',
                             justify='center')
        self.turn_on_cameras()
        self.root.bind('<Return>',
                       lambda event: self.send_manual_pass_command_external())
        self.root.bind('<Escape>',
                       lambda event: self.destroy_external_orup())
        self.root.bind("<Double-Button-1>",
                       lambda event: self.clear_optionmenu(event))
        self.unbindArrows()
        self.show_camera("kpp_cam_external")
        self.root.after(1000, self.capture_kpp_win_opened)

    def capture_kpp_win_opened(self):
        self.operator.ar_qdk.execute_method('capture_kpp_win_opened')


    def validate_external_entries(self):
        car_number = self.kpp_manual_pass_number_string.get()
        car_number_valid = self.validate_car_number(car_number)
        if car_number_valid:
            self.manual_pass_entry_number_cb['style'] = 'orup.TCombobox'
        else:
            self.manual_pass_entry_number_cb[
                'style'] = 'orupIncorrect.TCombobox'
        client = self.manual_pass_entry_client_cb.get()
        if client:
            client_valid = self.validate_client(
                client, self.operator.get_clients_reprs())
            if client_valid:
                self.manual_pass_entry_client_cb['style'] = 'orup.TCombobox'
            else:
                self.manual_pass_entry_client_cb[
                    'style'] = 'orupIncorrect.TCombobox'
        carrier = self.manual_pass_entry_client_cb.get()
        if carrier:
            carrier_valid = self.validate_client(
                client, self.operator.get_clients_reprs())
            if carrier_valid:
                self.manual_pass_entry_carrier_cb['style'] = 'orup.TCombobox'
            else:
                self.manual_pass_entry_carrier_cb[
                    'style'] = 'orupIncorrect.TCombobox'
        if car_number_valid and (client and client_valid or not client) and (
                carrier and carrier_valid or not carrier):
            return True

    def validate_internal_entries(self):
        car_number = self.kpp_car_number_internal.get()
        car_number_valid = self.validate_car_number(car_number)
        if car_number_valid:
            self.kpp_car_number_internal['style'] = 'orup.TCombobox'
            return True
        else:
            self.kpp_car_number_internal[
                'style'] = 'orupIncorrect.TCombobox'

    def validate_client(self, client, clients):
        if client in clients:
            return True

    def show_camera(self, camera_type):
        #        camera_type = "kpp_cam_external"
        video_inst = self.operator.get_camera_inst(camera_type)
        if video_inst:
            video_inst.set_new_params(x=1331, y=341, width=1110, height=614)

    def hide_camera(self, camera_type):
        video_inst = self.operator.get_camera_inst(camera_type)
        if video_inst:
            video_inst.hide_callback()

    def send_manual_pass_command_external(self):
        validate = self.validate_external_entries()
        if not validate:
            return
        if self.close_arrival_without_pass_out:
            self.operator.ar_qdk.execute_method(
                "kpp_close_arrival_without_pass_out",
                arrival_id=self.close_arrival_without_pass_out,
                note=self.manual_pass_note.get("1.0", "end-1c", ))
        self.operator.ar_qdk.execute_method(
            "kpp_create_arrival",
            car_number=self.kpp_manual_pass_number_string.get().capitalize(),
            client_id=self.operator.get_client_id(
                self.manual_pass_entry_client_cb.get()),
            carrier_id=self.operator.get_client_id(
                self.manual_pass_entry_carrier_cb.get()),
            note=self.manual_pass_note.get("1.0", "end-1c"),
            init_car_number=self.kpp_external_init_carnum)
        self.hide_camera("kpp_cam_external")
        self.destroyBlockImg()

    def validate_car_number(self, carnum):
        valid_car = re.match(
            '^[АВЕКМНОРСТУХ]\d{3}(?<!000)[АВЕКМНОРСТУХ]{2}\d{2,3}$',
            carnum)
        valid_agro = re.match("^\d{4}(?<!0000)[АВЕКМНОРСТУХ]{2}\d{2,3}$",
                              carnum)
        valid_trailer = re.match("^[АВЕКМНОРСТУХ]{2}\d{4}(?<!0000)\d{2,3}$",
                                 carnum)
        if (valid_car or valid_trailer or valid_agro):
            return True

    def manual_pass_external_number_react(self, *args):
        # Функция реакции программы на совершение действий типа write в combobox для ввода гос.номера
        self.validate_car_number_combobox(self.manual_pass_entry_number_cb)

    def manual_pass_internal_number_react(self, *args):
        # Функция реакции программы на совершение действий типа write в combobox для ввода гос.номера
        self.validate_car_number_combobox(self.kpp_car_number_internal)

    def validate_car_number_combobox(self, combobox):
        carnum = combobox.get()
        carnum = carnum.upper()
        value = len(carnum)
        combobox.set(carnum)
        valid_car_number = self.validate_car_number(carnum)
        if not valid_car_number or value < 8:
            # Сделать красную обводку
            combobox['style'] = 'orupIncorrect.TCombobox'
        else:
            # Оставить обычное оформление
            combobox['style'] = 'orup.TCombobox'

    def get_arrivals(self):
        self.operator.ar_qdk.execute_method(
            "kpp_get_arrivals",
            auto_id=self.operator.get_auto_id(self.kpp_tree_carnum_cb.get()),
            carrier_id=self.operator.get_client_id(
                self.kpp_tree_carriers_cb.get()),
            client_id=self.operator.get_client_id(
                self.kpp_tree_clients_cb.get()),
            time_in=self.kpp_start_calendar.get(),
            time_out=self.kpp_end_calendar.get())

    def abort_filters(self):
        """ Сбросить все фильтры на значения по умолчанию"""
        self.kpp_tree_carnum_cb.set_default_value()
        self.kpp_tree_carriers_cb.set_default_value()
        self.kpp_tree_clients_cb.set_default_value()
        self.kpp_start_calendar.set_date(datetime.datetime.today())
        self.kpp_end_calendar.set_date(datetime.datetime.today())
        self.get_arrivals()

    def create_tree(self):
        self.tar = KPPTreeview(self.root, self.operator, height=18)
        self.tar.createTree()
        self.tree = self.tar.get_tree()
        self.tree.bind("<Double-Button-1>", self.double_click_record)
        return self.tree

    def double_click_record(self, event):
        """ Реакция на дабл-клик по текущему заезду """
        item = self.tree.selection()[0]
        self.chosen_arrival_id = self.tree.item(item, "text")
        self.chosen_arrival = self.tree.item(item, "values")
        for arrival in self.arrivals:
            if arrival["id"] == self.chosen_arrival_id:
                self.chosen_arrival = arrival
                continue
        opened = self.chosen_arrival["opened"]
        if opened:
            self.draw_arrival_close_win()
        else:
            threading.Thread(
                target=self.create_notification_animation,
                args=('kpp_record_already_close_win.png',), daemon=True).start()

    def draw_arrival_close_win(self):
        self.initBlockImg("kpp_close_record_win", "kpp_close_record_btns")
        self.manual_arrival_close_note = self.getText(
            h=3, w=50, bg=cs.orup_bg_color, font=fonts.orup_font)
        self.can.create_window(960, 635, window=self.manual_arrival_close_note,
                               tags = ("block_win_els"))
        self.root.bind('<Return>', lambda event: self.kpp_close_arrival_manual())
        self.root.bind('<Escape>', lambda event: self.destroyBlockImg())

    def kpp_close_arrival_manual(self):
        user_note = self.manual_arrival_close_note.get("1.0", "end-1c")
        if not user_note:
            self.manual_arrival_close_note["highlightcolor"] = "#E14B50"
            self.manual_arrival_close_note["highlightthickness"] = 1
            return
        self.operator.ar_qdk.execute_method(
            "kpp_close_arrival_manually",
            arrival_id=self.chosen_arrival_id,
            note=self.manual_arrival_close_note.get("1.0", "end-1c", ))
        self.destroyBlockImg()
        self.get_arrivals()

    def bindArrows(self):
        if self.settings.kpp_mirrored:
            left_button = self.internal_button_pressed
            right_button = self.external_button_pressed
        elif not self.settings.kpp_mirrored:
            left_button = self.external_button_pressed
            right_button = self.internal_button_pressed
        self.root.bind('<Left>', lambda event: left_button())
        self.root.bind('<Right>', lambda event: right_button())

    def cam_zoom_callback(self, cam_type=None):
        self.hide_kpp_tree_btns()
        self.hide_buttons((self.ok_btn, self.abort_btn))
        super().cam_zoom_callback(cam_type)
        try:
            self.abort_photocell_waiting_btn.lower()
        except:
            pass

    def cam_hide_callback(self, cam_type=None):
        #super(KPP, self).cam_hide_callback(cam_type)
        self.tree.lift()
        self.cam_zoom = False
        self.show_kpp_tree_btns()
        self.turn_on_cameras()
        self.create_abort_photocell_waiting_btn()
        self.show_buttons((self.ok_btn, self.abort_btn))

    def initBlockImg(self, name, btnsname=None, slice='shadow', mode='new',
                     seconds=[], hide_widgets=[], picture=None, **kwargs):
        self.hide_kpp_tree_btns()
        self.hide_widgets(self.page_buttons)
        super(KPP, self).initBlockImg(
            name, btnsname, slice, mode, seconds, hide_widgets,
            picture, **kwargs)
        self.hide_main_navbar_btns()
        self.delete_abort_photocell_waiting_btn()

    def destroyBlockImg(self, mode="total"):
        if not self.operator.current == self.name:
            self.operator.currentPage.destroyBlockImg()
            return False
        #print("Bruh", self.operator.current, self.name)
        self.operator.ar_qdk.execute_method("capture_kpp_win_closed")
        self.kpp_pass_win_opened = False
        super(KPP, self).destroyBlockImg()
        self.turn_on_cameras()
        self.tree.lift()
        self.get_arrivals()
        self.show_kpp_tree_btns()
        self.show_main_navbar_btns()
        self.break_recognition_btn.lower()
        self.show_time()
        if self.status["barrier_open"]:
            self.show_lift_btn("down")
        else:
            self.show_lift_btn("up")
        self.can.delete("try_count")
        # self.kpp_lift_up_btn.lift()

    def destroy_external_orup(self):
        self.hide_camera("kpp_cam_external")
        self.destroy_orup(reason="закрытие внешнего ОРУП КПП")

    def destroy_internal_orup(self):
        self.hide_camera("kpp_cam_internal")
        self.destroy_orup(reason="закрытие внутреннего ОРУП КПП")

    def drawBlurScreen(self):
        super(KPP, self).drawBlurScreen()

    def place_car_detect_text(self, side_name):
        self.operator.place_car_detect_text(
            side_name,
            self.operator.cam_meta["kpp_cam_external"]["xpos"],
            self.operator.cam_meta["kpp_cam_external"]["ypos"],
            self.operator.cam_meta["kpp_cam_internal"]["xpos"],
            self.operator.cam_meta["kpp_cam_internal"]["ypos"],
            self.operator.cam_meta["kpp_cam_external"]["v_width"],
            self.operator.cam_meta["kpp_cam_external"]["v_height"],
        )

    def open_entry_gate_operation_start(self):
        pass

    def close_entry_gate_operation_start(self):
        pass

    def open_exit_gate_operation_start(self):
        pass

    def close_exit_gate_operation_start(self):
        pass

    def openWin(self):
        super(KPP, self).openWin()
        self.render_status()
        self.hide_weight()
        self.get_arrivals()
        self.get_kpp_status()
        if not self.clockLaunched:
            self.start_clock()
            self.clockLaunched = True
        self.can.create_window(1038.5, 435, window=self.tree, tag='tree')
        self.draw_gate_arrows()
        # self.draw_barrier_arrow("kpp_barrier")
        self.show_widgets(self.page_widgets)
        self.show_kpp_tree_btns()
        # if self.arriving_in_progress:
        #    self.set_arriving_status(
        #        text="Ожидается проезд авто",
        #        tags=("kpp_status", "arriving_in_progress"))
        #    self.create_abort_photocell_waiting_btn()
        self.show_main_navbar_btns()

    def page_close_operations(self):
        super(KPP, self).page_close_operations()
        self.delete_abort_photocell_waiting_btn()
        self.operator.turn_cams(False)
        self.hide_kpp_tree_btns()
        self.break_recognition_btn.lower()
        self.root.unbind("Escape")
        self.hide_main_navbar_btns()
        # self.kpp_lift_up_btn.lower()
        # self.kpp_lift_down_btn.lower()
        self.can.delete(
            "kpp_status", "plate_recognise_status_internal", "plate_recognise_status_external", "try_count",
            "preloader_circle")


    def compare_timestamps(self, timestamp_dict):

        def parse(ts):
            if not ts:
                return None
            try:
                return datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                return None

        best_key = None
        best_time = None

        for k, v in timestamp_dict.items():
            dt = parse(v)
            if dt and (best_time is None or dt > best_time):
                best_time = dt
                best_key = k

        return best_key

    def render_status(self):
        if not self.status:
            return
        if self.status["emergency_lift_up"]["active"]:
            self.set_arriving_status(
                text=f"Шлагбаум не смог закрыться, проверьте фотоэлементы!",
                tags=("kpp_status", "arriving_in_progress"))
        elif self.status["barrier_open"]:
            self.show_gate_open_status()
        elif self.status["arrival_in_progress"]:
            self.arriving_in_progress = True
            self.set_arriving_status()
            self.create_abort_photocell_waiting_btn()
        else:
            self.arriving_in_progress = False
            self.can.delete("arriving_in_progress")
        if self.blockImgDrawn:
            return
        if self.status["barrier_open"]:
            self.show_lift_btn("down")
            #if self.operator.road_anim_info["kpp_barrier_arrow"]['pos'] != 85:
            self.open_barrier()
        else:
            self.show_lift_btn("up")
            #if self.operator.road_anim_info["kpp_barrier_arrow"]['pos'] != 85:
            self.close_barrier()

    def set_status(self, status):
        if not status:
            return
        self.status = status

    def recognition_status_off(self):
        self.plate_recognition_in_progress = False

    def operate_new_plate_recognition_trying(
            self, current_try, max_tries, side="external", *args, **kwargs):
        if self.operator.current != "KPP":
            return
        if self.blurDrawn:
            if not self.blockImgDrawn:
                self.set_recognition_count(current_try, max_tries)
        else:
            text = f"Пытаемся распознать... ({current_try}/{max_tries})"
            if side == "external":
                camera_type = "kpp_cam_external"
                tag = "plate_recognise_status_external"
                self.can.delete("cad_color_external")
                delta_x = -65
            else:
                camera_type = "kpp_cam_internal"
                tag = "plate_recognise_status_internal"
                self.can.delete("cad_color_internal")
                delta_x = 65
            camera_inst = self.operator.get_camera_inst(camera_type)
            if not camera_inst:
                return
            x = camera_inst.place_x + delta_x
            y = camera_inst.place_y - camera_inst.video_height / 2 - 16  # Что бы текст был над видео
            self.can.delete(tag)
            if (self.blockImgDrawn and not self.orupState) or self.cam_zoom:
                return
            self.can.create_text(
                x, y, text=text, font=fonts.cad_work_font,
                fill=cs.orup_fg_color, tags=(tag,))
            threading.Thread(
                target=self.operator.tag_timeout_deleter,
                args=(tag, 4), daemon=True).start()

