import json
import random
import socketserver
from datetime import datetime, timedelta
from inspect import getframeinfo, currentframe

import Client.reasoning
import Client.weights
import context_information_database

HOST = "localhost"

# range of possible port numbers has to be n-1 with respect to the for loop at def connection to server
# ...in main.py, otherwise server can listen to port which is never been called from client
PORT = random.randint(64997, 64999)
print(PORT)
time_format = '%Y-%m-%dT%H:%M:%S.%f'


def process_update_messages(received_data_dict):
    # deserialization of the received byte string back to json for creating
    # table columns out of the dictionary keys
    context_information_database.update_context_information_keystore(received_data_dict)


def process_context_information_messages(received_data_dict):
    db_table_name = 'received_context_information'

    # TODO: check timestamp in received data and compare with system time in order to neglect context information
    try:
        if datetime.strptime(received_data_dict['elicitation_date'],
                             time_format) > datetime.now() + timedelta(minutes=0):
            print("Context elicitation error [date from received data is greater than system time]")
            print("Context data will be ignored")
            print("------------------------------")
            return
    except:
        print("timestamp error while comparing system time with received context information")
        return

    # try:
    #     if datetime.strptime(received_data_dict['elicitation_date'], time_format) < datetime.strptime(
    #             context_information_database.get_latest_date_entry(db_table_name), time_format):
    #         # TODO decide how to deal with received data which is older then the latest database entry --> save but not process or not even save?
    #         print("Received context information is older than the latest database entry")
    #         print("Context data will be ignored")
    #         print("-----------------------------")
    #         return
    # except:
    #     print("timestamp error while comparing the latest database entry with received context information")

    # TODO get nation number out of received package and compare with nation number list to retrieve correct nation
    # TODO at the moment the database entry would contain redundant nation entries --> get rid of one ?
    received_data_dict['nation'] = 'russia'

    # evaluate possible set of security mechanisms with respect to data origin (country) and other params which has to be implemented
    options = Client.reasoning.reasoning(received_data_dict)

    try:
        weight, max_weight = Client.weights.calculate_weights(received_data_dict)
        received_data_dict['weight'] = weight
        best_option = Client.weights.choose_option(weight, max_weight, options)
        print(best_option)
    except TypeError:
        frameinfo = getframeinfo(currentframe())
        print("""[ERROR]:weight calculation was not possible in""", frameinfo.filename, "in line:", frameinfo.lineno)

    # deserialization of the received byte string back to json for creating
    # table columns out of the dictionary keys
    context_information_database.update_context_information(received_data_dict)


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

            # create dict out of received data and forward data to designated methods in order to process data for context evaluation
            try:
                received_data_dict = json.loads(self.data)

                match received_data_dict['message_type']:
                    case 'context_information':
                        process_context_information_messages(received_data_dict)
                    case 'keystore_update':
                        process_update_messages(received_data_dict)
                    case _:
                        print('message type is unknown')
                        print('received data will be ignored')
                        break

            except json.JSONDecodeError:
                print("transformation of received data failed")
                break


with socketserver.ThreadingTCPServer((HOST, PORT), ConnectionTCPHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print("Waiting for connection")
    server.serve_forever()
    print('Connection')

# TODO:if I manually stop the run of the programm all client send context information is lost --> example: stopped process after receiving context information with id 32 --> restarted server and received information 39
