"""
- mainClass: 메인 윈도우 클래스
- joinClass: 회원가입 다이얼로그
최초 작성: 2023-08-27 18:45
최종 수정: 2023-08-28 03:00
"""

import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from _ui.ui_main_form import Ui_mainForm
from _ui.ui_join_form import Ui_joinForm
import psycopg2
from interaction_db import InteractionToDB

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



    def send_user_info_to_main_class(self, data_list):
        # 데이터를 메인 클래스로 옮긴다,
        pass




class MainClass(QMainWindow, Ui_mainForm):
    """
    메인 윈도우 클래스
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUi()
        self.initSignal()
        self.initFunc()


    def initUi(self):
        """
        GUI 스타일시트의 초기화를 담당합니다.
        """
        self.stackedWidget.setCurrentIndex(0)  # 메인 페이지 0번 인덱스 고정
        self.setWindowFlags(Qt.FramelessWindowHint)  # 테두리 제거
        self.icon_title_img.setIcon((QIcon('./_icons/cam_icon_white.png')))
        self.icon_open_id.setIcon((QIcon('./_icons/person_icon.png')))
        self.icon_open_pw.setIcon((QIcon('./_icons/lock_icon.png')))
        self.lb_main_title_background.setPixmap(QPixmap('./_icons/main_title.png'))

    def initSignal(self):
        """
        버튼 및 시그널 연결의 초기화를 담당합니다.
        + 추가 내용 : DB 상호작용 오브젝트 생성
        """
        self.btn_open_login.clicked.connect(lambda: print(">> stackedWidget: index 1"))
        self.btn_open_login.clicked.connect(self.log_in_check)
        self.btn_open_signup.clicked.connect(lambda: print(">> 회원가입 버튼 클릭"))
        self.btn_open_signup.clicked.connect(self.signup_dialog_act)
        self.btn_main1_close.clicked.connect(lambda: print(">> main window close") or QApplication.quit())
        self.btn_main2_close.clicked.connect(lambda: print(">> main window close") or QApplication.quit())

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


    # def signup_show_event(self):
    #     self.join_dialog = joinClass()
    #     self.join_dialog.show()


# class joinClass(QDialog, Ui_joinForm):
#     """
#     회원가입 다이얼로그 클래스
#     """
#     def __init__(self):
#         super().__init__()
#         self.signals = SignalManager()
#         self.setupUi(self)
#
#     def initUi(self):
#         pass
#
#     def initSignal(self):
#         pass
#
#     def initFunc(self):
#         pass


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