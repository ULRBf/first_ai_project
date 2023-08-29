"""
- mainClass: 메인 윈도우 클래스
- joinClass: 회원가입 다이얼로그

최초 작성: 2023-08-27 18:45
최종 수정: 2023-08-28 23:51
"""

import sys
import os
from PyQt5.QtMultimedia import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimediaWidgets import *
from Qt_ui._ui.ui_main_form import Ui_mainForm
from Qt_ui._ui.ui_join_form import Ui_joinForm
from ultralytics import YOLO
from glob import glob
from time import sleep
from PIL.ImageFont import *
from PIL.Image import *
from PIL.ImageDraw import *
import cv2
import easyocr
import threading
import matplotlib.pyplot as plt
import warnings
import random
import numpy as np
import psycopg2
from Qt_ui.interaction_db import InteractionToDB
import datetime
import time
from threading import Thread
from PIL import ImageFont, ImageDraw, Image

warnings.filterwarnings('ignore')  # 불필요한 경고문 제거

class SignUpClass(QDialog, Ui_joinForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initSignal()

    def initSignal(self):
        self.btn_open_login.clicked.connect(self.check_info)

    def show_message_box(self, msg):
        if msg == "need_more_data":
            QMessageBox.about(self, '에러 확인 요청', '정보를 다 입력해주세요.')
        elif msg == "not_match_pw":
            QMessageBox.about(self, '에러 확인 요청', '비밀번호를 다시 확인해주세요.')
        elif msg == "can_sign_up":
            QMessageBox.about(self, '가입 승인', '회원가입이 완료되었습니다.')

    def check_info(self):
        # 누락된 내용이 있는지 정도만 확인하자.
        data_list = [self.le_id_input.text(),
                     self.le_pw_input.text(),
                     self.le_cpw_input.text(),
                     self.le_name_input.text(),
                     self.le_contact_input.text()]
        for data in data_list:
            if data == '':
                self.show_message_box("need_more_data")
                return

        if self.le_pw_input.text() != self.le_cpw_input.text():
            self.show_message_box("not_match_pw")
        else:
            main = MainClass()
            main.get_other_class_data(data_list)
            self.show_message_box("can_sign_up")
            self.close()

class MainClass(QMainWindow, Ui_mainForm):
    """
    메인 윈도우 클래스
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # UI 초기화
        self.initUi()  # UI 요소 초기화
        self.initSignal()  # 버튼 및 시그널 연결 초기화
        self.initFunc()  # 기능 연결 초기화

    def initUi(self):
        """
        GUI 스타일시트의 초기화를 담당합니다.
        """
        self.stackedWidget.setCurrentIndex(0)  # 메인 페이지 0번 인덱스 고정
        self.setWindowFlags(Qt.FramelessWindowHint)  # 테두리 제거
        self.icon_title_img.setIcon((QIcon('../Qt_ui/_icons/cam_icon_white.png')))
        self.icon_open_id.setIcon((QIcon('../Qt_ui/_icons/person_icon.png')))
        self.icon_open_pw.setIcon((QIcon('../Qt_ui/_icons/lock_icon.png')))
        self.lb_main_title_background.setPixmap(QPixmap('../Qt_ui/_icons/main_title.png'))
        self.lb_main_img.setPixmap(QPixmap('../Qt_ui/_icons/play_button_img.png'))
        self.lb_plate_img.setPixmap((QPixmap('../Qt_ui/_icons/plate_img.png')))
        self.icon_top_img.setIcon((QIcon('../Qt_ui/_icons/cam_icon_white.png')))

    def initSignal(self):
        """
        버튼 및 시그널 연결의 초기화를 담당합니다.
        + 추가 내용 : DB 상호작용 오브젝트 생성
        """
        self.btn_open_login.clicked.connect(lambda: print(">> stackedWidget: index 1"))
        self.btn_open_login.clicked.connect(self.log_in_check)
        self.btn_open_signup.clicked.connect(lambda: print(">> 회원가입 버튼 클릭"))
        self.btn_open_signup.clicked.connect(self.signup_dialog_act)
        self.btn_main1_close.clicked.connect(lambda: print(">> main window close") or sys.exit())
        self.btn_main2_close.clicked.connect(lambda: print(">> main window close") or sys.exit())
        self.btn_video_connect.clicked.connect(self.start_video_processing)
        self.btn_video_disconnect.clicked.connect(self.stop_video_event)
        self.interaction_to_db_obj = InteractionToDB()

    def initFunc(self):
        """
        메소드의 초기화를 담당합니다.
        """
        pass

    def signup_dialog_act(self):
        sign_up_dialog_obj = SignUpClass()
        sign_up_dialog_obj.exec_()

    def get_other_class_data(self, other_class_data):
        self.get_data_list = other_class_data
        self.send_sign_up_data_to_db()

    def send_sign_up_data_to_db(self):
        self.interaction_to_db_obj.insert_membership_registration(self.get_data_list[0],
                                                                  self.get_data_list[1],
                                                                  self.get_data_list[3],
                                                                  self.get_data_list[4])

    # 로그인 시의 동작
    def log_in_check(self):
        user_input_car_number = self.le_id_text.text()  # id 대용으로 car_number를 사용하기로 함.
        user_input_pw = self.le_pw_text.text()
        ret = self.interaction_to_db_obj.log_in(user_input_car_number, user_input_pw)

        if ret == "not_registered_this_car_number":
            # 메시지 박스에 "가입되지않은 정보입니다." 출력
            QMessageBox.about(self, '에러 확인 요청', '가입되지 않은 정보입니다.')
        elif ret == "check_pw":
            QMessageBox.about(self, '에러 확인 요청', '비밀번호가 맞지 않습니다.')
        else:
            self.stackedWidget.setCurrentIndex(1)

    def start_video_processing(self):
        """
        비디오 처리 시작 메소드
        """
        video_path = r'K-20230829-092255.mp4'
        model_path = r'day_night_best.pt'
        # 비디오 파일과 모델 경로를 설정하고 YOLOVideoClass 인스턴스 생성
        video_capture_thread = Thread(target=self.video_capture_using_thread, args=(video_path, model_path))
        video_capture_thread.start()
        ocr_module_thread = Thread(target=self.start_ocr_module)
        ocr_module_thread.start()

    def video_capture_using_thread(self, video_path, model_path):
        print(">> 재생 버튼 클릭")
        self.video_processor = YOLOVideoClass(model_path, video_path)
        self.video_processor.process_video(self.update_display)

    def update_display(self, frame):
        """
        프레임을 Qt 이미지로 변환하고 화면에 업데이트 하는 메소드
        """
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        qt_pixmap = QPixmap.fromImage(qt_image)
        self.lb_main_img.setPixmap(qt_pixmap)

    def stop_video_event(self):
        """
        비디오 처리 중단 메소드
        """
        self.video_processor.stop()
        self.lb_main_img.setPixmap(QPixmap('./_icons/play_button_img.png'))

    def start_ocr_module(self):
        while True:
            file_path = r"/SJH/temp_img_dir"
            finder = OldestFileFinder(file_path)
            oldest_file_path = finder.find_oldest_file()
            ocr_module = TextDetectionVisualizer()
            if oldest_file_path is not None:
                ocr_result = ocr_module.visualize_text_detection(oldest_file_path)  # 입력 이미지에서 텍스트 탐지 시각화 수행
                self.car_number_filter(ocr_result)

            # try:
            #     os.remove(file_path)
            # except OSError as e:
            #     print(f'파일 삭제 오류: {e}')

            # 뽑혀나온 데이터 전처리 해서 저장하고,
            # oldest_file_path 삭제 해야함.

    def car_number_filter(self, ocr_data):
        # ocr_data -> list 형태로 반환된다.
        for (bbox, text, prob) in ocr_data:
            print(f">> Bounding Box: {bbox} / Text: {text} / Probability: {prob * 100}")




class YOLOVideoClass:
    """
    YOLO 객체 감지 모델을 사용하여 비디오 처리하는 클래스
    """
    def __init__(self, model_path, video_path):
        self.model = YOLO(model_path)
        self.cap = cv2.VideoCapture(video_path)
        self.keep_processing = True
        self.time_toggle = 0

    def init_display_window(self):
        """
        디스플레이 창 초기화
        """
        cv2.namedWindow("Model View", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Model View", 700, 400)


    def process_video(self, callback):
        """
        비디오 처리 함수
          ->  '재생'버튼을 누를 때 1번 수행된다.
        """
        toggle_time = 1693280501.0823164  # 초기 설정 시간 -> 무조건 초기 1회는 캡쳐되도록 하려고.
        ch_toggle = True
        while self.cap.isOpened() and self.keep_processing:
            now_time = time.time()
            # 비디오 캡쳐 객체가 열려 있고 처리를 계속 해야 하는 동안 반복
            success, frame = self.cap.read()  # 다음 프레임 읽기
            if success:
                if ch_toggle is True:
                    # 프레임 읽기에 성공했을 때
                    results = self.model(frame)  # YOLO 모델을 사용하여 프레임 내 객체 감지
                    # print(results[0].boxes)  # 감지된 객체의 경계 상자 좌표 출력
                    xywh_list = results[0].boxes.xywh
                    if len(xywh_list) != 0:
                        xywh_list = results[0].boxes.xywh[0]
                        if (now_time - toggle_time >= 2) and (xywh_list[2] >= 80):
                            print("지금 캡쳐")
                            print(xywh_list.item)
                            # x, y, w, h = 100, 200, 300, 100  # 예시로 (100, 200)부터 (400, 300) 까지 영역 잘라냄
                            # cropped_image = image[y:y + h, x:x + w]
                            cv2.imwrite(f'./temp_img_dir/{now_time}.png', frame)
                            toggle_time = now_time
                        else:
                            pass
                if ch_toggle is True:
                    ch_toggle = False
                else:
                    ch_toggle = True

                annotated_frame = results[0].plot()  # 객체 감지 결과를 프레임에 표시한 이미지 생성
                annotated_frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)  # 이미지 색상 공간 변환
                callback(annotated_frame_rgb)  # 콜백 함수 호출하여 프레임 업데이트 및 표시

                key = cv2.waitKey(1)  # 키 입력 대기 (1ms)
                if key == ord("q"):
                    break  # 'q' 키를 누르면 처리 중단
            else:
                break

    def release_resources(self):
        """
        캡쳐 및 창 리소스 해제 메소드
        """
        self.cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        """
        비디오 처리 중단 메소드
        """
        self.keep_processing = False
        self.release_resources()


class OldestFileFinder:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def find_oldest_file(self):
        file_list = os.listdir(self.folder_path)
        sorted_files = sorted(file_list, key=lambda x: os.path.getmtime(os.path.join(self.folder_path, x)))
        if len(sorted_files) != 0:
            oldest_file_path = os.path.join(self.folder_path, sorted_files[0])
        else:
            oldest_file_path = None
        return oldest_file_path


class TextDetectionVisualizer:
    def __init__(self, languages=['ko'], gpu=True, target_height=600, target_width=600):
        # 지정된 언어와 GPU 사용 옵션으로 EasyOCR Reader를 초기화
        self.reader = easyocr.Reader(languages, gpu=gpu)
        self.target_height = target_height  # 출력 이미지의 원하는 높이
        self.target_width = target_width  # 출력 이미지의 원하는 너비

    def enhance_image(self, image):
        """
        입력 이미지를 가우시안 블러를 사용하여 개선하는 메서드를 정의
        """
        blurred = cv2.GaussianBlur(image, (0, 0), 3)  # 가우시안 블러 적용
        enhanced = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)  # 이미지 개선
        return enhanced

    def equalize_histogram(self, image):
        """
        Apply histogram equalization to enhance image contrast
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        equalized = cv2.equalizeHist(gray)
        return cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)

    def add_sharpen(self, image):
        """
        선명도 필터를 사용하여 입력 이미지의 선명도를 높이는 방법을 정의
        """
        sharpen_value_1 = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
        sharpen_value_2 = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]
        sharpen_value_3 = [[-1, -1, -1], [-1, 10, -1], [-1, -1, -1]]
        kernel = np.array(sharpen_value_2)
        sharpened = cv2.filter2D(image, -1, kernel)
        return sharpened

    def add_padding(self, image):
        """
        입력 이미지에 패딩을 추가하여 목표 차원과 일치하도록 하는 메서드를 정의
        """
        # 각 면에 대한 패딩 양을 계산
        if image.shape[0] < self.target_height or image.shape[1] < self.target_width:
            top_padding = max((self.target_height - image.shape[0]) // 2, 0)
            bottom_padding = max(self.target_height - image.shape[0] - top_padding, 0)
            left_padding = max((self.target_width - image.shape[1]) // 2, 0)
            right_padding = max(self.target_width - image.shape[1] - left_padding, 0)

            # 패딩을 추가하여 이미지를 생성
            padded_image = cv2.copyMakeBorder(image, top_padding, bottom_padding, left_padding, right_padding, cv2.BORDER_CONSTANT)
            return padded_image
        else:
            return image

    def add_threshold(self, image):
        """
        Apply adaptive thresholding to enhance text regions.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresholded = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        return thresholded

    def visualize_text_detection(self, image_path):
        """
        입력 이미지에서 텍스트 탐지를 시각화하는 메서드를 정의합니다.
        """
        # OpenCV를 사용하여 입력 이미지를 읽음
        img = cv2.imread(image_path)
        enhanced_img = self.enhance_image(img)  # 이미지 개선
        equalized_img = self.equalize_histogram(enhanced_img)  # 히스토그램 이퀄 개선
        sharpened_img = self.add_sharpen(equalized_img)  # 이미지 선명도 개선
        padded_img = self.add_padding(sharpened_img)  # 목표 차원에 맞게 패딩 추가
        thresholded_img = self.add_threshold(padded_img)  # 임계값 추가

        result = self.reader.readtext(thresholded_img)

        # 각 인식된 텍스트 영역에 대해 세부 정보를 출력
        # for (bbox, text, prob) in result:
        #     print(f">> Bounding Box: {bbox} / Text: {text} / Probability: {prob * 100}")

        img_pil = Image.fromarray(padded_img)  # 이미지를 PIL 형식으로 변환
        font = ImageFont.truetype('Pretendard-Medium.ttf', 60)  # 텍스트 렌더링을 위한 폰트 로드
        draw = ImageDraw.Draw(img_pil)  # 이미지에 그리기 객체 생성

        np.random.seed(42)
        COLORS = np.random.randint(0, 255, size=(255, 3), dtype="uint8")  # 랜덤한 색상 생성

        # 각 인식된 텍스트 영역에 대해 경계 상자와 텍스트를 이미지에 그림
        for i in result:
            x = i[0][0][0]  # 경계 상자의 좌상단 x 좌표
            y = i[0][0][1]  # 경계 상자의 좌상단 y 좌표
            w = i[0][1][0] - i[0][0][0]  # 경계 상자의 너비
            h = i[0][2][1] - i[0][1][1]  # 경계 상자의 높이

            color_idx = random.randint(0, 255)  # 랜덤한 색상 인덱스 선택
            color = tuple([int(c) for c in COLORS[color_idx]])  # 색상 값을 튜플로 변환

            # 인식된 텍스트 영역 주위에 사각형 그리기
            draw.rectangle(((x, y), (x + w, y + h)), outline=color, width=2)
            # 사각형 위에 인식된 텍스트 그리기
            draw.text((int((x + x + w) / 2), y - 2), str(i[1]), font=font, fill=color)

        return result
        # 최종 이미지를 matplotlib을 사용하여 표시
        # plt.figure(figsize=(10, 10))
        # plt.imshow(img_pil)
        # plt.axis('off')
        # plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fontDB = QFontDatabase()
    fontDB.addApplicationFont('./_font/Pretendard-Medium.ttf') # 폰트 지정
    app.setFont(QFont('Pretendard Medium'))
    run = MainClass()
    run.show()

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing Window...")
        