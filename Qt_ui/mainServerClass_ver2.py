"""
최초 작성: 2023-08-30
최종 수정: 2023-08-31 17:00
"""

import socket
import time
import datetime
import json
from threading import Thread
from Qt_ui.interaction_db import InteractionToDB

HEADER_BUFFER = 32
BUFFER = 1024

class Server:
    def __init__(self, address, port):
        self.server_address = (address, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(1)
        self.interaction_to_db_obj = InteractionToDB()  # DB 인스턴스 생성
        print(">> 클라이언트의 접속을 기다리는 중...")

    def handle_client(self, client_socket, client_address):
        json_obj = None
        current_time = datetime.datetime.now()
        formatted_datetime = current_time.strftime("%Y-%m-%d %H:%M:%S")
        while True:
            data = client_socket.recv(BUFFER)

            if not data:
                print(f">> {client_address[0]}:{client_address[1]} 이(가) 강제 종료되었습니다. ({formatted_datetime})")
                break

            json_data = data.decode()
            print(">> 디코딩 되기 전 JSON DATA:", json_data)

            try:
                json_obj = json.loads(json_data)

            except json.JSONDecodeError:
                continue

            print(f">> 클라이언트로부터 JSON 데이터 수신: {json_obj}")

            response_data = {"Response": "JSON 데이터를 성공적으로 수신"}
            response = json.dumps(response_data)
            client_socket.send(response.encode())

            # 서버로 전달 된 내용 처리하는 함수 여기에.
            self.process_get_data(client_socket, json_obj)

        client_socket.close()

    def process_get_data(self, client_socket, get_data):
        header = get_data['header']
        if header == 'login':
            self.process_login(client_socket, get_data)
        elif header == 'membership_join':
            self.process_membership_join(get_data)
        elif header == 'car_data':
            self.process_car_data(get_data)

    def process_login(self, client_socket, data):
        user_input_car_number = data['user_input_car_number']
        user_input_pw = data['user_input_pw']
        ret = self.interaction_to_db_obj.log_in(user_input_car_number, user_input_pw)
        try:
            idx = ret.find("@")  # 첫 번째 "o"의 위치를 반환
        except:
            idx = 0
        send_login_msg = {
            'header': 'return_login',
            'user_id': ret[idx+1:],
            'return': ret[:idx]
        }

        response = json.dumps(send_login_msg)
        client_socket.send(response.encode())

    def process_membership_join(self, data):
        car_plate_number = data['car_plate_number']
        password = data['password']
        name = data['name']
        contact = data['contact']
        self.interaction_to_db_obj.insert_membership_registration(car_plate_number, password, name, contact)

    def process_car_data(self, data):
        print(data)
        user_id = data['user_id']
        ocr_recog = data['ocr_recog']
        vehicle_classifi = data['vehicle_classifi']
        GPS = data['GPS']
        current_time = data['current_time']
        self.interaction_to_db_obj.insert_detected_car_info(user_id, ocr_recog, vehicle_classifi, GPS, current_time)

    def server_start(self):
        current_time = datetime.datetime.now()
        formatted_datetime = current_time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f">> {client_address[0]}:{client_address[1]} 이(가) 접속했습니다. ({formatted_datetime})")
                try:
                    self.handle_client(client_socket, client_address)
                except ConnectionResetError:
                    print(f">> {client_address[0]}:{client_address[1]} 이(가) 강제 종료되었습니다. ({formatted_datetime})")
                finally:
                    client_socket.close()
                    print(f">> {client_address[0]}:{client_address[1]} 이(가) 연결을 종료했습니다. ({formatted_datetime})")
        except KeyboardInterrupt:
            print(">> 서버가 수동으로 중지!")
        except Exception as e:
            print(f">> 오류 발생: {e}")

    def json_default(self, value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S.%f")
        # raise TypeError('not JSON serializable')

    def send_fuc(self, send_data: dict):  # 다시 client의 Back으로 보내는 작업
        # json_data = json.dumps(send_data, default=self.json_default).encode("utf-8")
        json_data = json.dumps(send_data).encode("utf-8")
        data_len = len(json_data)
        header_data = f"{data_len:032d}".encode("utf-8")
        self.server_socket.send(header_data)
        self.server_socket.send(json_data)

    # client의 Back으로부터 데이터를 받는 작업
    def receive_fuc(self):
        while True:
            # 먼저 헤더 데이터를 받는다.
            # header_buffer 사이즈인 32만큼을 채워서 보내서, 다음 recv 가 동작하도록 한다.
            received_byte_header: bytes = self.server_socket.recv(HEADER_BUFFER)
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
                received_byte_data += self.server_socket.recv(main_data_buffer)
                # 설정된 버퍼만큼 받아서 누적 저장
                received_header_int -= main_data_buffer
            received_json_data = received_byte_data.decode("utf-8")
            received_data = json.loads(received_json_data)
            # self.process_get_data(received_data)
            # print(">> 받은 데이터", received_data)

    # def process_get_data(self, get_data):
    #     print(get_data)


    def recv_run(self):
        receive_theread = Thread(target=self.receive_fuc, daemon=True)  # 이걸 계속 돌리려면, receive_fuc 함수를 while문 하나 더 씌워서 돌려야 할 것 같다.
        receive_theread.start()

if __name__ == '__main__':
    server = Server('127.0.0.1', 7777)
    server.server_start()
