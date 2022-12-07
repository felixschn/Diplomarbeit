import socket
import json
from datetime import datetime
import Server.context_information_creation as cic

if __name__ == '__main__':
    HOST, PORT = "localhost", 9999
    time_format = '%Y-%m-%dT%H:%M:%S.%f'
    #data = " ".join(sys.argv[1:])
    data = 'Bergholz war hier, auch heute'
    # Create a socket (SOCK_STREAM means a TCP socket)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        #sock.sendall(bytes(data + "\n", "utf-8"))

        context_information_2 = cic.ContextInformationCreation(
            cic.ContextInformationCreation.battery_information(), cic.ContextInformationCreation.distance_generator(), cic.ContextInformationCreation.location_generator(),
            datetime.now().strftime(time_format))
        print(type(context_information_2))

        sock.sendall(bytes(json.dumps(context_information_2.__dict__), encoding = 'utf-8'))

        # Receive data from the server and shut down
        received = str(sock.recv(1024), "utf-8")

    print("Sent:     {}".format(data))
    print("Received: {}".format(received))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
