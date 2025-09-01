""" Файл содержит информацию обо всех ошибках ОРУП. Основное содержимое - словари для ОРУП брутто и ОРУП тара.
Содержимое словаря - ключи:
    chek_func - функция из модуля check_funcs, которое возвращает True или False (алерт сработал или нет),
    description - текст-описание,
    error_text - текст предупреждение, которое видит весовщик,
    shown - была показана эта ошибка или нет,
    skippable - можно ли алерт проигнорировать, нажав на Принять или же нет
    tests - переменные для тестирования функции check_func"""
from cm.modules.orup_errors import check_funcs

general_errors_dict = {'AR_busy':
                           {'check_func': check_funcs.check_ar_busy,
                            'description': 'AR при проверке статуса возращает статус "Занят"',
                            'error_text':
                                "Программа занята обработкой другой машины.\n"
                                "Если ошибка не исчезает - свяжитесь с технической поддержкой.",
                            'shown': False,
                            'active': True,
                            'skippable': True,
                            'tests': {'correct_values': {'ar_status': 'Готов'},
                                      'incorrect_values': {'ar_status': 'Занят'}}},

                       'car_have_rfid':
                           {'check_func': check_funcs.check_car_has_rfid,
                            'description': 'Попытка ручного пропуска машины с меткой или картой',
                            'error_text': "У данного авто установлена метка RFID."
                                          "\nДобавьте комментарий и нажмите 'Принять' еще раз",
                            'shown': False,
                            'active': True,
                            'skippable': False,
                            'tests': {'correct_values': {'have_rfid': True, 'choose_mode': 'auto'},
                                      'incorrect_values': {'have_rfid': True, 'choose_mode': 'manual'}}},

                       'scale_error':
                           {'check_func': check_funcs.check_scale_fail,
                            'description': 'Проблема с весовым терминалом',
                            'error_text': "Не удается получить данные с весового терминала.\n"
                                          "Пожалуйста, проверьте терминал и свяжитесь с технической поддержкой.",
                            'shown': False,
                            'active': True,
                            'skippable': False,
                            'tests': {'correct_values': {'weight_data': 50},
                                      'incorrect_values': {'weight_data': 51}}
                            },

                       'tara_without_brutto_try':
                           {'check_func': check_funcs.check_brutto_on_exit,
                            'description': 'Машина (car_protocol=rfid) пытается взвесить брутто с внутренней стороны',
                            'error_text': "У данной машины нет брутто. (Протокол ТКО: въезд=брутто, выезд=тара)"
                                          "\nПожалуйста, проверьте, не допустили ли вы ошибку в вводе гос.номера ранее.\n"
                                          "Если допущена ошибка, измените гос.номер в акте через окно 'Статистика', и взвесьте тару",
                            'shown': False,
                            'active': True,
                            'skippable': False,
                            'tests': {'correct_values': {'course': 'OUT', 'have_brutto': False, 'chosen_trash_cat': 'ТКО'},
                                      'incorrect_values': {'course': 'OUT', 'have_brutto': False,
                                                           'car_protocol': 'rfid'}}
                            },

                       'double_brutto_try':
                           {'check_func': check_funcs.check_brutto_having_brutto,
                            'description': 'Попытка взвесить брутто дважды '
                                           '(Тачка опять подъехала с въезда, а выезда нет)',
                            'error_text': "У этой машины уже есть брутто. (Проткол ТКО - въезд=брутто, выезд=тара)\n"
                                          "\nПожалуйста, взвесьте сначала тару с другой стороны весов",
                            'shown': False,
                            'active': True,
                            'skippable': False,
                            'tests': {'correct_values': {'course': 'IN', 'have_brutto': False, 'car_protocol': 'rfid'},
                                      'incorrect_values': {'course': 'IN', 'have_brutto': True, 'car_protocol': 'rfid'}}
                            },
                       }

orup_brutto_errors = {'other_instead_tko':
                          {'check_func': check_funcs.other_instead_tko,
                           'description': 'Привезли другую категорию, хотя запланировано было ТКО',
                           'error_text':
                               "Ожидалось, что машина привезла ТКО-4.\n "
                               "Пожалуйста, уточните информацию прежде чем продолжать",
                           'shown': False,
                           'active': False,
                           'skippable': True,
                           'tests': {'correct_values': {'chosen_trash_cat': 'ТКО-4'},
                                     'incorrect_values': {'chosen_trash_cat': 'other'}}
                           },

                      'tko_instead_other':
                          {'check_func': check_funcs.tko_instead_other,
                           'description': 'Привезли ТКО, хотя рейс не запланирован',
                           'error_text':
                               "В системе не найдено запланнированных заездов с ТКО для этой машины.\n "
                               "Пожалуйста, уточните информацию, прежде чем продолжить",
                           'shown': False,
                           'active': False,
                           'skippable': True,
                           'tests': {'correct_values': {'chosen_trash_cat': 'other'},
                                     'incorrect_values': {'chosen_trash_cat': 'ТКО-4'}}
                           },

                      'tko_not_allowed':
                          {'check_func': check_funcs.tko_not_allowed,
                           'description': 'Привезли ТКО с запрещенной организации',
                           'error_text':
                               "Данная организация не может перевозить ТКО!\n"
                               "Свяжитесь с Региональным Оператором.",
                           'shown': False,
                           'active': True,
                           'skippable': False,
                           'tests': {
                               'correct_values': {'chosen_trash_cat': 'other'},
                               'incorrect_values': {
                                   'chosen_trash_cat': 'ТКО-4',}}
                           },

                      'incorrect_car_number':
                          {'check_func': check_funcs.check_car_number,
                           'description': 'Не ввели гос. номер',
                           'error_text': "Необходимо ввести государственный номер авто.\n"
                                         "Например, А111АА111 (8 или 9 символов)",
                           'shown': False,
                           'active': True,
                           'skippable': False,
                           'tests': {'correct_values': {'car_number': 'ВХ060ХА702'},
                                     'incorrect_values': {'car_number': '{102ХА102'}}
                           },

                      'incorrect_carrier':
                          {'check_func': check_funcs.check_carrier_incorrectness,
                           'description': 'Некорректное название перевозчика',
                           'error_text': 'Некорректное название перевозчика.'
                                         '\nПожалуйста, проверьте правильность набора названия организации.',
                           'shown': False,
                           'active': True,
                           'skippable': False,
                           'tests': {'correct_values': {'carrier_name': 'TEST', 'carriers_list': ['TEST']},
                                     'incorrect_values': {'carrier_name': 'TEST', 'carriers_list': ['TEST2']}}},
                      'incorrect_client':
                          {
                              'check_func': check_funcs.check_client_incorrectness,
                              'description': 'Некорректное название клиента',
                              'error_text': 'Некорректное название клиента.'
                                            '\nПожалуйста, проверьте правильность набора названия организации.',
                              'shown': False,
                              'active': True,
                              'skippable': False,
                              'tests': {
                                  'correct_values': {'carrier_name': 'TEST',
                                                     'carriers_list': [
                                                         'TEST']},
                                  'incorrect_values': {'carrier_name': 'TEST',
                                                       'carriers_list': [
                                                           'TEST2']}}},

                      'incorrect_object':
                          {
                              'check_func': check_funcs.check_object_incorrectness,
                              'description': 'Некорректное название объекта',
                              'error_text': 'Некорректное название объекта.'
                                            '\nПожалуйста, проверьте правильность набора названия объекта.',
                              'shown': False,
                              'active': True,
                              'skippable': False,
                              'tests': {
                                  'correct_values': {'carrier_name': 'TEST',
                                                     'carriers_list': [
                                                         'TEST']},
                                  'incorrect_values': {'carrier_name': 'TEST',
                                                       'carriers_list': [
                                                           'TEST2']}}},

                      'incorrect_platform':
                          {
                              'check_func': check_funcs.check_platform_incorrectness,
                              'description': 'Некорректное название площадки',
                              'error_text': 'Некорректное название площадки.'
                                            '\nПожалуйста, проверьте правильность набора названия площадки.',
                              'shown': False,
                              'active': True,
                              'skippable': False,
                              'tests': {
                                  'correct_values': {'carrier_name': 'TEST',
                                                     'carriers_list': [
                                                         'TEST']},
                                  'incorrect_values': {'carrier_name': 'TEST',
                                                       'carriers_list': [
                                                           'TEST2']}}},

                      'debtor_carrier':
                          {'check_func': check_funcs.check_carrier_debtor,
                           'description': 'Перевозчик в списке должников (статус 0 или False)',
                           'error_text': "Въезд для этого перевозчика запрещен!"
                                         "\nПричина: {}.\n"
                                         "Согласуйте заезд с офисом, добавьте комментарий и нажмите 'Принять' еще раз.",
                           'shown': False,
                           'active': False,
                           'skippable': False,
                           'tests': {'correct_values': {'carrier_name': 'TEST', 'debtors_list': ['TEST2']},
                                     'incorrect_values': {'carrier_name': 'TEST', 'debtors_list': ['TEST']}}
                           },
                      'debtor_client':
                          {'check_func': check_funcs.check_trash_cat_by_client,
                           'description': 'Клиент в списке должников (статус 0 или False)',
                           'error_text': "Для этого клиента данная категория груза запрещена!\nПоменяйте категорию груза или клиента!",
                           'shown': False,
                           'active': True,
                           'skippable': False,
                           'tests': {'correct_values': {'carrier_name': 'TEST',
                                                        'debtors_list': [
                                                            'TEST2']},
                                     'incorrect_values': {
                                         'carrier_name': 'TEST',
                                         'debtors_list': ['TEST']}}
                           },
                      'client_cat':
                          {'check_func': check_funcs.check_client_debtor,
                           'description': 'Клиент в списке должников (статус 0 или False)',
                           'error_text': "Въезд для этого клиента запрещен!"
                                         "\nПричина: {}.\n"
                                         "Согласуйте заезд с офисом, добавьте комментарий и нажмите 'Принять' еще раз.",
                           'shown': False,
                           'active': True,
                           'skippable': False,
                           'tests': {'correct_values': {'carrier_name': 'TEST',
                                                        'debtors_list': [
                                                            'TEST2']},
                                     'incorrect_values': {
                                         'carrier_name': 'TEST',
                                         'debtors_list': ['TEST']}}
                           },
                      'incorrect_trash_type':
                          {'check_func': check_funcs.check_tt_incorrectness,
                           'description': 'Некорректный вид груза',
                           'error_text': 'Некорретный вид груза.\n'
                                         'Пожалуйста, проверьте правильность набора названия вида груза',
                           'shown': False,
                           'active': True,
                           'skippable': False,
                           'tests': {'correct_values': {'type_name': 'TEST', 'types_list': ['TEST']},
                                     'incorrect_values': {'type_name': 'TEST', 'types_list': ['TEST2']}}},

                      'incorrect_trash_cat':
                          {'check_func': check_funcs.check_tc_incorrectness,
                           'desctiption': 'Некорректная категория груза',
                           'error_text': 'Некорректная категория груза.\n'
                                         'Пожалуйста, проверьте правильность набора названия категории груза',
                           'shown': False,
                           'active': True,
                           'skippable': False,
                           'tests': {'correct_values': {'chosen_trash_cat': 'TEST', 'cats_list': ['TEST']},
                                     'incorrect_values': {'chosen_trash_cat': 'TEST', 'cats_list': ['TEST2']}}}
                      }

orup_tara_errors = {}

orup_brutto_errors.update(general_errors_dict)
orup_tara_errors.update(general_errors_dict)

all_errors_dict = {'brutto':
                       {'errors_dict': orup_brutto_errors},
                   'tara':
                       {'errors_dict': orup_tara_errors}}
