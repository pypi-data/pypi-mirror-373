import datetime
from wsqluse import wsqluse
from gtki_module_exex.mixins import XlsCreator, TemplateCreator, DataFiller, \
    IshbDailyReportTemplate
from ar_qdk.main import ARQDK


class CreateExcel(XlsCreator, TemplateCreator, DataFiller):
    def __init__(self, file_name, data_list, column_names=None):
        if column_names:
            self.column_names = column_names
        self.data_list = data_list
        self.file_name = file_name
        self.workbook = self.create_workbook()
        self.worksheet = self.create_worksheet()

    def create_document(self):
        self.create_template()
        row_num = 1
        for row in self.data_list:
            self.create_row(row, row_num)
            row_num += 1
        self.workbook.close()


class CreateExcelActs(CreateExcel):
    def __init__(self, file_name, acts_list, amount_info,
                 column_names=None):
        super().__init__(file_name, acts_list, column_names)
        self.amount_info = amount_info

    def create_amount(self, amount_info):
        merge_format = self.workbook.add_format({'align': 'center',
                                                 'bold': True})
        merge_format.set_font_size(14)
        self.worksheet.merge_range('A2:L2', amount_info, merge_format)

    def create_document(self):
        self.create_template()
        self.create_amount(self.amount_info)
        row_num = 2
        for row in self.data_list:
            self.create_row(row, row_num)
            row_num += 1
        self.workbook.close()


class CreateExcelDailyReport(XlsCreator):
    def __init__(self, file_name, ar_ip, ar_port,
                 column_names=None):
        self.file_name = file_name
        self.ar_qdk = ARQDK(ip=ar_ip, port=ar_port)
        self.ar_qdk.make_connection()
        self.workbook = self.create_workbook()
        self.worksheet = self.create_worksheet()
        # super().__init__(file_name, acts_list, column_names)
        self.column_names = ["Категория", "Клиент", "Перевозчик",
                             "Количество \nрейсов",
                             "Общий вес,\nтонн", "Выручка, руб.", "Ошибки"]
        self.header_format = self.workbook.add_format({'bold': True,
                                                       'align': 'center',
                                                       'valign': 'center',
                                                       'font_size': 11})
        self.header_format.set_font_size(11)
        self.header_format.set_center_across()
        self.amount_format = self.header_format = self.workbook.add_format(
            {'bold': True,
             'font_size': 11})

    def create_day_header(self, day=None):
        merge_format = self.workbook.add_format({'align': 'center'})
        merge_format.set_font_size(14)
        self.worksheet.merge_range('A1:G1', day, merge_format)

    def operate_trash_cat(self, trash_cat, day, start_row):
        print("WORKING WITH", trash_cat)
        records = self.ar_qdk.execute_method("get_daily_report_by_trash_cat",
                                             trash_cat=trash_cat,
                                             day=day,
                                             except_car_numbers=('Н370УЕ102'),
                                             get_response=True)
        if records['status']:
            records = records['info']
        if not records:
            return
        trash_cat_row = start_row + 1
        self.worksheet.write(trash_cat_row, 0, trash_cat, self.amount_format)
        record_row = trash_cat_row
        for rec in records:
            if (rec['client_name'] == 'Физлицо' or rec[
                'carrier_name'] == 'Физлицо' or
                    rec['client_name'] == 'ИПБутыринИ.А.' or rec[
                        'carrier_name'] == 'ИПБутыринИ.А.'):
                record_row += 1
                continue
            self.set_record(rec['client_name'], rec['carrier_name'],
                            rec['amount'], rec['tonnage'], record_row)
            record_row += 1
        return self.set_amount(start_row, record_row)

    def get_amount(self, records):
        amount = 0
        tonnage = 0
        for rec in records:
            amount += rec['amount']
            tonnage += rec['tonnage']
        return amount, tonnage

    def set_record(self, client, carrier, amount, tonnage, start_row):
        record_format = self.workbook.add_format()
        self.worksheet.write(start_row, 1, client, record_format)
        self.worksheet.write(start_row, 2, carrier, record_format)
        self.worksheet.write(start_row, 3, amount, record_format)
        self.worksheet.write(start_row, 4, tonnage, record_format)
        return

    def set_amount(self, start_record_row, end_record_row, alias="ИТОГО:"):
        amount_format = self.header_format = self.workbook.add_format(
            {'bold': True,
             'font_size': 12})
        self.worksheet.write(end_record_row + 1, 0, alias,
                             self.header_format)
        self.worksheet.write_formula(end_record_row + 1, 3,
                                     f"=SUM(D{start_record_row + 2}:D{end_record_row})",
                                     amount_format)
        self.worksheet.write_formula(end_record_row + 1, 4,
                                     f"=SUM(E{start_record_row + 2}:E{end_record_row})",
                                     amount_format)
        return end_record_row

    def set_final_amount(self, end_record_row, rows, alias="ВСЕГО:"):
        final_format = self.workbook.add_format(
            {'bold': True,
             'font_size': 14})
        self.worksheet.write(end_record_row + 1, 0, alias,
                             final_format)
        amount_func = f"=SUM({'+'.join([f'D{row}' for row in rows])})"
        tonnage_func = f"=SUM({'+'.join([f'E{row}' for row in rows])})"
        self.worksheet.write_formula(end_record_row + 1, 3,
                                     amount_func,
                                     final_format)
        self.worksheet.write_formula(end_record_row + 1, 4,
                                     tonnage_func,
                                     final_format)
        return end_record_row

    def create_document(self, day=None):
        amounts = []
        if not day:
            day = datetime.datetime.now()
        self.create_day_header(day.strftime("%#d/%m/%Y"))
        self.set_column_width()
        start_row = self.set_column_names()
        new_row = start_row
        for tc in ["ТКО", "ПО", "Хвосты", "Прочее"]:
            response = self.operate_trash_cat(tc, day.strftime("%Y.%m.%d"),
                                            start_row=new_row)
            if response:
                new_row = response
                amounts.append(response + 2)
                new_row += 1
        hyn_row = self.add_hyundai(day, new_row)
        if hyn_row:
            amounts.append(hyn_row + 2)
            new_row = hyn_row
        phys_row = self.add_phys(day, new_row + 2)
        if phys_row:
            amounts.append(phys_row + 2)
            new_row = phys_row
        rec_row = self.add_recyclables(day, new_row + 2)
        if rec_row:
            amounts.append(rec_row + 2)
            new_row = rec_row
        row = self.set_amount(start_record_row=start_row,
                              end_record_row=new_row + 2, alias="ВСЕГО")
        row = self.set_final_amount(row, amounts)
        self.set_borders(row + 1)
        self.add_user_info(row)
        self.workbook.close()

    def add_user_info(self, row):
        row += 3
        current_user_info = self.ar_qdk.execute_method("get_current_user_info",
                                                       get_response=True)
        if not current_user_info['status']:
            return
        username = current_user_info['info'][0]['username']
        self.worksheet.write(row, 0, "Сдал:")
        self.worksheet.write(row, 1, username)
        self.worksheet.write(row, 3, "Подпись:")
        return row
        # self.worksheet.write(trash_cat_row, 0, "Физ.лицо", self.amount_format)

    def add_hyundai(self, day, start_row):
        records = self.ar_qdk.execute_method("get_daily_report_by_car_number",
                                             car_number='Н370УЕ102',
                                             day=day,
                                             get_response=True)
        if records['status']:
            records = records['info']
        if not records:
            return
        trash_cat_row = start_row + 1
        self.worksheet.write(trash_cat_row, 0, "ХУНДАЙ", self.amount_format)
        record_row = trash_cat_row
        for rec in records:
            self.set_record(rec['client_name'], rec['carrier_name'],
                            rec['amount'], rec['tonnage'], record_row)
            record_row += 1
        return self.set_amount(start_row, record_row)

    def add_phys(self, day, start_row):
        records = self.ar_qdk.execute_method("get_daily_report_by_client",
                                             client='Физлицо',
                                             day=day,
                                             get_response=True)
        if records['status']:
            records = records['info']
        if not records:
            return
        trash_cat_row = start_row + 1
        self.worksheet.write(trash_cat_row, 0, "Физ.лицо", self.amount_format)
        record_row = trash_cat_row
        for rec in records:
            self.set_record(rec['client_name'], rec['carrier_name'],
                            rec['amount'], rec['tonnage'], record_row)
            record_row += 1
        return self.set_amount(start_row, record_row)

    def add_recyclables(self, day, start_row):
        records = self.ar_qdk.execute_method("get_daily_report_by_client",
                                             client='ИПБутыринИ.А.',
                                             day=day,
                                             get_response=True)
        if records['status']:
            records = records['info']
        if not records:
            return
        trash_cat_row = start_row + 1
        self.worksheet.write(trash_cat_row, 0, "Вторсырье", self.amount_format)
        record_row = trash_cat_row
        for rec in records:
            self.set_record(rec['client_name'], rec['carrier_name'],
                            rec['amount'], rec['tonnage'], record_row)
            record_row += 1
        return self.set_amount(start_row, record_row)

    def set_borders(self, last_row):
        border_format = self.workbook.add_format()
        border_format.set_border()
        self.worksheet.conditional_format(f'A2:G{last_row + 1}',
                                          {'type': 'no_blanks',
                                           'format': border_format})
        self.worksheet.conditional_format(f'A2:G{last_row + 1}',
                                          {'type': 'blanks',
                                           'format': border_format})

    def set_column_names(self):
        col_num = 0
        self.worksheet.set_row_pixels(1, 42)
        for col_name in self.column_names:
            self.worksheet.write(1, col_num, col_name, self.header_format)
            col_num += 1
        return 1

    def set_column_width(self):
        self.worksheet.set_column_pixels(0, 0, 109)
        self.worksheet.set_column_pixels(1, 1, 198)
        self.worksheet.set_column_pixels(2, 2, 169)
        self.worksheet.set_column_pixels(3, 3, 78)
        self.worksheet.set_column_pixels(4, 4, 101)
        self.worksheet.set_column_pixels(5, 5, 99)
        self.worksheet.set_column_pixels(6, 6, 156)
