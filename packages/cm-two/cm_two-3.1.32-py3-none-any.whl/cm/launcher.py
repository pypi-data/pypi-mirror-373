""" Лаунчер Gravity interface """
from tkinter import *
from cm.configs.settings import Settings
from cm.main_operator import *
from cm.wlistener import WListener
from traceback import format_exc
import screeninfo
import os
import platform
import time
from cm.tools.ar_qdk import ARQDK
from tkinter import ttk
#from cm.styles.styles import *


monitors = screeninfo.get_monitors()
width = monitors[0].width
height = monitors[0].height
deffaultScreenSize = (width, height)
dirpath = os.path.dirname(os.path.realpath(__file__))
img_dir = os.path.join(dirpath, 'imgs')
loadingWin = os.path.join(img_dir, 'loadingWin.png')

root = Tk()
if platform.system() == "Windows":
    root.wm_state("zoomed")
elif platform.system() == "Linux":
    root.attributes('-zoomed', True)

loadingcan = Canvas(root, highlightthickness=0)
loadingcan.pack(fill=BOTH, expand=YES)
photoimg = PhotoImage(file=loadingWin, master=root)
loadingcan.create_image(width / 2, height / 2, image=photoimg)
loadingcan.create_text(width / 2, height / 2 * 1.24, text='Добро пожаловать',
                       font=fonts.loading_welcome_font,
                       fill='white', tag='loadingtext')


def set_exit_button(root, can):
    exit_img = PhotoImage(file=os.path.join(img_dir, "exit.png"))

    # Сохраняем изображение на объект root, чтобы не удалилось
    root.exit_img = exit_img

    # Передаём функцию с аргументом правильно
    button = ttk.Button(
        root,
        command=lambda: close_app(root),  # вызываем функцию
        padding='0 0 0 0',
        takefocus=False,
        image=exit_img,  # используем сохранённую картинку
        cursor='hand2'
    )
    button['width'] = 0
    button['style'] = "authWinBtn.TButton"
    can.create_window(1874.47, 54.29, window=button, tag="button")


set_exit_button(root, loadingcan)

def close_app(root):
    root.destroy()
    time.sleep(1)
    sys.exit(0)

def check_double():
    """ Проверить, запущена ли уже программа """
    from cm_adb import client, server
    ip, port, msg = 'localhost', 1333, 'MSG'
    try:
        client.client(ip, port, msg)
        return True
    except ConnectionRefusedError:
        server.CMADBServer(ip, port)._start()


def destroy_this_copy():
    loadingcan.delete('loadingtext')
    root.attributes('-fullscreen', True)
    loadingcan.create_text(
        width / 2, height / 2 * 1.24,
        text='Программа уже запущена, вы пытаетесь запустить ее повторно!'
             '\nЕсли это не так, позвоните в тех. поддержку.',
        font=fonts.loading_status_font, fill='white',
        justify='center')
    time.sleep(5)
    zoom_another_copy()
    sys.exit(0)


def zoom_another_copy():
    """ Выполняется, если попытаться запустить дубль. Разворачивает
    первоначальную копию"""
    from cm_qdk.main import CMQDK
    cm_qdk = CMQDK('localhost', 50505)
    cm_qdk.make_connection()
    cm_qdk.zoom_app()
    cm_qdk.get_data()


from cm.styles.styles import *


def startLoading():
    '''Инициализация проекта, выполняется параллельно с окном загрузки'''
    threading.Thread(target=functions.install_fonts, daemon=True).start()
    arg_parser = functions.create_parser()
    namespace = arg_parser.parse_args()
    internal_cam_frame = namespace.internal_cam_frame
    external_cam_frame = namespace.external_cam_frame
    scale_server_ip = namespace.scale_server_ip
    test_mode = namespace.test
    if not scale_server_ip:
        scale_server_ip = namespace.ar_ip
    monitor_num = namespace.monitor_num
    if internal_cam_frame:
        internal_cam_frame = tuple(internal_cam_frame)
    if external_cam_frame:
        external_cam_frame = tuple(external_cam_frame)
    cams_info = {'cad_gross': {
        'enable': namespace.gross_cam,
        'ip': namespace.gross_cam_ip,
        'port': namespace.gross_cam_port},
        'auto_exit': {
            'enable': namespace.auto_exit_cam,
            'ip': namespace.auto_exit_cam_ip,
            'port': namespace.auto_exit_cam_port},
        'main': {
            'enable': namespace.main_cam,
            'ip': namespace.main_cam_ip,
            'port': namespace.main_cam_port},
        "kpp_cam_external": {
            'enable': namespace.kpp_cam_external,
            'ip': namespace.kpp_cam_external_ip,
            'port': namespace.kpp_cam_external_port},
        "kpp_cam_internal": {
            'enable': namespace.kpp_cam_internal,
            'ip': namespace.kpp_cam_internal_ip,
            'port': namespace.kpp_cam_internal_port},
    }
    wlistener = WListener('Въезд', 'COM1', 9600, ar_ip=namespace.ar_ip)
    can = Canvas(root, highlightthickness=0, bg=cs.main_background_color)
    scale_server_port = get_scale_server_port(namespace)
    ar_qdk = ARQDK(namespace.ar_ip, int(namespace.ar_port))
    while True:
        try:
            ar_qdk.make_connection()
            ar_qdk.subscribe()
            ar_qdk.get_data()
            loadingcan.delete('no_connection_info')
            break
        except:
            no_ar_connection(loadingcan)
            time.sleep(1)
    launch_info = (
        ar_qdk.execute_method('get_cm_info', get_response=True)['info'])
    kpp_mirrored = None
    print("Got launch info", launch_info)
    if "kpp" in launch_info.keys() and launch_info["kpp"]:
        kpp_mirrored = not launch_info["kpp"][0]["external_side_left"]
    settings = Settings(
        root, dirpath, mirrored=launch_info['mirrored'],
        kpp_mirrored=kpp_mirrored,
        external_cam_frame=external_cam_frame,
        internal_cam_frame=internal_cam_frame,
    )
    is_it_double = check_double()
    if not launch_info['cm_doubles'] and is_it_double:
        destroy_this_copy()
        return
    if monitor_num == "first":
        root.geometry(f"{monitors[0].width}x{monitors[0].height}+400+400")
        root.grab_set()
        root.focus_set()
        root.attributes('-fullscreen', True)
    else:
        place_second_monitor(monitors[1], monitors[0])
    for canvas in [loadingcan, can]:
        functions.draw_version_on_screen(canvas=canvas,
                                         xpos=settings.screenwidth - 30,
                                         ypos=settings.screenheight - 30,
                                         version_text=settings.version + ' v.',
                                         font=fonts.version_font)

    Operator(
        root, settings, wlistener, can, deffaultScreenSize,
        loadingcan, ar_qdk=ar_qdk,
        scale_server_ip=scale_server_ip,
        scale_server_port=scale_server_port, fgsm=launch_info['FGSM'],
        cm_cams_info=cams_info,
        test_mode=test_mode,
        gravity=launch_info["gravity"],
        kpp_mode_enable=launch_info["kpp"],
        kpp_controller_work=launch_info["kpp_controller_work"],
        rfid=launch_info["RFID"]
    )
    loadingcan.destroy()
    can.pack(fill=BOTH, expand=YES)


def place_second_monitor(monitor, first_monitor):
    root.wm_state("normal")
    x = monitor.x
    y = monitor.y
    if int(x) < 0:
        x = f"-{first_monitor.width}"
    if int(x) > 0:
        x = f"+{first_monitor.width}"
    if int(x) == 0:
        x = f"+0"
    if int(y) < 0:
        y = f"-{first_monitor.height}"
    if int(y) > 0:
        y = f"+{first_monitor.height}"
    if int(y) == 0:
        y = f"+0"
    m_s = f"{monitor.width}x{monitor.height}{x}{y}"
    root.geometry(m_s)


def get_scale_server_port(namespace):
    if not namespace.scale_server_port:
        return 2297
    else:
        return namespace.scale_server_port


def startLoadingThread():
    """ Запуск инициализации загрузки параллельным потоком """
    threading.Thread(target=startLoading, args=(), daemon=True).start()


def launch_mainloop():
    """ Запустить оснвной цикл работы """
    root.after(100, startLoadingThread)
    try:
        root.mainloop()
    except:
        # При выходе из программы - трассировать текст исключения и выполнить
        # необходимые завершающие работы
        print(format_exc())
        sys.exit(0)


def no_ar_connection(loadingcan):
    """ Если нет подключения к AR """
    loadingcan.delete('no_connection_info')
    loadingcan.create_text(root.winfo_screenwidth() / 2,
                           root.winfo_screenheight() / 2,
                           text='Не удалось подключиться к ядру...'
                                '\nПерезапуск...',
                           font=fonts.loading_status_font,
                           fill='white',
                           anchor='s',
                           justify='center',
                           tags=('no_connection_info',))
    if platform.system() == "Windows":
        root.wm_state("zoomed")
    elif platform.system() == "Linux":
        root.attributes('-zoomed', True)


#import cProfile
#cProfile.run('launch_mainloop()', "cm_start.prof")

launch_mainloop()

# -kpp_cam_internal_ip
# localnet
# -kpp_cam_internal_port
# 10101
# -kpp_cam_external_ip
# localnet
# -kpp_cam_external_port
# 10102


# -gross_cam True -auto_exit_cam True -main_cam True
