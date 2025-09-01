""" Основной класс взаимодействия """
from cm.modules.orup_errors import general_functions
from cm.modules.orup_errors import all_errors


class OrupErrorsManager:
    def __init__(self, canvas, trash_types_list=None, trash_cats_list=None,
                 tko_name='ТКО-4', ar_busy_status='Занят',
                 *args, **kwargs):
        self.all_args = locals()
        self.all_args.update(kwargs)

    def check_orup_errors(self, orup, **all_args):
        """ Проверить данные перед началом взвешивания брутто. Получает все нужные аругементы для проверки и один
        обязатеьный аргумент orup, определяющий брутто это или тара (brutto/tara). Согласно этому значению будет
        перебираться соответствующий словарь. """
        # Сначала объединим атрибуты класса с аргументами метода
        # (что было изначально + что передали конкретно для этой проверки
        self.all_args.update(all_args)
        # Исходя из вида ORUP, извлекаем интересующий нас словарь ошибок (он разный для brutto и tara)
        errors_dict = general_functions.get_errors_dict(orup)
        check_result = general_functions.check_orup_errors(errors_dict,
                                                           self.all_args)
        # Если найдет причину для алерта
        if check_result:
            # Нарисуем табличку с заданным текстом
            general_functions.draw_error_window(text=check_result['error_text'].format(check_result['check_result']), **self.all_args)
            check_result['shown'] = True        # Промаркируем, что алерт показан
            return check_result                 # Вернем информацию об алерте
        # Если же нет - удалит окно, сбросит счетчики и вернет None
        else:
            general_functions.destroy_error_window(**self.all_args)
            general_functions.make_errors_unshown(all_errors.orup_brutto_errors)
