import socket

import Server.Simulation.run_sumo as run_sumo

HOST = "127.0.0.1"
PORT = 65000


def connection_to_server(message_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connect to the Client
    try:
        sock.connect((HOST, PORT))
        print('Connection established:')
        return sock

    except:
        print(f"{message_name}: couldn't connect because the wrong port or IP address was used")

    return


if __name__ == '__main__':
    sock = connection_to_server("context_information")
    run_sumo.simulation_data(sock)
