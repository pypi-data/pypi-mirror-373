# httpkit/server.py
import socket
from .router import Router
from .request import Request

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.router = Router()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)

    def route(self, path, method):
        # هذا هو الجزء الأهم. الآن، `route` تعيد دالة مُزيّن من الـ `Router`
        if method.upper() == "GET":
            return self.router.get(path)
        elif method.upper() == "POST":
            return self.router.post(path)
        else:
            raise ValueError(f"Unsupported method: {method}")

    def run(self):
        print(f"الخادم يعمل على http://{self.host}:{self.port}")
        while True:
            client_connection, client_address = self.server_socket.accept()
            request_data = client_connection.recv(4096).decode('utf-8')
            
            req = Request(request_data)
            handler = self.router.find_handler(req.path, req.method)
            
            if handler:
                handler(client_connection, req)
            else:
                not_found_response = b"HTTP/1.1 404 Not Found\r\nContent-Length: 9\r\n\r\nNot Found"
                client_connection.sendall(not_found_response)
            
            client_connection.close()
