import socket

import Server.Simulation.sumo_simulation as sumo_simulation


def connection_to_server(message_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 65000
    host = '127.0.0.1'

    # Connect to Client
    try:
        sock.connect((host, port))
        print('Connection established')
        return sock

    except:
        print(f"{message_name}: Couldn't connect, because wrong port or IP address was used", port)

    return


if __name__ == '__main__':
    # execute SUMO simulation
    sumo_simulation.simulation_data(connection_to_server("context_information"))
