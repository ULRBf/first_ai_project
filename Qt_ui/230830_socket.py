# 서버 - chatroom은 서버에서 이루어지도록 하자.
from socket import *
from threading import *
import ast
import pandas as pd
from queue import Queue
pd.set_option('display.max_columns', None)
import time
import json
from between_server_and_database import BetweenServerAndDataBase
from datetime import datetime
from builtins import enumerate
import random
import os
import base64

HEADER_BUFFER = 32
BUFFER = 1024

# 채팅방 객체는 유저가 채팅 창을 열고 있을 때 사용한다. 그리고 다른 페이지로 가면, 해당 객체를 죽인다.
# 이를 위해서 서버에 접속해있는 유저의 id, 소켓주소를 서버가 가지고 있어야 한다.
# 그렇지 않고 소켓주소를 알 수 있는 방법이 있나?

class UserChatRoom(Thread):
    def __init__(self, user_id, user_accept_socket):
        super().__init__()
        print("유저 채팅방 객체 생성.")
        self.between_server_and_database = BetweenServerAndDataBase()
        self.room_number = str(self.between_server_and_database.get_user_chat_room_number(user_id))  # 유저 id로 DB에서 찾아온다.
        self.user_id = user_id
        self.user_socket = user_accept_socket.this_socket
        self.set_chat_room_log()
        self.manager_id = None
        self.manager_socket = None
        self.message_queue = Queue()
        self.run()
        print("채팅방 room number 확인용", self.room_number, type(self.room_number))
        # 확인용.
        # print(f"{self.room_number = }")
        # print(f"{self.user_id = }")
        # print(f"{self.user_socket = }")

    def get_user_id(self):
        return self.user_id

    def get_room_number(self):
        return self.room_number

    def set_chat_room_log(self):
        chat_log_data = self.between_server_and_database.get_chat_log(self.room_number)
        # 해당 데이터를 유저에게 보내야함.
        send_chat_log_data = {
            'header': 'load_chat_log',
            'data_1': chat_log_data
        }
        # 유저에게로 송신
        json_data = json.dumps(send_chat_log_data).encode("utf-8")
        data_len = len(json_data)
        header_data = f"{data_len:032d}".encode("utf-8")
        self.user_socket.send(header_data)
        self.user_socket.send(json_data)


    def put_to_message_queue(self, send_data):
        self.message_queue.put(send_data)

    def get_to_message_queue(self):
        while True:
            get_data = self.message_queue.get()
            print("데이터 잘 들어오는지 확인", get_data)
            if get_data["user_type"] == "manager":
                self.manager_id = get_data["user_id"]
                self.manager_socket = get_data["manager_socket"]
                # 매니저 id, 소켓데이터 채워야 한다. + 왜 채팅 다시 안올라가냐 + 채팅방 없는경우, 다시 돌아가서 dB저장되는 코드 작성해야 함.

            now_time = datetime.now()
            time_str = now_time.strftime("%Y-%m-%d %H:%M:%S.%f")
            # --------------------------------------------DB에 저장
            if get_data["user_type"] == "user":
                save_data = {
                    'room_number': self.room_number,
                    'user_id': self.user_id,
                    'chat_contents': get_data["data_1"],
                    'chat_time': time_str
                }
            else:  # get_data["user_type"] == "manager"
                save_data = {
                    'room_number': self.room_number,
                    'user_id': self.user_id,
                    'chat_contents': get_data['typing_data'],
                    'chat_time': time_str
                }
            self.save_message_to_db(save_data)
            # --------------------------------------------DB에 저장

            # --------------------------------------------다른 사람에게 전송
            self.send_message(get_data)
            # 받은쪽에서 본인과 동일한 아이디인 경우 오른쪽 UI로, 다른 아이디인경우 왼쪽 UI로 화면상에 출력되도록 한다
            # --------------------------------------------다른 사람에게 전송

    def save_message_to_db(self, save_data):
        self.between_server_and_database.save_chat_data_to_db(save_data)

    def send_message(self, get_data_):
        if get_data_["user_type"] == "user":
            send_messgae_data = {
                "header": "send_message_from_chat_room",
                "message": get_data_["data_1"],
                "type": get_data_["type"],
                "user_id": get_data_["user_id"],
                "user_type": get_data_["user_type"],
                "time": datetime.now()
            }
        else:  # get_data["user_type"] == "manager"
            send_messgae_data = {
                "header": "send_message_from_chat_room_ver_manager",
                "message": get_data_["typing_data"],
                "type": get_data_["type"],
                "user_id": get_data_["user_id"],
                "user_type": get_data_["user_type"],
                "time": datetime.now()
            }

        # 보낼 내용 조정
        json_data = json.dumps(send_messgae_data, default=self.json_default).encode("utf-8")
        data_len = len(json_data)
        header_data = f"{data_len:032d}".encode("utf-8")

        # if문으로 None인지 아닌지 판단해서 있을 때, 없을 때 조건 갈라서 보내야 하고, 길이, 본 내용 따로 보내는거 적용해야한다.
        if self.manager_id is not None:
            # 메시지 보내기
            self.manager_socket.send(header_data)
            self.manager_socket.send(json_data)
            print("매니저 있음.", json_data)

        if self.user_id is not None:
            # 메시지 보내기
            self.user_socket.send(header_data)
            self.user_socket.send(json_data)
            print("유저 있음.", json_data)


    def get_id_list(self):
        return [self.user_id, self.manager_id]

    def run(self):
        get_message_theread = Thread(target=self.get_to_message_queue, daemon=True)
        get_message_theread.start()

    def json_default(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S.%f")
        elif isinstance(value, bytes):
            return value.decode('utf-8')
        raise TypeError('not JSON serializable')
    # https://dgkim5360.tistory.com/entry/not-JSON-serializable-error-on-python-json



class Server:
    def __init__(self):
        target_host = "127.0.0.1"
        target_port = 9995
        self.onlie_user_data_list = list()
        self.chat_room_list = list()
        self.server_accept_socket_queue = Queue()
        self.accept_socket_server_queue = Queue()
        self.address = (target_host, target_port)
        self.ServerSocket = socket(AF_INET, SOCK_STREAM)
        self.ServerSocket.bind(self.address)  # IP주소와 포트번호를 맵핑
        self.ServerSocket.listen()
        self.thread_start()  # server의 get 쓰레드 돌리기.

        while True:
            ClientSocket, address_info = self.ServerSocket.accept()
            # 서버에 있는 리스트 주소를 같이 넘겨준다.
            accept_socket_object = AcceptSocket(ClientSocket, address_info, self.onlie_user_data_list, self.server_accept_socket_queue, self.accept_socket_server_queue)
            accept_socket_object.recv_run()
            user_data = {"id": None, "accept_socket": accept_socket_object}  # id는 나중에 채우도록.
            self.onlie_user_data_list.append(user_data)

    def thread_start(self):
        get_thread = Thread(target=self.get_commend_from_queue, daemon=True)
        get_thread.start()

    def get_commend_from_queue(self):
        while True:
            get_data = self.server_accept_socket_queue.get()
            self.execute_get_data(get_data)

    def execute_get_data(self, get_data):
        # 받아온 명령 처리.
        header = get_data["header"]
        if header == 'request_chat_room':
            find_user_socket = None
            # id를 통해 서버에서 유저소켓정보 가져오기
            user_id = get_data["data_1"]["id"]
            for user_data in self.onlie_user_data_list:
                if user_data["id"] == user_id:
                    find_user_socket = user_data["accept_socket"]
            user_chat_room_object = UserChatRoom(user_id, find_user_socket)
            # 채팅방 객체 만들어서 채팅룸 리스트에 넣기.
            self.chat_room_list.append(user_chat_room_object)
            print("방이 있는지 확인", self.chat_room_list)

        elif header == "user_typing_data":
            user_id = get_data["user_id"]
            # 이제 넘겨줘야 함.
            # id값으로 for문을 돌아서 방을 찾아서 그 방으로 메시지 전송
            for chat_room in self.chat_room_list:
                if chat_room.get_user_id() == user_id:
                    chat_room.put_to_message_queue(get_data)

        elif header == "delete_chat_room":
            # 채팅방 리스트에서 해당 방 삭제.
            num = 0
            user_id = get_data["user_id"]
            for idx, chat_room in enumerate(self.chat_room_list):
                if chat_room.get_user_id() == user_id:
                    num = idx
            del self.chat_room_list[num]

        elif header == "manager_typing_data":
            exist_room_test = False
            room_number = get_data["room_number"]
            print("선택된 방 번호", room_number, type(room_number))
            # 해당 방 번호의 채팅방이 존재하는지 서버에 확인
            for chat_room in self.chat_room_list:
                # 방번호가 있으면 데이터 전송
                if chat_room.get_room_number() == room_number:
                    chat_room.put_to_message_queue(get_data)
                    exist_room_test = True
            print("방 존재 여부", exist_room_test)
            if exist_room_test is not True:
                # 다시 소켓으로. 데이터 전송
                self.accept_socket_server_queue.put(get_data)

class AcceptSocket:
    def __init__(self, ClientSocket_, address_info_, onlie_user_data_list, server_accept_socket_queue, accept_socket_server_queue):  # 서버의 온라인 유저 데이터에 접속할 수 있게 인자로 리스트 주소를 받음.
        self.onlie_user_data_list = onlie_user_data_list  # 로그인할 때 로그인 id데이터가 채워지도록 한다.
        self.server_accept_socket_queue = server_accept_socket_queue  # 서버에 있는 Queue(서버로 명령 전달 용)
        self.accept_socket_server_queue = accept_socket_server_queue
        self.between_server_and_database = BetweenServerAndDataBase()
        self.this_socket = ClientSocket_
        self.fd = self.this_socket.fileno()
        self.this_socket_address = address_info_
        self.re_get_data_thread_start()

        print("{}가 접속했습니다.".format(self.this_socket_address))
        print(f"Socket 정보 : {self.this_socket}")
        print(f"address 정보 : {self.this_socket_address}")

    def re_get_data_thread_start(self):
        re_get_thread = Thread(target=self.re_get_data_from_server_queue, daemon=True)
        re_get_thread.start()

    def re_get_data_from_server_queue(self):
        while True:
            re_get_data = self.accept_socket_server_queue.get()
            self.execute_re_get_data(re_get_data)

    # 채팅방 클래스로 갔다가 다시 돌아온 경우 -> DB저장을 위해서.
    def execute_re_get_data(self, re_get_data):
        header = re_get_data["header"]
        if header == "manager_typing_data":
            # print(f"{re_get_data = }")
            # 키 값 변경을 위한 작업(typing_data -> chat_contents)
            re_get_data["chat_contents"] = re_get_data["typing_data"]
            del re_get_data["typing_data"]
            # DB저장 후, 다시 백으로 보내야 함.
            self.between_server_and_database.save_chat_data_to_db(re_get_data)
            # 헤더 조금 바꿔서 Back으로 보내기.
            re_get_data["header"] = "re_manager_typing_data"
            self.execute_recv_data_type_dict(re_get_data)


    def get_fd(self):
        return self.fd

    def json_default(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S.%f")
        # raise TypeError('not JSON serializable')

    # 다시 client의 Back으로 보내는 작업
    def send_fuc(self, send_data: dict):
        json_data = json.dumps(send_data, default=self.json_default).encode("utf-8")
        # json_data = json.dumps(send_data).encode("utf-8")
        data_len = len(json_data)
        header_data = f"{data_len:032d}".encode("utf-8")
        self.this_socket.send(header_data)
        self.this_socket.send(json_data)

    # client의 Back으로부터 데이터를 받는 작업
    def receive_fuc(self):
        while True:
            # 먼저 헤더 데이터를 받는다.
            # header_buffer 사이즈인 32만큼을 채워서 보내서, 다음 recv 가 동작하도록 한다.
            received_byte_header: bytes = self.this_socket.recv(HEADER_BUFFER)
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
                received_byte_data += self.this_socket.recv(main_data_buffer)
                # 설정된 버퍼만큼 받아서 누적 저장
                received_header_int -= main_data_buffer
            received_json_data = received_byte_data.decode("utf-8")
            received_data = json.loads(received_json_data)
            # print("받은 데이터", received_data)
            self.data_type_check(received_data)

    def data_type_check(self, received_data):
        received_data: dict
        if received_data["type"] == "dictionary":
            self.execute_recv_data_type_dict(received_data)
        elif received_data["type"] == "image":
            self.execute_recv_data_type_image(received_data)

    def execute_recv_data_type_dict(self, recv_data: dict):
        header = recv_data["header"]
        if header == "try_login":
            result_data = self.login_check_function(recv_data)
            self.send_fuc(result_data)

        elif header == "try_signup":
            result_data = self.signup_check_function(recv_data)
            self.send_fuc(result_data)

        elif header == "request_chat_room":
            # 채팅방이 개설되어야 함. 근데 이 채팅방이 서버에 개설되어야 한다. 소켓이 아니라. -> 서버로 넘기자.
            self.server_accept_socket_queue.put(recv_data)

        elif header == "user_typing_data":
            # 서버로 해당 내용이 옮겨가야 한다.
            self.server_accept_socket_queue.put(recv_data)

        elif header == "delete_chat_room":
            # 서버로 해당 내용이 옮겨가야 한다.
            self.server_accept_socket_queue.put(recv_data)
            # self.server_accept_socket_queue.put(recv_data)

        elif header == "request_room_data":
            room_data = self.between_server_and_database.get_chat_room_unit_from_db()
            room_data_from_db = {
                "header": "request_room_data",
                "type": "dictionary",
                "data_1": room_data
            }
            self.send_fuc(room_data_from_db)

        elif header == "request_clicked_chat_room_data":
            room_number = recv_data["data_1"]
            this_room_chat_log = self.between_server_and_database.get_chat_log(room_number)
            request_clicked_chat_room_data = {
                "header": "request_clicked_chat_room_data",
                "type": "dictionary",
                "data_1": this_room_chat_log
            }
            self.send_fuc(request_clicked_chat_room_data)

        # 채팅방으로 이동
        elif header == "manager_typing_data":
            print("매니저 타이핑")
            recv_data["manager_socket"] = self.this_socket
            # 서버로 해당 내용이 옮겨가야 한다.(서버로 가서 채팅방이 있는지 없는지 확인해야함.)
            self.server_accept_socket_queue.put(recv_data)

        # 채팅방 갔다가 돌아온 데이터
        elif header == "re_manager_typing_data":
            print("re매니저 타이핑")
            # 형식 변환(안터지기 위해서)
            recv_data["message"] = recv_data["chat_contents"]
            recv_data["time"] = recv_data["chat_time"]
            # 백으로 바로 보내기.
            self.send_fuc(recv_data)
            # 문제가 있는 부분 -> 채팅방에서쏴지는거는 되는데, 채팅방이 안열린 곳에서 문제가 된다.

        elif header == "request_example":
            # 랜덤수 배정 유형 번호, 그 문제 위치대로 DB로 가서 데이터 주소 가져오고, DB로 가서
            # 1 또는 2중에 고르고,
            # 1 ~ len(그 유형 DB길이) 중 하나의 숫자를 선택해야함.
            example_type = random.randint(1, 2)
            # 1 유형 문제
            if example_type == 1:
                count_number = self.between_server_and_database.get_example_1_table_len_from_db()
            # 2 유형 문제
            else:  # example_type == 2:
                count_number = self.between_server_and_database.get_example_2_table_len_from_db()
                # 이제 DB에서 해당 문제를 가져와야 한다.

            random_number = random.randint(1, count_number)
            data = self.between_server_and_database.get_specific_example_from_db(example_type, random_number)
            # 이제 이 data에 있는 주소값에서 객체를 가져와야 함.

            image_data = open(data['image'], 'rb')
            read_image_data = image_data.read()
            encoded_image_data = base64.b64encode(read_image_data)

            example_csv = open(data['data_1'], 'rb')
            read_example_data = example_csv.read()

            explain_data = open(data['explain'], 'rb')
            read_explain_data = explain_data.read()

            data_dict = {
                'header': 'send_example_data',
                'example_type': data['example_type'],
                'example_number': data['example_number'],
                'image_data': encoded_image_data.decode(),
                'csv_data': read_example_data.decode('utf-8'),
                'explain_data': read_explain_data.decode('utf-8')
            }

            self.send_fuc(data_dict)
            # https://t4716.tistory.com/29

        elif header == 'submit_data_result_of_example':
            print(recv_data)
            # example_type, example_number가 None, None으로 나오는 문제가 있었음.
            # 이거 해결 해야함.
            example_type = recv_data['example_number']
            example_number = recv_data['example_number']
            get_answer_address = self.between_server_and_database.get_answer_from_db(example_type, example_number)
            print(get_answer_address)
            # 정/오 판단을 back으로 다시 전달해줘야한다.
            # 그리고 1유형 횟수, 맞은 횟수 등을 DB로 저장해야 한다.



    def execute_recv_data_type_image(self, recv_data):
        # 이미지 데이터 처리하는 용도
        pass

    def signup_check_function(self, recv_data):
        # 이제 DB연결되어야 한다.
        user_input_id = recv_data["data_1"]["id"]
        # DB로 가서 겹치는 ID가 있으면 가입 불가.
        id_data_from_db = self.between_server_and_database.check_same_id_for_signup(user_input_id)
        # 겹치는 ID가 없으면 가입 가능.
        if id_data_from_db == "no_exist_id":
            signup_data = {
                "header": "try_signup",
                "type": "dictionary",
                "data_1": "possible_make_id",
            }
            # 여기에 회원가입 DB에 저장하는 코드 있어야 함.
            self.between_server_and_database.register_signup_data(recv_data)
            # 회원가입완료와 동시에 1:1 문의 방 배정 되어야 한다.
            self.between_server_and_database.register_room_number_data(user_input_id)
            return signup_data
        else:
            signup_data = {
                "header": "try_signup",
                "type": "dictionary",
                "data_1": "impossible_make_id"
            }
            return signup_data

    def login_check_function(self, recv_data):
        """
        DB비교 등의 작업 수행
        if 있는 아이디이고, 로그인이 가능하다면
        ret_data = {"header", "로그인 가능"}
        return ret_data
        else: 로그인 불가능하다면
        ret_data = {"header", "로그인 불가능"}
        return ret_data
        """
        input_user_id = recv_data["data_1"]["id"]
        input_user_pw = recv_data["data_1"]["pw"]
        pw_data_from_db = self.between_server_and_database.get_pw_data_for_login(input_user_id)
        # print(input_user_pw, pw_data_from_db)
        # print(type(input_user_pw), type(pw_data_from_db))
        if input_user_pw == pw_data_from_db:
            # 로그인 가능
            get_user_type = self.between_server_and_database.get_user_type(input_user_id)
            login_data = {
                "header": "try_login",
                "type": "dictionary",
                "data_1": "login_success",
                "id_type_data": {"id": input_user_id, "type": get_user_type}
            }

            # 로그인이 가능할 때 현재 접속한 유저에 대한 내용을 서버로 넘겨야 한다.
            # fd(파일 디스크립터)를 이용해서 두 소켓이 맞는지 비교한다. (소켓.fileno())의 형태로 구할 수 있다.
            this_socket_fd = self.get_fd()
            for data in self.onlie_user_data_list:
                fd = data["accept_socket"].get_fd()
                if this_socket_fd == fd:
                    data['id'] = input_user_id

            # print("서버의 온라인 유저 데이터 확인용 -> ", self.onlie_user_data_list)
            return login_data

        else:
            # 로그인 불가
            login_data = {
                "header": "try_login",
                "type": "dictionary",
                "data_1": "login_fail"
            }
            return login_data

    def recv_run(self):
        receive_theread = Thread(target=self.receive_fuc, daemon=True)  # 이걸 계속 돌리려면, receive_fuc 함수를 while문 하나 더 씌워서 돌려야 할 것 같다.
        receive_theread.start()

if __name__ == "__main__":
    server_object = Server()
