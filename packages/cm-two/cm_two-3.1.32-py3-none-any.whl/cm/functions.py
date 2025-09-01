import argparse
import datetime
import sys
from cm.configs import settings
import os
from fontTools.ttLib import TTFont
import platform
from PIL import Image, ImageDraw


def create_parser():
    """ Создать и вернуть парсер для аргументов, передаваемых при запуске
    приложения"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-ar_ip', nargs='?')
    parser.add_argument('-mirrored', nargs='?')
    parser.add_argument('-ar_port', nargs='?', default=52250)
    parser.add_argument('-scale_server_ip', nargs='?', default=None)
    parser.add_argument('-check_doubles', nargs='?', default=0)
    parser.add_argument('-scale_server_port', nargs='?', default=2297)
    parser.add_argument('-test', nargs='?', default=False)
    parser.add_argument('-fgsm', nargs='?', default=False)
    parser.add_argument('-gross_cam', nargs='?', default=False)
    parser.add_argument('-gross_cam_ip', nargs='?', default=False)
    parser.add_argument('-gross_cam_port', nargs='?', default=False)
    parser.add_argument('-auto_exit_cam', nargs='?', default=False)
    parser.add_argument('-auto_exit_cam_ip', nargs='?', default=False)
    parser.add_argument('-auto_exit_cam_port', nargs='?', default=False)
    parser.add_argument('-main_cam', nargs='?', default=False)
    parser.add_argument('-main_cam_ip', nargs='?', default=False)
    parser.add_argument('-main_cam_port', nargs='?', default=False)

    parser.add_argument('-kpp_cam_internal', nargs='?', default=False)
    parser.add_argument('-kpp_cam_internal_ip', nargs='?', default=False)
    parser.add_argument('-kpp_cam_internal_port', nargs='?', default=False)
    parser.add_argument('-kpp_cam_external', nargs='?', default=False)
    parser.add_argument('-kpp_cam_external_ip', nargs='?', default=False)
    parser.add_argument('-kpp_cam_external_port', nargs='?', default=False)

    parser.add_argument('-external_cam_frame', nargs='+', type=int,
                        default=False)
    parser.add_argument('-internal_cam_frame', nargs='+', type=int,
                        default=False)
    parser.add_argument('-monitor_num', nargs='+', type=str,
                        default="first")
    return parser


def draw_version_on_screen(canvas, xpos, ypos, version_text, font):
    """ Рисует на холсте версию приложения """
    canvas.create_text(xpos, ypos, text=version_text, font=font,
                       fill='grey')


def log_events():
    td = datetime.datetime.today().date()
    path = os.path.join(settings.LOGS_DIR, f'{td}.log')
    log_file = open(path, "w")
    sys.stdout = log_file


def del_logs():
    files = os.listdir(settings.LOGS_DIR)
    for filename in files:
        if filename == '__init__.py' or filename == '__pycache__':
            continue
        date = filename.split('.')[0]
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
        today = datetime.datetime.today().date()
        if date.date() < today - datetime.timedelta(
                days=3):
            os.remove(os.path.join(settings.LOGS_DIR, filename))


def install_fonts():
    files = os.listdir(settings.FONTS_DIR)
    for filename in files:
        if filename == '__init__.py' or filename == '__pycache__':
            continue
        font = TTFont(os.path.join(settings.FONTS_DIR, filename))
        font.save(os.path.join(settings.FONTS_DIR, filename))
        if platform.uname().system == 'Windows':
            import win32api
            import win32con
            import ctypes
            ctypes.windll.gdi32.AddFontResourceA(
                os.path.join(settings.FONTS_DIR, filename))
            win32api.SendMessage(win32con.HWND_BROADCAST,
                                 win32con.WM_FONTCHANGE)


def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)),
                (w - rad, h - rad))
    im.putalpha(alpha)
    return im
