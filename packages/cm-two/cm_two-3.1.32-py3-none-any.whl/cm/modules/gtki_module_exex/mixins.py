import xlsxwriter


class XlsCreator:
    file_name = None
    workbook = None

    def create_workbook(self):
        return xlsxwriter.Workbook(self.file_name)

    def create_worksheet(self):
        return self.workbook.add_worksheet()




class TemplateCreator:
    worksheet = None
    workbook = None
    column_names = [
        'ID', 'Гос.Номер', 'Клиент', 'Перевозчик',
        'Брутто', 'Тара', 'Нетто', 'Категория груза',
        'Вид груза', 'Дата въезда', 'Дата выезда',
        'Комментарии'
    ]

    def create_template(self):
        bold = self.workbook.add_format({'bold': True, 'bg_color': 'yellow'})
        bold.set_font_size(14)
        col_num = 0
        for col_name in self.column_names:
            self.worksheet.write(0, col_num, col_name, bold)
            col_num += 1


class IshbDailyReportTemplate(TemplateCreator):
    column_names = ["Категория", "Клиент", "Перевозчик", "Количество рейсов",
                    "Общий вес, тонн", "Выручка, руб.", "Ошибки"]


class DataFiller:
    worksheet = None

    def create_row(self, data_list, row_num=1):
        col_num = 0
        for data in data_list:
            self.worksheet.write(row_num, col_num, data)
            col_num += 1

