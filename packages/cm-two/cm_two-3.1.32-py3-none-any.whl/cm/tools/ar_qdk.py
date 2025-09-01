""" Модуль содержит основной класс для работы с AR (Gravity One) """

from qdk.main import QDK


class ARQDK(QDK):
    """ Основной класс для взаимодействия с AR Gravity One """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def execute_method(self, method_name, get_response=False, *args, **kwargs):
        print(f"\nSending to AR method - {method_name}. "
              f"With args {args}, kwargs - {kwargs}. "
              f"Get response - {get_response}")
        return super(ARQDK, self).execute_method(
            method_name=method_name, get_response=get_response, *args,
            **kwargs)

    def get_status(self):
        """
        Извлечь статус AR.

        :return:
        """
        return self.execute_method('get_status')

    def start_car_protocol(self, info):
        """
        Начать заезд.

        :param info: Словарь с необходимой информацией.
        :return:
        """
        return self.execute_method('start_weight_round', info=info)

    def add_comment(self, record_id, comment):
        """
        Добавить комментарий к заезду.

        :param record_id: id записи.
        :param comment: Комментарий.
        :return:
        """
        return self.execute_method('add_comment', record_id=record_id,
                                   comment=comment)

    def operate_gate_manual_control(self, operation, gate_name,
                                    auto_close=False, smart_auto_close=False,
                                    *args, **kwargs):
        """
        Работа со шлагбаумами.

        :param operation: Название операции (close|open):
        :param gate_name: Имя шлагбаума (entry/exit)
        :return:
        """
        return self.execute_method('operate_gate_manual_control',
                                   smart_auto_close=smart_auto_close,
                                   operation=operation, gate_name=gate_name,
                                   auto_close=auto_close, *args, **kwargs)

    def change_opened_record(self, record_id, auto_id, car_number, carrier,
                             trash_cat_id, trash_type_id, comment, pol_object,
                             client=None, polygon=None):
        """
        Изменить открытую запись.

        :param record_id: id зписи.
        :param auto_id: id авто.
        :param car_number: гос. номер авто.
        :param carrier: id перевозчика.
        :param trash_cat_id: id категории груза.
        :param trash_type_id: id вида груза.
        :param comment: комментарий весовщика.
        :param polygon: id полигона.
        :return:
        """
        return self.execute_method('change_opened_record', record_id=record_id,
                                   auto_id=auto_id, car_number=car_number,
                                   carrier=carrier, trash_cat_id=trash_cat_id,
                                   trash_type_id=trash_type_id,
                                   comment=comment, polygon=polygon,
                                   client=client, pol_object=pol_object)

    def close_opened_record(self, record_id, time_out=None):
        """
        Закрыть открытую запись.

        :param record_id: id записи.
        :param time_out: время выезда.
        :param alert: Алерт закрытия.
        :return:
        """
        return self.execute_method('close_opened_record', record_id=record_id,
                                   time_out=time_out)

    def get_unfinished_records(self):
        """
        Получить все незаконченные заезды (заезды без тары).

        :return:
        """
        return self.execute_method('get_unfinished_records')

    def get_health_monitor(self):
        """
        Получить состояние монитора здоровья.

        :return:
        """
        return self.execute_method('get_health_monitor')

    def try_auth_user(self, username, password):
        """
        Попытка аутентификации юзера.

        :param username: Логин пользователя.
        :param password: Пароль пользователя.
        :return:
        """
        return self.execute_method('try_auth_user', username=username,
                                   password=password)

    def capture_cm_launched(self):
        """
        Зафиксировать запуск СМ.

        :return:
        """
        return self.execute_method('capture_cm_launched')

    def capture_cm_terminated(self):
        """
        Зафиксировать завершение СМ.

        :return:
        """
        return self.execute_method('capture_cm_terminated')

    def get_history(self, time_start, time_end, what_time='time_in',
                    trash_cat=None, trash_type=None, carrier=None,
                    auto_id=None, polygon_object_id=None, client=None,
                    platform_id=None):
        """
        Получить историю заездов.

        :return:
        """
        return self.execute_method('get_history', time_start=time_start,
                                   time_end=time_end, what_time=what_time,
                                   trash_cat=trash_cat, trash_type=trash_type,
                                   carrier=carrier, auto_id=auto_id,
                                   polygon_object_id=polygon_object_id,
                                   client=client, platform_id=platform_id)

    def get_table_info(self, table_name, only_active=True):
        """
        Получить содержимое таблицы.

        :param table_name: Имя таблицы.
        :param only_active: Только активные записи?
        :return:
        """
        return self.execute_method('get_table_info', tablename=table_name)

    def get_last_event(self, auto_id):
        """
        Получить данные о последнем заезде авто.

        :param auto_id: ID авто.
        :return:
        """
        return self.execute_method('get_last_event', auto_id=auto_id)

    def restart_unit(self):
        return self.execute_method('restart_unit')

    def catch_orup_decline(self, car_number, mode="no info"):
        return self.execute_method('capture_orup_decline',
                                   car_number=car_number,
                                   mode=mode)

    def catch_orup_accept(self, car_number):
        return self.execute_method('capture_orup_accept',
                                   car_number=car_number)

    def catch_window_switch(self, window_name):
        return self.execute_method('capture_window_switch',
                                   window_name=window_name)

    def abort_round(self):
        return self.execute_method('abort_round')

    def cancel_photocell_waiting(self):
        return self.execute_method('cancel_photocell_waiting')

    def delete_record_hard(self, table_name, record_id):
        return self.execute_method('delete_record_hard', table_name=table_name,
                                   record_id=record_id)

    def delete_record_soft(self, table_name, record_id):
        return self.execute_method('delete_record_soft', table_name=table_name,
                                   record_id=record_id)

    def get_record_info(self, table_name, record_id):
        return self.execute_method('get_record_info', table_name=table_name,
                                   record_id=record_id)

    def add_carrier(self, name: str, full_name: str, inn: str, status: str,
                    kpp: str, access: int, wserver_id: int, id_1c: str,
                    active: bool = True):
        return self.execute_method('add_carrier', name=name,
                                   full_name=full_name, inn=inn, status=status,
                                   kpp=kpp, access=access,
                                   wserver_id=wserver_id, id_1c=id_1c,
                                   active=active)

    def upd_carrier(self, client_id, name=None, full_name=None, active=None,
                    wserver_id=None, status=None, inn=None, kpp=None,
                    access: int = None, id_1c: str = None):
        return self.execute_method('upd_carrier', client_id=client_id,
                                   name=name, full_name=full_name,
                                   active=active, wserver_id=wserver_id,
                                   status=status, inn=inn, kpp=kpp,
                                   access=access, id_1c=id_1c)

    def cancel_tare(self, record_id):
        return self.execute_method(
            'cancel_tare', record_id=record_id
        )
