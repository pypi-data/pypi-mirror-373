""" Общие функции """
from cm.modules.orup_errors import all_errors


def destroy_error_window(canvas, error_win_tag='errorwin', error_txt_tag='errorwintxt', *args, **kwargs):
    canvas.delete(error_win_tag, error_txt_tag)


def draw_error_window(canvas, text, xpos, ypos, photo_object, error_win_tag='errorwin', error_txt_tag='errorwintxt',
                      text_color='black', text_font='Times', *args, **kwargs):
    canvas.delete(error_txt_tag)                                                 # Удалить текст ошибки (если он был)
    canvas.create_image(xpos, ypos, image=photo_object, tag=error_win_tag)       # Создать окно ошибки (красный квадрат)
    # Создать текст
    canvas.create_text(xpos, ypos, text=text, font=text_font, fill=text_color, tags=(error_win_tag, error_txt_tag),
                       justify='center')



def check_orup_errors(orup_errors_dict, args_dict, *args, **kwargs):
    """ Перебирает словарь ошибок, передавая им словарь аргументов для проверки, возрващает первое совпадение"""
    for error_name, info_dict in orup_errors_dict.items():
        # Если функция проверки возбуждает алерт, и если алерт еще не показан или не пропускаемый - вернуть словарь
        try:
            check_result_incorrect = info_dict['check_func'](**args_dict)
            info_dict['check_result'] = check_result_incorrect
            if check_result_incorrect and (info_dict['skippable'] == False or not info_dict['shown'] and
                                           info_dict['skippable']) and info_dict['active']:
                return info_dict
        except TypeError: # Нет необходимых аргументов для проверки
            pass

def make_errors_unshown(args_dict, *args, **kwargs):
    """ Сделать для всех алертов unshown (пропустить заезд и сбросить счетчики) """
    for error_name, info_dict in args_dict.items():
        info_dict['shown'] = False


def get_errors_dict(orup_mode):
    """ Принимает orup_mode (brutto/tara) и возвращает нужный словарь """
    return all_errors.all_errors_dict[orup_mode]['errors_dict']



