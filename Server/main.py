import json
import socket
import time
from datetime import datetime

import Server.context_information_creation as cic


# created method for socket connection in order to re-establish connection if server was shutdown
# idea:https://stackoverflow.com/questions/15870614/python-recreate-a-socket-and-automatically-reconnect
def connection_to_server():
    global sock
    # TODO check behaviour if server is closed during connection and vice versa
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to server and send data
    for port in range(64997, 65000):
        print(port)
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
        # create context information object
        context_information_2 = cic.ContextInformationCreation(
            cic.ContextInformationCreation.battery_information(),
            cic.ContextInformationCreation.distance_generator(),
            cic.ContextInformationCreation.location_generator(),
            datetime.now().strftime(time_format))
        print(context_information_2)

        try:
            # send message and generate json out of
            # context information object
            sock.send(bytes(
                json.dumps(context_information_2.__dict__),
                encoding='utf-8'))

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
        if connection_to_server():
            sending_context_information()
        else:
            print("Couldn't establish socket connection")
            print("Will try again after 10 sec ...")
            time.sleep(10)
