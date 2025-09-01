from __future__ import print_function
import time
from PIL import Image, ImageTk
import threading
import importlib.resources as pkg_resources
import os, cv2
import traceback


os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
    "rtsp_transport;tcp"
    "|timeout;5000000"     # connect-timeout (µs)  FFmpeg ≥ 5.0
    "|rw_timeout;5000000"  # read-/write-timeout  FFmpeg ≥ 4.4
    "|stimeout;5000000"    # старое имя до FFmpeg 5.0 — на всякий случай
)

def _open_capture(url):
    import cv2

    # формируем список параметров только если такие свойства есть
    props = []
    if hasattr(cv2, "CAP_PROP_OPEN_TIMEOUT_MSEC"):
        props += [
            cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 3000,   # 3 с connect
            cv2.CAP_PROP_READ_TIMEOUT_MSEC,  3000,   # 3 с packet
            cv2.CAP_PROP_BUFFERSIZE,         1
        ]

    # ── попытка «нового» вызова ───────────────────────────────
    if props:
        cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG, props)
        if cap.isOpened():          # удалось — пользуемся
            return cap
        cap.release()               # не удалось — чистим

    # ── fallback для старых OpenCV ────────────────────────────
    return cv2.VideoCapture(url, cv2.CAP_FFMPEG)


class PhotoBoothApp:
    def __init__(self, url, outputPath, root, canvas,
                 width=300, height=300,
                 pos_x=500, pos_y=500, zoomed_x=1000, zoomed_y=1000,
                 zoomed_video_width=1000, zoomed_video_height=700,
                 root_zoom_callback_func=None,
                 root_hide_callback_func=None,
                 cam_type=None):
        self.url = url
        self.can_show = False
        self.zoomed = False
        self.cam_type = cam_type
        self.zoomed_video_width = zoomed_video_width
        self.zoomed_video_height = zoomed_video_height
        self.outputPath = outputPath
        self.root_zoom_callback_func = root_zoom_callback_func
        self.root_hide_callback_funct = root_hide_callback_func
        self.frame = None
        self.latest_frame = None
        self.can_zoom = True
        self.thread = None
        self.stopEvent = threading.Event()
        self.zoomed_x = zoomed_x
        self.zoomed_y = zoomed_y

        self.root = root
        self.init_x, self.init_y = pos_x, pos_y
        self.place_x, self.place_y = pos_x, pos_y
        self.init_video_width, self.init_video_height = width, height
        self.video_width, self.video_height = width, height

        self.canvas = canvas
        self.image_id_1 = None
        self.image_id_2 = None
        self.tk_image_1 = None
        self.tk_image_2 = None
        self.last_used_id = 1

        with pkg_resources.path("cm.imgs", "camera_is_connecting.png") as img_path:
            self.img_loading = ImageTk.PhotoImage(Image.open(img_path))
        with pkg_resources.path("cm.imgs", "camera_is_not_available.png") as img_path:
            self.img_unavailable = ImageTk.PhotoImage(Image.open(img_path))

        self.camera_unavailable = False

        threading.Thread(target=self.read_frames_loop, daemon=True).start()
        threading.Thread(target=self.video_loop, daemon=True).start()

    def read_frames_loop(self):
        cap = _open_capture(self.url)

        # параметры «здоровья» камеры
        unavailable_threshold = 10  # секунд без кадров → камера down
        reconnect_interval = 5  # секунд между попытками connect
        fail_limit = 20  # N подряд неудачных .read()

        # служебные счётчики/таймеры
        last_ok_frame = time.time()  # последний успешный кадр
        last_reconnect = 0  # последняя попытка reconnect
        fail_counter = 0  # подряд ret==False

        while not self.stopEvent.is_set():
            try:
                # ─── читаем кадр ───────────────────────────────────────────
                ret, frame = cap.read()

                if not ret:  # кадра нет
                    fail_counter += 1
                    now = time.time()

                    # камера не даёт кадры уже unavailable_threshold сек
                    self.camera_unavailable = (now - last_ok_frame
                                               > unavailable_threshold)

                    # пора пересоздать VideoCapture?
                    if (fail_counter >= fail_limit or
                            now - last_reconnect >= reconnect_interval):
                        cap.release()
                        cap = _open_capture(self.url)
                        last_reconnect = now
                        fail_counter = 0  # обнуляем серию ошибок

                    time.sleep(0.1)
                    continue  # к следующей итерации цикла

                # ─── кадр пришёл ───────────────────────────────────────────
                self.latest_frame = frame
                self.camera_unavailable = False
                last_ok_frame = time.time()
                fail_counter = 0

            except Exception as e:
                # Печать трейсбека помогает ловить экзотические падения
                print(f"[{self.cam_type}] read_frames_loop error:", e)
                traceback.print_exc()
                time.sleep(1)  # дышим и пробуем дальше

    def video_loop(self):
        while not self.stopEvent.is_set():
            try:
                if not self.can_show:
                    time.sleep(0.05)
                    continue

                frame = self.latest_frame
                if frame is None:
                    image = self.img_unavailable if self.camera_unavailable else self.img_loading
                    self._show_image(image, static=True)
                    time.sleep(0.05)
                    continue

                resized = cv2.resize(frame, (self.video_width, self.video_height))
                image = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                pil_image = Image.fromarray(image)
                tk_image = ImageTk.PhotoImage(pil_image)

                self._show_image(tk_image)

            except Exception as e:
                print(f"[{self.cam_type}] [video_loop error]", e)
            time.sleep(0.03)

    def _show_image(self, image, static=False):
        if self.last_used_id == 1:
            if self.image_id_2 is None:
                self.image_id_2 = self.canvas.create_image(self.place_x, self.place_y, image=image, tag="cam_img")
                self.canvas.tag_bind(self.image_id_2, '<Button-1>', self.img_callback)
            else:
                self.canvas.itemconfig(self.image_id_2, image=image)
                self.canvas.coords(self.image_id_2, self.place_x, self.place_y)
            self.canvas.tag_raise(self.image_id_2)
            self.last_used_id = 2
            if not static:
                self.tk_image_2 = image
        else:
            if self.image_id_1 is None:
                self.image_id_1 = self.canvas.create_image(self.place_x, self.place_y, image=image, tag="cam_img")
                self.canvas.tag_bind(self.image_id_1, '<Button-1>', self.img_callback)
            else:
                self.canvas.itemconfig(self.image_id_1, image=image)
                self.canvas.coords(self.image_id_1, self.place_x, self.place_y)
            self.canvas.tag_raise(self.image_id_1)
            self.last_used_id = 1
            if not static:
                self.tk_image_1 = image
        if not self.can_show:
            self.clear_images()

    def hide_callback(self, root_calback=True):
        self.video_width = self.init_video_width
        self.video_height = self.init_video_height
        self.place_x = self.init_x
        self.place_y = self.init_y
        self.can_show = True
        if self.root_hide_callback_funct and root_calback:
            self.root_hide_callback_funct(self.cam_type)
            self.zoomed = False

    def set_new_params(self, x=None, y=None, width=None, height=None):
        if width:
            self.video_width = width
        if height:
            self.video_height = height
        if x:
            self.place_x = x
        if y:
            self.place_y = y

    def zoom_callback(self, root_calback=True):
        self.video_width = self.zoomed_video_width
        self.video_height = self.zoomed_video_height
        self.place_x = self.zoomed_x
        self.place_y = self.zoomed_y
        self.can_show = True
        if self.root_zoom_callback_func and root_calback:
            self.root_zoom_callback_func(self.cam_type)
        self.zoomed = True

    def img_callback(self, *args):
        if not self.can_zoom:
            return
        self.can_show = False
        if self.zoomed:
            self.hide_callback()
        else:
            self.zoom_callback()

    def onClose(self):
        print("[INFO] closing...")
        self.stopEvent.set()
        try:
            self.root.quit()
        except:
            pass

    def stop_video(self):
        self.can_show = False
        if self.image_id_1 is not None:
            self.canvas.delete(self.image_id_1)
            self.image_id_1 = None
        if self.image_id_2 is not None:
            self.canvas.delete(self.image_id_2)
            self.image_id_2 = None

    def play_video(self):
        # Удалим старые изображения, чтобы избежать "призраков"
        if self.image_id_1:
            self.canvas.delete(self.image_id_1)
            self.image_id_1 = None
        if self.image_id_2:
            self.canvas.delete(self.image_id_2)
            self.image_id_2 = None
        self.can_show = True

    def clear_images(self):
        self.can_show = False
        if self.image_id_1:
            self.canvas.delete(self.image_id_1)
            self.image_id_1 = None
        if self.image_id_2:
            self.canvas.delete(self.image_id_2)
            self.image_id_2 = None


def start_video_stream(root, canvas, xpos, ypos, v_width, v_height,
                       cam_login, cam_pass, cam_ip, zoomed_x, zoomed_y,
                       zoomed_video_width, zoomed_video_height,
                       cam_type=None,
                       cam_port=554,
                       zoom_callback_func=None, hide_callback_func=None):
    url = f"rtsp://{cam_login}:{cam_pass}@{cam_ip}:{cam_port}/Streaming/Channels/102"

    inst = PhotoBoothApp(url, "output", root=root, canvas=canvas, width=v_width,
                         height=v_height, pos_x=xpos, pos_y=ypos,
                         zoomed_x=zoomed_x,
                         zoomed_y=zoomed_y,
                         root_zoom_callback_func=zoom_callback_func,
                         root_hide_callback_func=hide_callback_func,
                         cam_type=cam_type,
                         zoomed_video_width=zoomed_video_width,
                         zoomed_video_height=zoomed_video_height)
    return inst
