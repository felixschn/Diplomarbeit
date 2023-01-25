import socket
import threading
import time

import Server.Messages.message_context_information as message_context_information
import Server.Messages.message_keystore_information as message_keystore_information
import Server.Messages.message_security_mechanism_information as message_security_mechanisms_information
import Server.Messages.message_filter_file as message_filter_file

sock = None


# created method for socket connection in order to re-establish connection if server was shutdown
# idea:https://stackoverflow.com/questions/15870614/python-recreate-a-socket-and-automatically-reconnect
def connection_to_server():
    # TODO check behaviour if server is closed during connection and vice versa
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to server and send data

    for port in range(64997, 65000):
        try:

            sock.connect((HOST, port))
            # sock.sendall(bytes(data + "\n", "utf-8"))
            print('Connection established')
            return sock

        except:
            print(
                "Couldn't connect, because wrong port or IP address was used",
                port)

    return


if __name__ == '__main__':
    HOST = '127.0.0.1'
    time_format = '%Y-%m-%dT%H:%M:%S.%f'

    #thread_security_mechanisms_information = threading.Thread(target=message_security_mechanisms_information.send_security_mechanisms_information,
                                                              #args=(connection_to_server(),))
    #thread_security_mechanisms_information.start()

    thread_context_information = threading.Thread(target=message_context_information.send_context_information, args=(connection_to_server(),))
    thread_context_information.start()

    thread_keystore_information = threading.Thread(target=message_keystore_information.send_keystore_update, args=(connection_to_server(),))
    thread_keystore_information.start()

    thread_security_mechanisms_information = threading.Thread(target=message_security_mechanisms_information.send_security_mechanisms_information, args=(connection_to_server(),))
    thread_security_mechanisms_information.start()

    thread_filter_file = threading.Thread(target=message_filter_file.send_filter_file, args=(connection_to_server(),))
    thread_filter_file.start()

    print(threading.active_count())
    print(threading.enumerate())
    print(time.perf_counter())

    while True:
        pass
