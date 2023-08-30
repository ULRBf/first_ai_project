import socket


class ClientClass:
    def __init__(self, server_address, server_port):
        self.server_address = (server_address, server_port)
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)

    def send_data(self, message):
        self.client_socket.send(message.encode())
        data = self.client_socket.recv(1024)
        print("Received:", data.decode())

    def close(self):
        self.client_socket.close()

if __name__ == '__main__':
    client = ClientClass('127.0.0.1', 7777)

    try:
        while True:
            user_input = input("Enter a message (or 'quit' to exit): ")
            if user_input.lower() == 'quit':
                break
            client.send_data(user_input)
    except KeyboardInterrupt:
        pass  # Allow the user to exit gracefully using Ctrl+C

    client.close()
