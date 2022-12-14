import json
import random
import socketserver

import Client.weights
import context_information_database

HOST = "localhost"

# range of possible port numbers has to be n-1 with respect to the for loop at def connection to server
# ...in main.py, otherwise server can listen to port which is never been called from client
PORT = random.randint(64997, 64999)
print(PORT)
time_format = '%Y-%m-%dT%H:%M:%S.%f'
context_information_database.create_context_information_database()


class ConnectionTCPHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        while True:
            try:
                self.data = self.request.recv(1024).strip()
                print("{} wrote:".format(
                    self.client_address[0]))
                print(self.data.decode('utf-8'))

                # deserialization of the received byte string back to json for creating
                # table columns out of the dictionary keys
                context_information_database.create_table_context_information_database(
                    json.loads(self.data))
                context_information_database.insert_values_ci_db(json.loads(self.data))

                # call calc function to evalute recieved data
                Client.weights.calculate_weights(json.loads(self.data))

            except:
                print("...Lost connection to client...")
                print("...Waiting for reconnection...")
                break


with socketserver.TCPServer((HOST, PORT),
                            ConnectionTCPHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print("Waiting for connection")
    server.serve_forever()
    print('Connection')

# TODO:if I manually stop the run of the programm all client send context information is lost --> example: stopped process after receiving context information with id 32 --> restarted server and received information 39
