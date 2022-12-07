import socketserver
import context_information_creation as cic
from datetime import datetime
import json

HOST = "localhost"
PORT = 9999
time_format = '%Y-%m-%dT%H:%M:%S.%f'


class ConnectionTCPHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data)


with socketserver.TCPServer((HOST, PORT), ConnectionTCPHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
