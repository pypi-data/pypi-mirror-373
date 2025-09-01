import socket
import time
import traceback
from time import sleep
import logging
from traceback import format_exc
from cm.configs import config as s
import pickle
import threading


class WListener:
    '''Прослушиватель ком портов, к которым линкуются периферийные
    железки, при создании экземпляра необходимо задать имя железки,
    номер ком-порта, порт'''

    def __init__(self, name='def', comnum='25', port='1488', bs=8, py='N',
                 sb=1, to=1, ip='localhost', ar_ip='localhost',
                 scale_port=2297):
        self.name = name
        self.scale_port = int(scale_port)
        self.ip = ip
        self.comnum = comnum
        self.port = port
        self.bs = bs
        self.ar_ip = ar_ip
        self.sb = sb
        self.to = to
        self.py = py
        self.weight = '5'
        self.activity = True

    def scale_reciever(self, scale_ip):
        while True:
            try:
                client = self.connect_cps(scale_ip)
                self.interact_cps(client)
            except (ConnectionRefusedError, ConnectionResetError) as err:
                print(traceback.format_exc())
                self.weight = "8"
                sleep(1)

    def connect_cps(self, scale_ip):
        while True:
            try:
                client = socket.socket()
                client.connect((scale_ip, self.scale_port))
                return client
            except:
                print(f'Не удалось подключиться к сереру рассылки {scale_ip}:{self.scale_port}'
                      'данных с весового терминала. Повтор ... ')
                sleep(1)

    def interact_cps(self, client):
        while True:
            data = client.recv(1024)
            if not data: break
            data = data.decode(encoding='utf-8')
            data = data.split('X0')[0]
            self.weight = data
            time.sleep(0.25)

