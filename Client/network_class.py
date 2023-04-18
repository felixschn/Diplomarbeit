import json
import os
import random
import socketserver
from datetime import datetime, timedelta
from importlib import reload, import_module
from inspect import getframeinfo, currentframe

import tqdm

import Client.Reasoning_Engine.Context_Model.Weight_Calculation.weights
import Client.Reasoning_Engine.Context_Model.reasoning
import Client.set_security_mechanisms
from Client.Data_Engine import context_information_database

HOST = "localhost"
BUFFER_SIZE = 4096
DELIMITER = "<delimiter>"

# the range of possible port numbers must be n-1 with respect to the for loop in the function called connection to server in main.py, or else the server will
# listen to a port that has never been called from the client
PORT = random.randint(64999, 64999)
time_format = '%Y-%m-%dT%H:%M:%S.%f'


def reload_retrieved_modules(filename, module_path):
    formatted_file_name = filename.replace('.py', '')
    imported_mod = import_module(f"{module_path}{formatted_file_name}")

    # note: Due to a security feature of the reload function, existing functions of a module remain if they are not overwritten through an update; see: the docs and
    # https://stackoverflow.com/questions/58946837/reload-function-fails-to-erase-removed-variables
    # to avoid any problems with not removed functions, the filter files will contain only one public function which has to be present and, therefore, never get deleted
    reload(imported_mod)


def process_message_weight_calculation_file(received_data, connection_handler):
    # check if received data is not empty
    if len(received_data) == 0:
        return

    print(f"Empfangen: {received_data}\n")

    _, filename, size_of_file, file_content = received_data.split(DELIMITER)
    filename = os.path.basename(filename)
    size_of_file = int(size_of_file)
    show_progress = tqdm.tqdm(range(size_of_file), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    # write the received data to a file in the 'Weight_Calculation' directory
    with open(f"D:\PyCharm Projects\Diplomarbeit\Client\Reasoning_Engine\Context_Model\Weight_Calculation\\{filename}", "wb") as received_file:
        while True:
            read_data = connection_handler.request.recv(BUFFER_SIZE)

            # break out of the loop if no further data is received
            if not read_data:
                print("---- Received read_data was empty ----")
                break

            # write the retrieved data to the file
            received_file.write(read_data)
            # update the process bar
            show_progress.update(len(read_data))

    # reloading the modules to process context information with the newest data
    reload_retrieved_modules(filename, "Client.Reasoning_Engine.Context_Model.Weight_Calculation.")

    # update the database with a filter name from the added filter file
    context_information_database.update_weight_calculation_files(filename)


def process_message_security_mechanism_file(received_data, connection_handler):
    # check if the received data is not empty
    if len(received_data) == 0:
        return

    print(f"Empfangen: {received_data}\n")

    # store the received data in various variables
    _, filename, size_of_file, file_content = received_data.split(DELIMITER)
    filename = os.path.basename(filename)
    size_of_file = int(size_of_file)
    show_progress = tqdm.tqdm(range(size_of_file), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    # write the received data to a file in the 'Security_Mechanisms' directory
    with open(f"D:\PyCharm Projects\Diplomarbeit\Client\Security_Mechanisms\\{filename}", "wb") as received_file:
        while True:
            read_data = connection_handler.request.recv(BUFFER_SIZE)

            # break out of the loop if no further data is received
            if not read_data:
                print("---- Received read_data was empty ----")
                break

            # write the retrieved data to the file
            received_file.write(read_data)
            # update the process bar
            show_progress.update(len(read_data))

    # reloading the modules to process context information with the newest data
    reload_retrieved_modules(filename, "Client.Security_Mechanisms.")

    # update the database with a filter name from the added filter file
    #context_information_database.update_security_mechanisms_file(filename)


def process_message_filter_file(received_data, connection_handler):
    # check if the received data is not empty
    if len(received_data) == 0:
        return

    print(f"Empfangen: {received_data}\n")

    # store the received data in various variables
    _, filename, size_of_file, file_content = received_data.split(DELIMITER)
    filename = os.path.basename(filename)
    size_of_file = int(size_of_file)
    show_progress = tqdm.tqdm(range(size_of_file), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    # write the received data to a file in the 'Filter' directory
    with open(f"D:\PyCharm Projects\Diplomarbeit\Client\Reasoning_Engine\Filter\\{filename}", "wb") as received_file:
        while True:
            read_data = connection_handler.request.recv(BUFFER_SIZE)

            # break out of the loop if no further data is received
            if not read_data:
                print("---- Received read_data was empty ----")
                break

            # write the retrieved data to the file
            received_file.write(read_data)
            # update the process bar
            show_progress.update(len(read_data))

    # reloading the modules to process context information with the newest data
    reload_retrieved_modules(filename, "Client.Reasoning_Engine.Filter.")

    # update the database with a filter name from the added filter file
    context_information_database.update_security_mechanisms_filter(filename)


def process_message_keystore_information(received_data_dict):
    # deserialization of the received byte string back to json format in order to create table columns from dictionary keys
    context_information_database.update_context_information_keystore(received_data_dict)


def process_message_security_mechanisms_information(received_data_dict):
    # check if the number of mode_weights and modes is not equal
    if received_data_dict['modes'] != len(received_data_dict['mode_weights']) or received_data_dict['modes'] != len(received_data_dict['mode_values']):
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """update message for security_mechanism_information: the number of modes and mode weights or mode values are not equal""")
        return

    # write retrieved information to the database
    context_information_database.update_security_mechanisms_information(received_data_dict)

    # call function to create new combinations, weights and values for the updated security mechanism information
    context_information_database.create_security_mechanism_combinations()


def process_message_security_mechanisms_filter(received_data_dict):
    context_information_database.update_security_mechanisms_filter(received_data_dict)


def process_message_context_information(received_data_dict):
    global weight, max_weight
    db_table_name = 'received_context_information'

    try:
        if datetime.strptime(received_data_dict['elicitation_date'], time_format) > datetime.now() + timedelta(minutes=0):
            print("""[ERROR]: date from received data is greater than system time; Context data will be ignored\n""")
            return

    except:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno, """while comparing system time with received context information in""")
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

    try:
        weight, max_weight = Client.Reasoning_Engine.Context_Model.Weight_Calculation.weights.evaluate_weight(received_data_dict)
        received_data_dict['weight'] = weight
        print("calculated weight: ", weight)

    except TypeError:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """weight calculation was not possible\n further message processing not possible""")
        return

    try:
        best_option = Client.Reasoning_Engine.Context_Model.reasoning.calculate_best_combination(weight, max_weight, received_data_dict)
        print(best_option, "\n")
        received_data_dict['best_option'] = str(best_option)

    except:
        frame_info = getframeinfo(currentframe())
        print("""[ERROR]: in""", frame_info.filename, "in line:", frame_info.lineno,
              """best_option calculation was not possible\n further message processing not possible""")
        return

    # save context information with best option evaluation to the database
    context_information_database.update_context_information(received_data_dict)

    # check if the best_option tuple is not empty
    if best_option:
        # give best_option to set_security_mechanisms function in order to set the appropriated mechanisms and their modes
        Client.set_security_mechanisms.set_security_mechanisms(best_option)


class ConnectionTCPHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        print(f'Connected: {self.client_address[0]}:{self.client_address[1]}\n')
        while True:
            try:
                self.data = self.request.recv(1024).strip()
                received_time = datetime.now()
                if not self.data.decode():
                    print("----Received message was empty----")
                    print("----Waiting for new message----")
                    break
            except:
                print("----Lost connection to client----")
                print("----Waiting for reconnection----")
                break

            print(f"{self.client_address[0]} wrote at {received_time}: ")
            print(self.data.decode('utf-8'))

            if "security_mechanisms_filter" in self.data.decode():
                process_message_filter_file(self.data.decode(), self)
                continue

            if "security_mechanism_file" in self.data.decode():
                process_message_security_mechanism_file(self.data.decode(), self)
                continue

            if "weight_calculation_file" in self.data.decode():
                process_message_weight_calculation_file(self.data.decode(), self)

            # create a dict out of the received data and forward the data to designated methods to process the data for context evaluation
            try:
                received_data_dict = json.loads(self.data)

                match received_data_dict['message_type']:
                    case 'context_information':
                        process_message_context_information(received_data_dict)
                    case 'keystore_update':
                        process_message_keystore_information(received_data_dict)
                    case 'security_mechanisms_information':
                        process_message_security_mechanisms_information(received_data_dict)
                    case 'security_mechanisms_filter':
                        process_message_security_mechanisms_filter(received_data_dict)
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
