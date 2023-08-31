import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Qt_ui._ui.search_ui import Ui_SearchForm

class SearchClass(QMainWindow, Ui_SearchForm):
    def __init__(self):
        super().__init__()
        self.draggable = False
        self.offset = None
        self.setupUi(self)
        self.initUi()
        self.initSignal()

    def initUi(self):
        self.stackedWidget.setCurrentIndex(1)  # 시작시 메인 페이지 0번 인덱스 고정
        self.setWindowFlags(Qt.FramelessWindowHint)  # 윈도우창 테두리 제거
        self.icon_top_img.setIcon(QIcon('./_icons/cam_icon_white.png'))
        self.first_page_label.setPixmap(QPixmap('./_icons/intro_page.png'))
        self.btn_main_close.clicked.connect(lambda: sys.exit(">> search window close"))
        self.btn_main_minimized.clicked.connect(self.showMinimized)
        self.tableWidget.resizeColumnsToContents()

        # 마우스 커서
        self.setCursor(QCursor(QPixmap('./_icons/mouse_cursor_type1.png')))
        self.le_vehicle_info.setCursor(QCursor(QPixmap('./_icons/mouse_cursor_type2.png')))
        self.le_first_time.setCursor(QCursor(QPixmap('./_icons/mouse_cursor_type2.png')))
        self.le_second_time.setCursor(QCursor(QPixmap('./_icons/mouse_cursor_type2.png')))
        self.le_vehicle_type.setCursor(QCursor(QPixmap('./_icons/mouse_cursor_type2.png')))

    def initSignal(self):
        self.time_func()

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

    def time_func(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.changeStackedWidgetIndex)
        self.timer.start(3000)

    def changeStackedWidgetIndex(self):
        self.stackedWidget.setCurrentIndex(0)


# ====================================================================================================================


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
        run = SearchClass()
        run.show()
    except MemoryError:
        print(">> 메모리 오류가 발생")
    # except Exception as e:
    #     print(f">> 예외 발생: {e}")

    try:
        sys.exit(app.exec_())
    except SystemExit:
        print("Closing Window...")
