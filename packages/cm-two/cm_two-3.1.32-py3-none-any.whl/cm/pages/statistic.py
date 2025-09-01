from cm.pages.superpage import SuperPage
import datetime
import tkinter.filedialog
import traceback
from tkinter import StringVar
from cm.modules.gtki_module_exex.main import CreateExcelActs
from gtki_module_treeview.main import HistroryTreeview
from cm.styles import color_solutions as cs, fonts
from cm.widgets.dropDownCalendar import MyDateEntry
from cm.widgets.drop_down_combobox import AutocompleteCombobox, \
    AutocompleteComboboxCarNumber


class Statistic(SuperPage):
    """ Окно статистики """

    def __init__(self, root, settings, operator, can):
        super(Statistic, self).__init__(root, settings, operator, can)
        self.btns_height = self.h / 4.99
        self.records_amount = 0
        self.uncount_records = []
        self.name = 'Statistic'
        self.buttons = settings.statBtns
        # self.font = '"Montserrat SemiBold" 14'
        self.history = {}
        self.chosenType = ''
        self.chosenContragent = ''
        self.choosenCat = ''
        self.typePopup = ...
        self.carnums = []
        self.filterColNA = '#2F8989'
        self.filterColA = '#44C8C8'
        self.tree = self.create_tree()
        self.posOptionMenus()
        self.calendarsDrawn = False
        self.btn_name = self.settings.statisticBtn
        self.weight_sum = 0
        self.changed_record = None
        self.page_buttons = self.create_btns_and_hide(self.buttons)

    def create_tree(self):
        self.tar = HistroryTreeview(self.root, self.operator, height=28)
        self.tar.createTree()
        self.tree = self.tar.get_tree()
        self.tree.bind("<Double-Button-1>", self.OnDoubleClick)
        return self.tree

    def rebind_btns_after_orup_close(self):
        self.tree.bind("<Double-Button-1>", self.OnDoubleClick)

    def excel_creator(self):
        file_name = self.get_excel_file_path()
        data_list = self.generate_excel_content()
        self.form_excel(file_name, data_list)

    def export_1c_report(self):
        self.operator.ar_qdk.execute_method("send_1c_report")

    def generate_excel_content(self):
        items = self.tree.get_children()
        data_list = []
        for item in items:
            record_id = self.tree.item(item, 'text')
            data = self.tree.item(item, 'values')
            data = list(data)
            data.insert(0, record_id)
            data_list.append(data)
        return data_list

    def get_excel_file_path(self):
        name = tkinter.filedialog.asksaveasfilename(defaultextension='.xlsx',
                                                    filetypes=[("Excel files",
                                                                "*.xls *.xlsx")])
        return name

    def form_excel(self, file_name, data_list):
        inst = CreateExcelActs(file_name, data_list, self.amount_weight)
        inst.create_document()

    def OnDoubleClick(self, event):
        ''' Реакция на дабл-клик по заезду '''
        self.orupState = True
        item = self.tree.selection()[0]
        self.chosenStr = self.tree.item(item, "values")
        self.record_id = self.tree.selection()[0]
        self.draw_change_records(self.chosenStr, item)

    def draw_change_records(self, string, record_id):
        self.parsed_string = self.parse_string(string)
        btnsname = 'record_change_btns'
        record_info = self.history[int(record_id)]
        print("C1")
        self.initBlockImg('record_change_win', btnsname=btnsname,
                          hide_widgets=self.statisticInteractiveWidgets)
        print("C2")
        self.posEntrys(
            carnum=self.parsed_string["car_number"],
            trashtype=self.parsed_string["trash_type"],
            trashcat=self.parsed_string["trash_cat"],
            contragent=self.parsed_string["carrier"],
            client=self.parsed_string['client'],
            notes=self.parsed_string['notes'],
            polygon=self.operator.get_polygon_platform_repr(record_info['id']),
            object=self.operator.get_pol_object_repr(record_info['object_id']),
            spec_protocols=False,
            call_method='manual',
        )
        print("C3")
        self.root.bind('<Return>', lambda event: self.change_record())
        self.root.bind('<Escape>',
                       lambda event: self.destroy_orup(mode="decline"))
        self.root.bind("<Double-Button-1>",
                       lambda event: self.clear_optionmenu(event))
        self.unbindArrows()

    def mark_changed_rec(self):
        if not self.changed_record:
            return
        try:
            self.tree.selection_set(self.changed_record)
            self.tree.see(self.changed_record)
        except:
            print(traceback.format_exc())
            pass

    def destroy_orup(self, mode=None, reason="окно статистики"):
        super().destroy_orup(mode, reason=reason)

    def parse_string(self, string):
        # Парсит выбранную строку из окна статистики и возвращает словарь с элементами
        parsed = {}
        parsed["car_number"] = string[0]
        parsed["carrier"] = string[2]
        parsed["trash_cat"] = string[6]
        parsed["trash_type"] = string[7]
        parsed["notes"] = string[10]
        parsed['client'] = string[1]
        return parsed

    def change_record(self):
        self.changed_record = self.tree.selection()
        info = self.get_orup_entry_reprs()
        self.try_upd_record(info['carnum'], info['carrier'], info['trash_cat'],
                            info['trash_type'], info['comm'],
                            info['polygon_platform'], info['client'],
                            info['polygon_object'])

    def try_upd_record(self, car_number, carrier, trash_cat, trash_type,
                       comment, polygon, client, pol_object):
        self.car_protocol = self.operator.fetch_car_protocol(car_number)
        data_dict = {}
        data_dict['car_number'] = car_number
        data_dict['chosen_trash_cat'] = trash_cat
        data_dict['type_name'] = trash_type
        data_dict['carrier_name'] = carrier
        data_dict['client_name'] = client
        data_dict['sqlshell'] = object
        data_dict['photo_object'] = self.settings.redbg[3]
        data_dict['client'] = client
        data_dict['comment'] = comment
        data_dict['platform_name'] = self.platform_choose_var.get()
        data_dict['object_name'] = self.objectOm.get()
        response = self.operator.orup_error_manager.check_orup_errors(
            orup='brutto',
            xpos=self.settings.redbg[1],
            ypos=self.settings.redbg[2],
            **data_dict)
        if not response:
            auto_id = self.operator.get_auto_id(car_number)
            carrier_id = self.operator.get_client_id(carrier)
            trash_cat_id = self.operator.get_trash_cat_id(trash_cat)
            trash_type_id = self.operator.get_trash_type_id(trash_type)
            polygon_id = self.operator.get_polygon_platform_id(polygon)
            client_id = self.operator.get_client_id(client)
            pol_object_id = self.operator.get_polygon_object_id(pol_object)
            self.operator.ar_qdk.change_opened_record(record_id=self.record_id,
                                                      auto_id=auto_id,
                                                      carrier=carrier_id,
                                                      trash_cat_id=trash_cat_id,
                                                      trash_type_id=trash_type_id,
                                                      comment=comment,
                                                      car_number=car_number,
                                                      polygon=polygon_id,
                                                      client=client_id,
                                                      pol_object=pol_object_id)
            self.destroy_orup()
            self.upd_statistic_tree()

    def upd_statistic_tree(self):
        """ Обновить таблицу статистики """
        self.get_history()
        self.draw_stat_tree()

    def draw_add_comm(self):
        btnsname = 'addCommBtns'
        self.add_comm_text = self.getText(h=5, w=42, bg=cs.orup_bg_color)
        self.initBlockImg(name='addComm', btnsname=btnsname,
                          seconds=('second'),
                          hide_widgets=self.statisticInteractiveWidgets)
        self.can.create_window(self.w / 2, self.h / 2.05,
                               window=self.add_comm_text, tag='blockimg')
        self.root.bind('<Return>', lambda event: self.add_comm())
        self.root.bind('<Escape>',
                       lambda event: self.destroyBlockImg(mode="total"))

    def add_comm(self):
        comment = self.add_comm_text.get("1.0", 'end-1c')
        self.operator.ar_qdk.add_comment(record_id=self.record_id,
                                         comment=comment)
        self.destroyBlockImg()
        self.upd_statistic_tree()

    def posOptionMenus(self):
        self.placeTypeOm()
        self.placeCatOm(bg=self.filterColNA)
        self.placeContragentCombo()
        self.placePoligonOm()
        self.placeObjectOm()
        self.placeCarnumCombo()
        self.placeClientsOm()
        self.statisticInteractiveWidgets = [self.stat_page_polygon_combobox,
                                            self.trashTypeOm, self.trashCatOm,
                                            self.carriers_stat_om,
                                            self.stat_page_carnum_cb,
                                            self.clientsOm,
                                            self.stat_page_pol_object_combobox]
        self.hide_widgets(self.statisticInteractiveWidgets)

    def abortFiltres(self):
        """ Сбросить все фильтры на значения по умолчанию
        """
        for combobox in self.statisticInteractiveWidgets:
            if isinstance(combobox, AutocompleteCombobox):
                combobox.set_default_value()
        self.startCal.set_date(datetime.datetime.today())
        self.endCal.set_date(datetime.datetime.today())
        self.upd_statistic_tree()
        self.changed_record = None

    def placePoligonOm(self):
        listname = ['площадка'] + self.operator.get_polygon_platforms_reprs()
        self.poligonVar = StringVar()
        self.stat_page_polygon_combobox = AutocompleteCombobox(self.root,
                                                               textvariable=self.poligonVar,
                                                               default_value=
                                                               listname[0])
        self.configure_combobox(self.stat_page_polygon_combobox)
        self.stat_page_polygon_combobox.set_completion_list(listname)
        self.stat_page_polygon_combobox.config(width=8, height=30,
                                               font=fonts.statistic_filtres)
        self.can.create_window(self.w / 2.475 - 100, self.btns_height,
                               window=self.stat_page_polygon_combobox,
                               tags=('filter', 'typeCombobox'))

    def placeObjectOm(self):
        listname = ['объект'] + self.operator.get_pol_objects_reprs()
        self.pol_object_var = StringVar()
        self.stat_page_pol_object_combobox = AutocompleteCombobox(self.root,
                                                                  textvariable=self.pol_object_var,
                                                                  default_value=
                                                                  listname[0])
        self.configure_combobox(self.stat_page_pol_object_combobox)
        self.stat_page_pol_object_combobox.set_completion_list(listname)
        self.stat_page_pol_object_combobox.config(width=16, height=36,
                                                  font=fonts.statistic_filtres)
        self.can.create_window(self.w / 1.91 - 30, self.h / 3.85,
                               window=self.stat_page_pol_object_combobox,
                               tags=('filter', 'typeCombobox'))

    def placeTypeOm(self):
        listname = ['вид груза'] + self.operator.get_trash_types_reprs()
        self.stat_page_trash_type_var = StringVar()
        self.trashTypeOm = AutocompleteCombobox(self.root,
                                                textvariable=self.stat_page_trash_type_var,
                                                default_value=listname[0])
        self.configure_combobox(self.trashTypeOm)
        self.trashTypeOm.set_completion_list(listname)
        self.trashTypeOm.config(width=9, height=30,
                                font=fonts.statistic_filtres)
        self.can.create_window(self.w / 3.435 - 40, self.btns_height,
                               window=self.trashTypeOm,
                               tags=('filter', 'typeCombobox'))

    def placeCatOm(self, bg, deffvalue='кат. груза'):
        listname = ['кат. груза'] + self.operator.get_trash_cats_reprs()
        self.stat_page_trash_cat_var = StringVar()
        self.trashCatOm = AutocompleteCombobox(self.root,
                                               textvariable=self.stat_page_trash_cat_var,
                                               default_value=listname[0])
        self.trashCatOm.set_completion_list(listname)
        self.trashCatOm.config(width=9, height=30,
                               font=fonts.statistic_filtres)
        self.can.create_window(self.w / 5.45, self.btns_height,
                               window=self.trashCatOm,
                               tags=('filter', 'catOm'))
        self.configure_combobox(self.trashCatOm)

    def placeClientsOm(self):
        # listname = ['клиенты'] + self.operator.get_clients_reprs()
        self.stat_page_clients_var = StringVar()
        self.clientsOm = AutocompleteCombobox(self.root,
                                              textvariable=self.stat_page_clients_var,
                                              default_value='Клиенты')
        self.configure_combobox(self.clientsOm)
        self.full_clients()
        self.clientsOm['style'] = 'orup.TCombobox'
        # self.clientsOm.set_completion_list(listname)
        self.clientsOm.config(width=23, height=int(self.h / 40),
                              font=fonts.statistic_filtres)
        self.can.create_window(self.w / 1.278 - 60, self.btns_height,
                               window=self.clientsOm,
                               tags=('filter', 'typeCombobox'))

    def full_clients(self):
        self.clientsOm.set_completion_list(self.operator.get_clients_reprs())

    def full_carriers(self):
        self.carriers_stat_om.set_completion_list(
            self.operator.get_clients_reprs())

    def placeContragentCombo(self):
        # carriers = ['перевозчики'] + self.operator.get_clients_reprs()
        self.stat_page_carrier_var = StringVar()
        self.carriers_stat_om = AutocompleteCombobox(self.root,
                                                     textvariable=self.stat_page_carrier_var,
                                                     default_value='Перевозчики')
        self.configure_combobox(self.carriers_stat_om)
        self.full_carriers()
        self.carriers_stat_om.config(width=25, height=int(self.h / 40),
                                     font=fonts.statistic_filtres)
        self.can.create_window(self.w / 1.91 - 70, self.btns_height,
                               window=self.carriers_stat_om,
                               tags=('filter', 'stat_page_carrier_var'))

    def placeCarnumCombo(self):
        listname = ['гос.номер'] + self.operator.get_auto_reprs()
        self.stat_page_carnum_cb = AutocompleteComboboxCarNumber(self.root,
                                                                 default_value=
                                                                 listname[
                                                                     0])
        self.stat_page_carnum_cb.set_completion_list(listname)
        self.configure_combobox(self.stat_page_carnum_cb)
        self.stat_page_carnum_cb.config(width=11, height=20,
                                        font=fonts.statistic_filtres)
        self.can.create_window(self.w / 1.53 - 50, self.btns_height,
                               window=self.stat_page_carnum_cb,
                               tags=('stat_page_carnum_cb', 'filter'))

    def place_amount_info(self, weight, amount, tag='amount_weight'):
        """ Разместить итоговую информацию (количество взвешиваний (amount), тоннаж (weigh) )"""
        if self.operator.current == 'Statistic' and self.blockImgDrawn == False:
            self.can.delete(tag)
            weight = self.formatWeight(weight)
            self.amount_weight = 'ИТОГО: {} ({} взвешиваний)'.format(weight,
                                                                     amount)
            self.can.create_text(self.w / 2, self.h / 1.113,
                                 text=self.amount_weight,
                                 font=fonts.general_text_font,
                                 tags=(tag, 'statusel'),
                                 fill=self.textcolor, anchor='s',
                                 justify='center')

    def place_uncount_records(self, uncount_records, ):
        self.can.delete('amount_weight')
        uncount_records.sort()
        if uncount_records:
            amount_weight_nc = f'\nНекоторые акты {tuple(uncount_records)} ' \
                               f'были отменены.\n'
            self.can.create_text(self.w / 2, self.h / 1.062,
                                 text=amount_weight_nc,
                                 font=self.font,
                                 tags=('amount_weight', 'statusel'),
                                 fill=self.textcolor, anchor='s',
                                 justify='center')

    def formatWeight(self, weight):
        weight = str(weight)
        if len(weight) < 4:
            ed = 'кг'
        else:
            weight = int(weight) / 1000
            ed = 'тонн'
        return f"{weight} {ed}"

    def placeText(self, text, xpos, ypos, tag='maincanv', color='black',
                  font='deff', anchor='center'):
        if font == 'deff': font = self.font
        xpos = int(xpos)
        ypos = int(ypos)
        self.can.create_text(xpos, ypos, text=text, font=self.font, tag=tag,
                             fill=color, anchor=anchor)

    def placeCalendars(self):
        self.startCal = MyDateEntry(self.root, date_pattern='dd/mm/yy')
        self.startCal.config(width=7, font=fonts.statistic_calendars)
        self.endCal = MyDateEntry(self.root, date_pattern='dd/mm/yy')
        self.endCal.config(width=7, font=fonts.statistic_calendars)
        # self.startCal['style'] = 'stat.TCombobox'
        # self.endCal['style'] = 'stat.TCombobox'
        self.startCal['style'] = 'orup.TCombobox'
        self.endCal['style'] = 'orup.TCombobox'

        self.can.create_window(self.w / 3.86, self.h / 3.85,
                               window=self.startCal,
                               tags=('statCal'))
        self.can.create_window(self.w / 2.75, self.h / 3.85,
                               window=self.endCal,
                               tags=('statCal'))
        self.statisticInteractiveWidgets.append(self.startCal)
        self.statisticInteractiveWidgets.append(self.endCal)
        self.calendarsDrawn = True

    def drawing(self):
        super().drawing()
        self.drawWin('maincanv', 'statisticwin')
        if not self.calendarsDrawn:
            self.placeCalendars()
        self.get_history()
        self.draw_stat_tree()
        self.show_widgets(self.statisticInteractiveWidgets)

    def get_history(self):
        """ Запрашивает истоию заездов у GCore """
        trash_cat = self.operator.get_trash_cat_id(
            self.stat_page_trash_cat_var.get())
        trash_type = self.operator.get_trash_type_id(
            self.stat_page_trash_type_var.get())
        carrier = self.operator.get_client_id(self.stat_page_carrier_var.get())
        auto = self.operator.get_auto_id(self.stat_page_carnum_cb.get())
        platform_id = self.operator.get_polygon_platform_id(
            self.stat_page_polygon_combobox.get())
        pol_object_id = self.operator.get_polygon_object_id(
            self.stat_page_pol_object_combobox.get())
        client = self.operator.get_client_id(self.stat_page_clients_var.get())
        self.operator.ar_qdk.get_history(
            time_start=self.startCal.get_date(),
            time_end=self.endCal.get_date(),
            trash_cat=trash_cat,
            trash_type=trash_type,
            carrier=carrier, auto_id=auto,
            polygon_object_id=pol_object_id,
            client=client, platform_id=platform_id
        )

    # statistic.py (добавить/заменить эту функцию в классе StatisticPage)
    def refresh_stat_tree(self, records, operator):
        """
        Обновляет self.tree без мерцания, строго следуя формату
        HistroryTreeview.insertRec.
        """
        tree = self.tree
        mv_date = self.tar.getMovedDate  # формат дат «как в таблице»
        existing = set(tree.get_children())  # все текущие iids
        processed = set()

        for rec in records:
            act_id = rec['act_number'] if rec['package_id'] else rec['record_id']
            iid = str(rec['record_id'])  # ttk.Treeview.iid → строка

            # === значения в порядке columns = ("1","10","2","3","4","5","6","7","8","9","11") ===
            values = (
                rec['car_number'] or '-',  # "1"
                operator.get_client_repr(rec['client_id']) or '-',  # "10"
                operator.get_client_repr(rec['carrier']) or '-',  # "2"
                rec['brutto'] if rec['brutto'] is not None else '-',  # "3"
                rec['tara'] if rec['tara'] is not None else '-',  # "4"
                rec['cargo'] if rec['cargo'] is not None else '-',  # "5"
                operator.get_trash_cat_repr(rec['trash_cat']) or '-',  # "6"
                operator.get_trash_type_repr(rec['trash_type']) or '-',  # "7"
                mv_date(rec['time_in']),  # "8"
                mv_date(rec['time_out']),  # "9"
                rec['full_notes'],  # "11"
            )
            tags = ('usual',)

            if iid in existing:
                #   строка уже есть → обновляем при расхождениях
                item = tree.item(iid)
                if item["text"] != act_id or item["values"] != values:
                    tree.item(iid, text=act_id, values=values, tags=tags)
            else:
                #   новой строки ещё нет → вставляем через tar.insertRec,
                #   чтобы не дублировать логику вычисления нетто и т.п.
                self.tar.insertRec(
                    id=act_id,
                    car_number=rec['car_number'],
                    carrier=operator.get_client_repr(rec['carrier']),
                    brutto=rec['brutto'],
                    tara=rec['tara'],
                    cargo=rec['cargo'],
                    trash_cat=operator.get_trash_cat_repr(rec['trash_cat']),
                    trash_type=operator.get_trash_type_repr(rec['trash_type']),
                    time_in=rec['time_in'],
                    time_out=rec['time_out'],
                    notes=rec['full_notes'],
                    client=operator.get_client_repr(rec['client_id']),
                    tags=tags,
                    record_id=rec['record_id'],
                )
            processed.add(iid)

        # удалить лишние строки
        for iid in existing - processed:
            tree.delete(iid)

        # сортировка остаётся прежней
        self.tar.sortId(tree, '#0', reverse=True)

    def draw_stat_tree(self, tree=None):
        self.can.delete('tree')
        if not tree:
            tree = self.tree
        try:
            self.tar.sortId(tree, '#0', reverse=True)
        except TypeError:
            pass
        self.can.create_window(self.w / 1.9, self.h / 1.7,
                               window=tree,
                               tag='tree')

    def openWin(self):
        super(Statistic, self).openWin()
        self.show_main_navbar_btns()
        self.hide_weight()
        self.changed_record = None
        self.root.bind("<Double-Button-1>",
                       lambda event: self.clear_optionmenu(event))
        self.root.bind('<Escape>',
                       lambda event: self.operator.mainPage.openWin())

    def page_close_operations(self):
        super(Statistic, self).page_close_operations()
        self.changed_record = None
        self.hide_widgets(self.statisticInteractiveWidgets)
        self.root.unbind("<Button-1>")
        self.can.delete('amount_weight', 'statusel', 'tree')
        self.hide_main_navbar_btns()

    def initBlockImg(self, name, btnsname=None, slice='shadow', mode='new',
                     seconds=[], hide_widgets=[], **kwargs):
        super(Statistic, self).initBlockImg(name, btnsname)
        self.hide_widgets(self.statisticInteractiveWidgets)
        self.hide_widgets(self.page_buttons)
        self.hide_main_navbar_btns()

    def destroyBlockImg(self, mode='total'):
        super(Statistic, self).destroyBlockImg()
        self.tree.lift()
        self.show_widgets(self.statisticInteractiveWidgets)
        self.show_widgets(self.page_buttons)
        self.show_main_navbar_btns()
        self.show_time()
        self.place_amount_info(
            self.operator.statPage.weight_sum,
            self.operator.statPage.records_amount,
            tag='amount_info')
