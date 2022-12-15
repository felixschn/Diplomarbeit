import json
import random
import socketserver
from datetime import datetime, timedelta

import Client.weights
import Client.reasoning
import context_information_database

HOST = "localhost"

# range of possible port numbers has to be n-1 with respect to the for loop at def connection to server
# ...in main.py, otherwise server can listen to port which is never been called from client
PORT = random.randint(64997, 64999)
print(PORT)
time_format = '%Y-%m-%dT%H:%M:%S.%f'
context_information_database.create_context_information_database()


class ConnectionTCPHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:

        print(f'Connected: {self.client_address[0]}:{self.client_address[1]}')

        while True:
            try:
                self.data = self.request.recv(1024).strip()
            except:
                print("...Lost connection to client...")
                print("...Waiting for reconnection...")
                break

            print("{} wrote:".format(
                self.client_address[0]))
            print(self.data.decode('utf-8'))

            # TODO: check timestamp in received data and compare with system time in order to neglect context information

            # create dict out of received data; call calculate_weights and add to dict
            try:
                received_data_dict = json.loads(self.data)
            except:
                print("transformation of received data failed")
                break

            try:
                if datetime.strptime(received_data_dict['elicitation_date'],
                                     time_format) > datetime.now() + timedelta(minutes=0):
                    print("Context elicitation error [date from received data is greater than system time]")
                    print("Context data will be ignored")
                    print("------------------------------")
                    continue
            except:
                print("timestamp error while comparing system time with received context information")
                continue

            try:
                if datetime.strptime(received_data_dict['elicitation_date'], time_format) < datetime.strptime(
                        context_information_database.get_latest_date_entry(), time_format):
                    # TODO decide how to deal with received data which is older then the latest database entry --> save but not process or not even save?
                    print("Received context information is older than the latest database entry")
                    print("Context data will be ignored")
                    print("-----------------------------")
                    continue
            except:
                print("timestamp error while comparing the latest database entry with received context information")

            received_data_dict['nation'] = 'russia'
            options = Client.reasoning.reasoning(received_data_dict)

            weight, max_weight = Client.weights.calculate_weights(json.loads(self.data))
            received_data_dict['weight'] = weight
            best_option = Client.weights.choose_option(weight, max_weight, options)

            # deserialization of the received byte string back to json for creating
            # table columns out of the dictionary keys
            context_information_database.create_table_context_information_database(received_data_dict)
            context_information_database.insert_values_ci_db(received_data_dict)


with socketserver.TCPServer((HOST, PORT), ConnectionTCPHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print("Waiting for connection")
    server = socketserver.ThreadingTCPServer(('', 8000), ConnectionTCPHandler)
    server.serve_forever()
    print('Connection')

# TODO:if I manually stop the run of the programm all client send context information is lost --> example: stopped process after receiving context information with id 32 --> restarted server and received information 39
