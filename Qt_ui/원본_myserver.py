import socket
import time
import datetime

class Server:
    def __init__(self, address, port):
        self.server_address = (address, port)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(self.server_address)
        self.server_socket.listen(1)
        print(">> 클라이언트의 접속을 기다리는 중...")

    def handle_client(self, client_socket, client_address):
        current_time = datetime.datetime.now()
        formatted_datetime = current_time.strftime("%Y-%m-%d %H:%M:%S")
        while True:
            data = client_socket.recv(1024)
            if not data:
                print(f">> {client_address[0]}:{client_address[1]} 이(가) 종료했습니다. ({formatted_datetime})")
                break
            message = data.decode()
            print(f">> 클라이언트로부터 받은 메시지: {message}")
            response = f"You said: {message}"
            client_socket.send(response.encode())

        client_socket.close()

    def server_start(self):
        current_time = datetime.datetime.now()
        formatted_datetime = current_time.strftime("%Y-%m-%d %H:%M:%S")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f">> {client_address[0]}:{client_address[1]} 이(가) 접속했습니다. ({formatted_datetime})")

            try:
                self.handle_client(client_socket, client_address)
            except ConnectionResetError:
                print(f">> {client_address[0]}:{client_address[1]} 이(가) 강제 종료되었습니다. ({formatted_datetime})")
            finally:
                client_socket.close()


if __name__ == '__main__':
    server = Server('127.0.0.1', 7777)
    server.server_start()
