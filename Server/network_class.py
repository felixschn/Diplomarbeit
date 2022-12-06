import socketserver
import context_information_creation as cic
from datetime import datetime

HOST = "localhost"
PORT = 9999


class ConnectionTCPHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())


with socketserver.TCPServer((HOST, PORT), ConnectionTCPHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    # server.serve_forever()

    context_information_1 = cic.ContextInformationCreation(
        cic.battery_information(), 30, "141.4378366,-25.95915986",
        datetime.now(), datetime.now())

    context_information_2 = cic.ContextInformationCreation(
        cic.battery_information(), cic.distance_generator(), cic.location_generator(),
        datetime.now())

    print(context_information_1)
    print(context_information_2)

