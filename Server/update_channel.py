import json
import socket
import time

import Server.context_information_keystore_update as ciku

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


def sending_context_information():
    while True:

        context_information_keystore_update_battery_consumption = ciku.ContextInformationKeystoreUpdate(
            'battery_consumption', 0, 50, 0, 1,
            '[5, 10, 15, 20, 25, 35]')
        context_information_keystore_update_battery_state = ciku.ContextInformationKeystoreUpdate('battery_state', 0, 100, 100, 3, '[20, 40, 60, 80]')

        try:
            # send message and generate json out of context information object
            sock.send(bytes(
                json.dumps(context_information_keystore_update_battery_state.__dict__),
                encoding='utf-8'))
            print(json.dumps(context_information_keystore_update_battery_state.__dict__))

            # Receive data from the server and shut down;
            # TODO implement possible server responses
            # received = str(sock.recv(1024), "utf-8")

            # adjust time to send less or more messages
            time.sleep(10)

        except:
            print(
                "Connection to server was closed during transmission")
            break


if __name__ == '__main__':
    HOST = '127.0.0.1'
    time_format = '%Y-%m-%dT%H:%M:%S.%f'
    while True:
        for port in range(64997, 65000):
            if connection_to_server(port):
                sending_context_information()
            else:
                print("Couldn't establish socket connection")
                print("Will try again after 10 sec ...")
