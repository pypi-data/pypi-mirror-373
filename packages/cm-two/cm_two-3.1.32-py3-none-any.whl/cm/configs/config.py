import os

rootdir = os.getcwd()
CUR_DIR = os.path

# ДБ
auto = 'auto'
book = 'records'
special_protocols = 'special_protocols'
clients_table = 'clients'
auto_table = 'auto'
trash_types_table = 'trash_types'
trash_cats_table = 'trash_cats'
polygon_objects_table = 'duo_pol_owners'
disputs_table = 'disputs'
users_table = 'users'

tables_info = {'auto':
                   {'repr': 'car_number',
                    'loading_description': 'Загружаю базу автомобилей'},
               'clients':
                   {'repr': 'name',
                    'loading_description': 'Загружаю базу перевозчиков'},
               'users':
                   {'repr': 'username',
                    'loading_description': 'Загружаю базу пользователей'},
               'trash_cats':
                   {'repr': 'name',
                    'loading_description': 'Загружаю базу категорий грузов'},
               'trash_types':
                   {'repr': 'name',
                    'loading_description': 'Загружаю базу видов грузов'},
               'duo_pol_owners':
                   {'repr': 'name',
                    'loading_description': 'Загружаю базу организаций на объекте'},
               'pol_objects': {
                   'repr': 'name',
                   'loading_description': 'Загружаю объекты'},
               'trash_cats_types':
                   {'repr': 'id',
                    'loading_description': 'Почти все готово...'},
               'platform_pol_objects_mapping':
                   {'repr': 'id',
                    'loading_description': 'Почти все готово...'},

               }

# Настройки сокета для получения комманд от Watchman-CM
ar_ip = '192.168.100.118'
cmUseInterfacePort = 2292

# Настройка сокета для передачи статуса  Watchman-CM
statusSocketPort = 2291

# Сервер рассылки показаний с весов
scale_splitter_port = 2297

'''Пакет конфигурации для Watchman-MC'''

wrip = 'localhost'
wrport = 2296

# ОРУП
allowed_carnum_symbols = ['А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т',
                          'У',
                          'Х', 'а', 'в', 'е', 'к', 'м', 'н', 'о', 'р', 'с',
                          'т', 'у', 'х']

gates_info = {'entry': {'name': 'entry', 'num': 1,
                        'open_anim_command': 'self.open_entry_gate_operation_start()',
                        'close_anim_command': 'self.close_entry_gate_operation_start()'},
              'exit': {'name': 'exit', 'num': 2,
                       'open_anim_command': 'self.open_exit_gate_operation_start()',
                       'close_anim_command': 'self.close_exit_gate_operation_start()'},
              }
