"""
최초 작성: 2023-08-27 18:45
최종 수정: 2023-08-31 11:00
"""

import pickle
import sys
import os
import socket
import json
from builtins import open as b_open
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
from PIL.Image import Image
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

HEADER_BUFFER = 32
BUFFER = 1024
warnings.filterwarnings('ignore')  # 불필요한 경고문 제거

class SignUpClass(QDialog, Ui_joinForm):
    def __init__(self):
        super().__init__()
        self.draggable = False
        self.offset = None
        self.setupUi(self)
        self.initUi()
        self.initSignal()

    def initUi(self):
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)  # 다이얼로그창 테두리 제거

    def initSignal(self):
        self.btn_open_login.clicked.connect(self.check_info)
        self.btn_dialog_close.clicked.connect(lambda: print(">> join dialog close") or self.close())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_position = event.globalPos() - self.offset
            self.move(new_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False
            self.offset = None

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
        self.draggable = False
        self.offset = None
        self.setupUi(self)  # UI 초기화
        self.initUi()  # UI 요소 초기화
        self.initSignal()  # 버튼 및 시그널 연결 초기화
        self.initSocket()  # 클라이언트 소켓

    def initUi(self):
        """
        GUI 스타일시트의 초기화를 담당합니다.
        """
        self.stackedWidget.setCurrentIndex(0)  # 시작시 메인 페이지 0번 인덱스 고정
        self.setWindowFlags(Qt.FramelessWindowHint)  # 윈도우창 테두리 제거
        self.tableWidget.clearContents()  # 시작시 테이블위젯 값 초기화
        self.icon_title_img.setIcon((QIcon('./_icons/cam_icon_white.png')))
        self.icon_open_id.setIcon((QIcon('./_icons/person_icon.png')))
        self.icon_open_pw.setIcon((QIcon('./_icons/lock_icon.png')))
        self.lb_main_title_background.setPixmap(QPixmap('./_icons/main_title.png'))
        self.lb_main_img.setPixmap(QPixmap('./_icons/play_button_img.png'))
        self.lb_plate_img.setPixmap((QPixmap('./_icons/plate_img.png')))
        self.icon_top_img.setIcon((QIcon('./_icons/cam_icon_white.png')))
        self.lb_type_img.setPixmap((QPixmap('./_icons/vehicle_type.png')))

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
        self.btn_main1_minimized.clicked.connect(self.showMinimized)  # 창 최소화
        self.btn_main2_minimized.clicked.connect(self.showMinimized)  # 창 최소화
        self.btn_video_connect.clicked.connect(self.start_video_processing)
        self.btn_video_disconnect.clicked.connect(self.stop_video_event)
        self.interaction_to_db_obj = InteractionToDB()

    def initSocket(self):
        current_time = datetime.datetime.now()
        formatted_datetime = current_time.strftime("%Y-%m-%d %H:%M:%S")
        self.server_address = ('127.0.0.1', 7777)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)
        print(f">> 접속한 서버: {self.server_address[0]}:{self.server_address[1]} ({formatted_datetime})")
        # self.recv_run()
        client_thread = threading.Thread(target=self.receive_thread)
        client_thread.start()

    def send_message(self):
        message = self.text_edit.toPlainText()
        if message:
            self.client_socket.send(message.encode())
            self.text_edit.clear()

    def socket_close(self, event):
        self.client_socket.close()

    def receive_thread(self):
        while True:
            data = self.client_socket.recv(BUFFER)
            if not data:
                break

            json_data = data.decode()
            print(">> 디코딩 되기 전 JSON DATA:", json_data)

            try:
                json_obj = json.loads(json_data)
            except json.JSONDecodeError:
                continue

            print(f">> 서버로부터 JSON 데이터 수신: {json_obj}")

            response_data = {"Response": "JSON 데이터를 성공적으로 수신"}
            response = json.dumps(response_data)


    def json_default(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S.%f")
        # raise TypeError('not JSON serializable')

    # 다시 client의 Back으로 보내는 작업
    def send_fuc(self, send_data: dict):
        # json_data = json.dumps(send_data, default=self.json_default).encode("utf-8")
        print(">> send_data:", send_data)
        json_data = json.dumps(send_data).encode("utf-8")
        data_len = len(json_data)
        header_data = f"{data_len:032d}".encode("utf-8")
        self.client_socket.send(header_data)
        self.client_socket.send(json_data)

    # client의 Back으로부터 데이터를 받는 작업
    def receive_fuc(self):
        while True:
            # 먼저 헤더 데이터를 받는다.
            # header_buffer 사이즈인 32만큼을 채워서 보내서, 다음 recv 가 동작하도록 한다.
            received_byte_header: bytes = self.client_socket.recv(HEADER_BUFFER)
            received_header = received_byte_header.decode("utf-8")
            # print("header길이 데이터 확인용 ->", received_header)
            received_header_int = int(received_header)

            # 데이터를 담을 공간 생성
            received_byte_data: bytes = b""
            while received_header_int > 0:  # 데이터가 없지 않으면
                if received_header_int < BUFFER:
                    # 남은 데이터 양이 설정된 버퍼 크기보다 작으면
                    main_data_buffer = received_header_int
                    # 받을 데이터 버퍼 크기를 남은 데이터 양으로 설정
                else:
                    main_data_buffer = BUFFER
                received_byte_data += self.client_socket.recv(main_data_buffer)
                # 설정된 버퍼만큼 받아서 누적 저장
                received_header_int -= main_data_buffer
            received_json_data = received_byte_data.decode("utf-8")
            received_data = json.loads(received_json_data)
            print("받은 데이터", received_data)


    def recv_run(self):
        receive_theread = Thread(target=self.receive_fuc, daemon=True)  # 이걸 계속 돌리려면, receive_fuc 함수를 while문 하나 더 씌워서 돌려야 할 것 같다.
        receive_theread.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_position = event.globalPos() - self.offset
            self.move(new_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.draggable = False
            self.offset = None

    def signup_dialog_act(self):
        sign_up_dialog_obj = SignUpClass()
        sign_up_dialog_obj.exec_()

    def get_other_class_data(self, other_class_data):
        self.get_data_list = other_class_data
        self.send_sign_up_data_to_db()

    def send_sign_up_data_to_db(self):
        self.interaction_to_db_obj.insert_membership_registration(self.get_data_list[0], self.get_data_list[1],
                                                                  self.get_data_list[3], self.get_data_list[4])

    def log_in_check(self):
        """
        로그인 체크 메소드
        """
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
        # video_path = r'seoul_drive.mp4'
        video_path = self.load_file()
        model_path = r'230830_점심_best.pt'
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

    def start_ocr_module(self):  # 그 자식
        while True:
            file_path = r"./_temp_img_dir"
            file_finder = FileFinderClass(file_path)
            oldest_file_path = file_finder.find_oldest_file()
            latest_file_path = file_finder.find_latest_file()
            ocr_module = TextDetectionVisualizer()
            current_time = datetime.datetime.now()
            formatted_datetime = current_time.strftime("%Y-%m-%d %H:%M:%S")
            db_formatted_datetime = current_time.strftime("%Y%m%d %H:%M:%S")
            if oldest_file_path is not None:
                # ocr_result = ocr_module.visualize_text_detection(oldest_file_path)  # 입력 이미지에서 텍스트 탐지 시각화 수행
                # self.car_number_filter(ocr_result)
                # self.oldest_image_path = oldest_file_path
                # self.lastest_image_path = latest_file_path
                pixmap = QPixmap(latest_file_path)
                self.lb_plate_img.setPixmap(pixmap)

                # for filename in os.listdir(file_path):
                #     if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                #         image_path = os.path.join(image_path, filename)

                ocr_result = ocr_module.visualize_text_detection(latest_file_path)  # 최신 파일에 OCR 수행
                number_result = self.car_number_filter(ocr_result)

                if os.path.exists(oldest_file_path):  # 위의 OCR이 수행되면 경로상의 과거 파일이 삭제됨
                    os.remove(oldest_file_path)

                ml_result = self.ml_vehicle_classification(number_result)
                print(f">> ocr_recognition: {number_result}")
                print(f">> vehicle_classification: {ml_result}")

                total_result = {'ocr_recog': number_result,
                                'vehicle_classifi': ml_result,
                                'GPS': '광주광역시 상무지구',
                                'current_time': formatted_datetime}

                self.send_fuc(total_result)  # 서버에 센드

                row_count = self.tableWidget.rowCount()
                self.tableWidget.insertRow(row_count)

                for row, text in enumerate([number_result]):
                    item = QTableWidgetItem(str(text))
                    loc = QTableWidgetItem(str("광주광역시 상무지구"))
                    time = QTableWidgetItem(str(formatted_datetime))
                    self.tableWidget.setItem(row_count, 0, item)
                    self.tableWidget.setItem(row_count, 2, loc)
                    self.tableWidget.setItem(row_count, 3, time)
                    self.tableWidget.resizeColumnsToContents()  # 값이 들어올 때 테이블위젯 컬럼 크기도 자동으로 조절

                # self.interaction_to_db_obj.insert_detected_car_info()

            # try:
            #     os.remove(file_path)
            # except OSError as e:
            #     print(f'파일 삭제 오류: {e}')

            # 뽑혀나온 데이터 전처리 해서 저장하고,
            # oldest_file_path 삭제 해야함.

    def ml_vehicle_classification(self, car_plate_info):
        car_plate_info = "545소 1234"
        with b_open('rfc_model.pkl', 'rb') as model_file:
            chili_shrimp_burger = pickle.load(model_file)
        with b_open('le_text_model.pkl', 'rb') as model_file:
            le_text_model = pickle.load(model_file)
        with b_open('le_target_model.pkl', 'rb') as model_file:
            le_target_model = pickle.load(model_file)

        if len(car_plate_info) == 8:
            number = car_plate_info[:2]
            text = car_plate_info[2]
        elif len(car_plate_info) == 9:
            number = car_plate_info[:3]
            text = car_plate_info[3]
        encoded_text = le_text_model.transform([text])
        result = chili_shrimp_burger.predict([[number, encoded_text[0]]])
        decoded_classes = le_target_model.inverse_transform(result)

        return decoded_classes[0]

    def car_number_filter(self, ocr_data):
        # ocr_data -> list 형태로 반환된다.
        for (bbox, text, prob) in ocr_data:
            # print(f">> Bounding Box: {bbox} / Text: {text} / Probability: {prob * 100}")
            return text

    def load_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi);;All Files (*)", options=options)
        return file_path

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
            current_time = datetime.datetime.now()
            formatted_datetime = current_time.strftime("%Y-%m-%d_%H-%M-%S")
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
                            # print("지금 캡쳐")
                            # print(xywh_list.item)
                            x, y, w, h = int(xywh_list[0]), int(xywh_list[1]), int(xywh_list[2]), int(xywh_list[3])  # x, y, w, h = 100, 200, 300, 100  # 예시로 (100, 200)부터 (400, 300) 까지 영역 잘라냄
                            cropped_image = frame[y - h -10// 2:y + h, x - w -10// 2:x + w]
                            cv2.imwrite(f'./_temp_img_dir/{formatted_datetime}_cropped.png', cropped_image)
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


class FileFinderClass:
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

    def find_latest_file(self):
        file_list = os.listdir(self.folder_path)
        sorted_files = sorted(file_list, key=lambda x: os.path.getmtime(os.path.join(self.folder_path, x)), reverse=True)
        if len(sorted_files) != 0:
            latest_file_path = os.path.join(self.folder_path, sorted_files[0])
        else:
            latest_file_path = None
        return latest_file_path


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
        sharpen_value_2 = [[0, -1, 0], [-1, 6, -1], [0, -1, 0]]
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
        임계값을 적용해서 텍스트 인식률을 향상
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

# ===================================================================================================================

def ExceptionHook(exctype, value, traceback):
    """
    PyQt 경고 출력용 함수입니다. (지금처럼 클래스 밖의 메인 함수로 선언되어야 합니다)
    """
    sys.__excepthook__(exctype, value, traceback)
    sys.exit(1)  # 이 줄은 예외 처리 후 프로그램을 종료하고 싶을 때 추가하고, 프로그램을 종료하지 않고 예외만 출력하고 싶은 경우 삭제

if __name__ == "__main__":
    sys.excepthook = ExceptionHook  # PyQt 경고 출력용 함수
    try:
        app = QApplication(sys.argv)
        fontDB = QFontDatabase()
        fontDB.addApplicationFont('./_font/Pretendard-Medium.ttf')  # 폰트 지정
        app.setFont(QFont('Pretendard Medium'))
        run = MainClass()
        run.show()
    except MemoryError:
        print(">> 메모리 오류가 발생")
    except Exception as e:
        print(f">> 예외 발생: {e}")

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing Window...")
        