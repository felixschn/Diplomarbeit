import json
import random
import socket
import time

import Server.context_information_keystore_update as ciku
import Server.security_mechanisms_informaiton as cismi

sock = None


# created method for socket connection in order to re-establish connection if server was shutdown
# idea:https://stackoverflow.com/questions/15870614/python-recreate-a-socket-and-automatically-reconnect
def connection_to_server(port):
    global sock
    # TODO check behaviour if server is closed during connection and vice versa
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server and send data
    try:
        sock.connect((HOST, port))
        # sock.sendall(bytes(data + "\n", "utf-8"))
        print('Connection established')
        return True

    except:
        print(
            "Couldn't connect, because wrong port or IP address was used",
            port)

    return False


# creating objects which can be send over the established connection
# TODO somehow the identifier count in steps of two
context_information_keystore_update_battery_consumption = ciku.ContextInformationKeystoreUpdate(
    'battery_consumption', 0, 100, 5, 15,
    '[5, 10, 15, 20, 25, 35]')

context_information_keystore_update_battery_state = ciku.ContextInformationKeystoreUpdate('battery_state', 0, 100, 100,
                                                                                          5, '[20, 40, 60, 80]')
context_information_keystore_update_charging_station_distance = ciku.ContextInformationKeystoreUpdate(
    'charging_station_distance', 0, 500, 0, 5, '[0,100,200,300,400,500]')

context_information_security_mechanisms_information = cismi.SecurityMechanismsInformation('firewall', 3, [0,1,2])


def sending_context_information():
    while True:
        try:
            # send messages randomly and generate json objects out of various objects
            match random.randint(1, 4):
                case 1:
                    sock.send(bytes(
                        json.dumps(context_information_keystore_update_battery_consumption.__dict__),
                        encoding='utf-8'))
                    print(json.dumps(context_information_keystore_update_battery_consumption.__dict__))
                case 2:
                    sock.send(bytes(
                        json.dumps(context_information_keystore_update_battery_state.__dict__),
                        encoding='utf-8'))
                    print(json.dumps(context_information_keystore_update_battery_state.__dict__))
                case 3:
                    sock.send(bytes(
                        json.dumps(context_information_keystore_update_charging_station_distance.__dict__),
                        encoding='utf-8'))
                    print(json.dumps(context_information_keystore_update_charging_station_distance.__dict__))
                case 4:
                    sock.send(bytes(
                        json.dumps(context_information_security_mechanisms_information.__dict__), encoding='utf-8'))
                    print(json.dumps(context_information_security_mechanisms_information.__dict__))

            # adjust time to send less or more messages
            time.sleep(5)

        except:
            print(
                "Connection to server was closed during transmission")
            break


if __name__ == '__main__':
    HOST = '127.0.0.1'
    time_format = '%Y-%m-%dT%H:%M:%S.%f'
    while True:
        # simulate trivial port scan
        for port in range(64997, 65000):
            # create connection and sending information
            if connection_to_server(port):
                sending_context_information()
            else:
                print("Couldn't establish socket connection")
                print("Will try again after 10 sec ...")
