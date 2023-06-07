import json
import socketserver
from datetime import datetime, timedelta
from importlib import reload, import_module
from inspect import getframeinfo, currentframe
from pathlib import Path

import tqdm

import Client.Application_Area.Security_Mechanisms.set_security_mechanisms
from Client.Data_Engine import database_connector
from Client.Reasoning_Engine.Context_Model.Rule_Set.asset_evaluation import asset_evaluation
from Client.Reasoning_Engine.Context_Model.reasoning import calculate_best_combination

HOST = "localhost"
BUFFER_SIZE = 4096
DELIMITER = "<delimiter>"

# the range of possible port numbers must be n-1 with respect to the for loop in the function called connection to server in main.py, or else the server will
# listen to a port that has never been called from the client
PORT = 65000
time_format = '%Y-%m-%dT%H:%M:%S.%f'


def reload_retrieved_modules(filename, module_path):
    formatted_file_name = filename.replace('.py', '')
    imported_mod = import_module(f"{module_path}{formatted_file_name}")

    # note: due to a security feature of the reload function, existing functions of a module remain if they are not overwritten through an update;
    # to avoid any problems with not removed functions, the instruction files will contain only one public function
    # which has to be present and, therefore, never get deleted
    reload(imported_mod)


def process_incoming_message(received_data, connection_handler, module_storing_path, module_path) -> str:
    if len(received_data) == 0:
        raise Exception

    # store the received data in variables
    _, filename, size_of_file, file_content = received_data.split(DELIMITER)
    size_of_file = int(size_of_file)
    show_progress = tqdm.tqdm(range(size_of_file), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)

    # write the received data to a file in the respective directory
    path_to_project = Path(__file__).parents[2]
    path_to_file = path_to_project.joinpath(module_storing_path + filename)

    with open(path_to_file, "wb") as received_file:
        while True:
            read_data = connection_handler.request.recv(BUFFER_SIZE)

            if not read_data:
                break

            received_file.write(read_data)
            show_progress.update(len(read_data))

    # reloading the modules to process context information with the newest data
    reload_retrieved_modules(filename, module_path)

    return filename


def process_message_high_level_derivation_file(received_data, connection_handler):
    modul_storing_path = f"Client\Reasoning_Engine\Context_Model\Rule_Set\\"
    module_path = "Client.Reasoning_Engine.Context_Model.Rule_Set."

    try:
        filename = process_incoming_message(received_data, connection_handler, modul_storing_path, module_path)

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno, "storing received high_level_derivation_file failed")
        return

    # update the database with the received high_level_derivation file name
    database_connector.insert_high_level_derivation_files(filename)


def process_message_filter_file(received_data, connection_handler):
    modul_storing_path = f"Client\Reasoning_Engine\Filter\\"
    module_path = "Client.Reasoning_Engine.Filter."

    try:
        filename = process_incoming_message(received_data, connection_handler, modul_storing_path, module_path)

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno, "storing received filter_file failed")
        return

    # update the database with the received filter_file name
    database_connector.insert_filter_files(filename)


def process_message_security_mechanism_file(received_data, connection_handler):
    # only store new file to directory; storing file name into database is not required due to the existing (and necessary) security_mechanism_information entry
    modul_storing_path = f"Client\Application_Area\Security_Mechanisms\\"
    module_path = "Client.Application_Area.Security_Mechanisms."

    try:
        process_incoming_message(received_data, connection_handler, modul_storing_path, module_path)

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno, "storing received security mechanism file")
        return


def process_message_keystore_information(received_data_dict):
    database_connector.update_context_information_keystore(received_data_dict)


def process_message_security_mechanisms_information(received_data):
    # check if the number of mode_costs and modes is equal
    if received_data['modes'] != len(received_data['mode_costs']) or received_data['modes'] != len(received_data['mode_values']):
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno, "update message for security_mechanism_information:" \
                                                                                 "the number of modes and mode costs or mode values are not equal")
        return

    database_connector.update_security_mechanism_information(received_data)

    # call function to create new combinations, costs and values when receiving new security mechanism information
    database_connector.create_security_mechanism_combinations()


def process_message_context_information(received_context_information):
    # exemplary way to check Quality of Context by running timestamp comparison
    try:
        # reject messages with timestamp greater than system time
        if datetime.strptime(received_context_information['elicitation_date'], time_format) > datetime.now() + timedelta(minutes=0):
            print("[ERROR]: date from received data is greater than system time; Context data will be ignored\n")
            return

        # reject messages with timestamp older than last database entry
        if datetime.strptime(received_context_information['elicitation_date'], time_format) < datetime.strptime(
                database_connector.get_latest_date_entry(), time_format):
            print("Received context information is older than the latest database entry")
            print("Context data will be ignored")
            print("-----------------------------")
            return

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
              "timestamp error while comparing the latest database entry with received context information")
        return

    try:
        print("----------Evaluation Process----------")
        # asset calculation to prepare later best option choice
        calculated_asset, sum_of_max_asset = asset_evaluation(received_context_information)
        received_context_information["asset"] = calculated_asset
        print("calculated asset: ".ljust(33), calculated_asset)

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno, "asset calculation was not possible\nfurther message processing not possible")
        return

    try:
        # based on the asset calculation and cost of security mechanisms combination; the best combination is selected
        best_option = calculate_best_combination(calculated_asset, sum_of_max_asset, received_context_information)
        print("best option: ".ljust(33), best_option)

    except:
        frame_info = getframeinfo(currentframe())
        print("[ERROR]: in", frame_info.filename, "in line:", frame_info.lineno,
              "best_option calculation was not possible\n further message processing not possible")
        return

    # convert tuple values to string to save it in the database
    received_context_information["location"] = str(received_context_information["location"])
    received_context_information['best_option'] = str(best_option)
    database_connector.insert_context_information(received_context_information)

    # set security mechanism modes of best_option
    if best_option:
        Client.Application_Area.Security_Mechanisms.set_security_mechanisms.set_security_mechanisms(best_option)


class ConnectionTCPHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        print(f"\nConnected: {self.client_address[0]}:{self.client_address[1]}")

        # loop is necessary to received recurring context information messages
        while True:
            try:
                self.data = self.request.recv(1024).strip()
                received_time = datetime.now()
                if not self.data.decode():
                    break
            except:
                print("----------Lost Connection to Client----------")
                print("----------Waiting for Reconnection----------")
                break

            print("\n----------Incoming Message----------")
            print(f"{self.client_address[0]} wrote at {received_time}: ")
            print(self.data.decode('utf-8'))

            if "security_mechanisms_filter" in self.data.decode():
                process_message_filter_file(self.data.decode(), self)
                break

            if "security_mechanism_file" in self.data.decode():
                process_message_security_mechanism_file(self.data.decode(), self)
                break

            if "high_level_derivation_file" in self.data.decode():
                process_message_high_level_derivation_file(self.data.decode(), self)
                break

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
                    case _:
                        frame_info = getframeinfo(currentframe())
                        print("\n[ERROR] in", frame_info.filename, "in line", frame_info.lineno, "\nmessage type is unknown, received data will be ignored")
                        break

            except json.JSONDecodeError:
                frame_info = getframeinfo(currentframe())
                print("[ERROR] in", frame_info.filename, "in line", frame_info.lineno, "transformation of received data failed")
                break


with socketserver.ThreadingTCPServer((HOST, PORT), ConnectionTCPHandler) as server:
    # activate the socket server; this will keep running until an interrupt is sent to the program with Ctrl-C
    print("---- Waiting for connection at port", PORT, "----")
    server.serve_forever()
