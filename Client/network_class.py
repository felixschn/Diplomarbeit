import json
import random
import socketserver
from datetime import datetime, timedelta
from inspect import getframeinfo, currentframe

import Client.reasoning
import Client.weights
import context_information_database

HOST = "localhost"

# the range of possible port numbers must be n-1 with respect to the for loop in the function called connection to server in main.py, or else the server will
# listen to a port that has never been called from the client
PORT = random.randint(64997, 64999)
time_format = '%Y-%m-%dT%H:%M:%S.%f'


def process_update_messages(received_data_dict):
    # deserialization of the received byte string back to json format in order to create table columns from dictionary keys
    context_information_database.update_context_information_keystore(received_data_dict)


def process_security_mechanism_information(received_data_dict):
    # check if the number of mode_values and modes is not equal
    if received_data_dict['modes'] != len(received_data_dict['mode_values']):
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """update message for security_mechanism_information: the number of modes and mode values are not equal""")
        return

    context_information_database.update_security_mechanisms_information(received_data_dict)


def process_context_information_messages(received_data_dict):
    global weight, max_weight
    db_table_name = 'received_context_information'

    # TODO: check timestamp in received data and compare with system time in order to neglect context information
    try:
        if datetime.strptime(received_data_dict['elicitation_date'], time_format) > datetime.now() + timedelta(minutes=0):
            print("""[ERROR]: date from received data is greater than system time; Context data will be ignored\n""")
            return

    except:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno, """while comparing system time with received context information in""")
        return

    try:
        if datetime.strptime(received_data_dict['elicitation_date'], time_format) < datetime.strptime(
                context_information_database.get_latest_date_entry(db_table_name), time_format):
            # TODO decide how to deal with received data which is older then the latest database entry --> save but not process or not even save?
            print("Received context information is older than the latest database entry")
            print("Context data will be ignored")
            print("-----------------------------")
            return
    except:
        print("timestamp error while comparing the latest database entry with received context information")

    # evaluate possible set of security mechanisms with respect to data origin (country) and other params which has to be implemented
    options = Client.reasoning.create_all_possible_permutations(received_data_dict)

    try:
        weight, max_weight = Client.weights.calculate_weights(received_data_dict)
        received_data_dict['weight'] = weight
        print("calculated weight: ", weight)

    except TypeError:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno, """weight calculation was not possible""")

    try:
        best_option = Client.weights.choose_option(weight, max_weight, list(options))
        print(best_option, "\n")
        received_data_dict['best_option'] = str(best_option)

    except:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno, """best_option calculation was not possible""")

    # deserialization of the received byte string back to json for creating
    # table columns out of the dictionary keys
    context_information_database.update_context_information(received_data_dict)


class ConnectionTCPHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        print(f'Connected: {self.client_address[0]}:{self.client_address[1]}\n')
        while True:
            try:
                self.data = self.request.recv(1024).strip()

            except:
                print("----Lost connection to client----")
                print("----Waiting for reconnection----")
                break

            print("{} wrote:".format(self.client_address[0]))
            print(self.data.decode('utf-8'))

            # create a dict out of the received data and forward the data to designated methods to process the data for context evaluation
            try:
                received_data_dict = json.loads(self.data)

                match received_data_dict['message_type']:
                    case 'context_information':
                        process_context_information_messages(received_data_dict)
                    case 'keystore_update':
                        process_update_messages(received_data_dict)
                    case 'security_mechanisms_information':
                        process_security_mechanism_information(received_data_dict)
                    case _:
                        frame_info = getframeinfo(currentframe())
                        print("""\n[ERROR] in""", frame_info.filename, "in line", frame_info.lineno,
                              """\nmessage type is unknown, received data will be ignored""")
                        break

            except json.JSONDecodeError:
                frame_info = getframeinfo(currentframe())
                print("[ERROR] in""", frame_info.filename, "in line", frame_info.lineno,
                      """\n'transformation of received data failed'""")
                break


with socketserver.ThreadingTCPServer((HOST, PORT), ConnectionTCPHandler) as server:
    # Activate the server; this will keep running until an interrupt is sent to the program with Ctrl-C
    print("---- Waiting for connection at port", PORT, "----")
    server.serve_forever()

# TODO: if I manually stop the run of the programm all client send context information is lost --> example: stopped process after receiving context information with id 32 --> restarted server and received information 39
