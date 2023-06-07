import collections
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import traci

battery_consumption_buffer = collections.deque(maxlen=100)
time_format = '%Y-%m-%dT%H:%M:%S.%f'

path_to_project = Path(__file__).parents[2]
path_to_sumo_conf = path_to_project.joinpath("Server\\Simulation\\Sumo_Configuration\\osm.sumocfg")


def simulation_data(sock):
    if "SUMO_HOME" in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)

    else:
        sys.exit("please declare environment variable Sumo_Configuration HOME")

    sumo_binary = os.path.join(os.environ["SUMO_HOME"], "bin", "sumo-gui.exe")
    sumo_cmd = [sumo_binary, "-c", path_to_sumo_conf]

    traci.start(sumo_cmd)
    traci.vehicle.setColor("main_vehicle", (0, 255, 255))

    while True:
        traci.simulationStep()

        # check if the vehicle "main_vehicle" reached its destination and close the simulation
        if "main_vehicle" not in traci.vehicle.getLoadedIDList():
            traci.close()
            return

        # retrieve current longitude and latitude of the simulated vehicle
        vehicle_position_x, vehicle_position_y = traci.vehicle.getPosition("main_vehicle")
        long, lat = traci.simulation.convertGeo(vehicle_position_x, vehicle_position_y)

        # retrieve the remaining trip distance *to* the last edge (remaining length of last edge is neglected by getDrivingDistance function)
        trip_distance = traci.vehicle.getDrivingDistance("main_vehicle", "-5115636#7", traci.vehicle.getLanePosition("main_vehicle"))
        trip_distance -= traci.vehicle.getLanePosition("main_vehicle")
        # avoiding division with zero
        if trip_distance <= 0:
            trip_distance = 0.0001

        # retrieve the name of and the distance to potential followers
        following_car_distance = traci.vehicle.getFollower("main_vehicle")

        # retrieve battery properties of the simulated vehicle
        battery_state = float(traci.vehicle.getParameter("main_vehicle", "device.battery.actualBatteryCapacity"))
        battery_consumption = float(traci.vehicle.getParameter("main_vehicle", "device.battery.energyConsumed"))
        battery_consumption_buffer.append(battery_consumption)
        battery_maximum_capacity = float(traci.vehicle.getParameter("main_vehicle", "device.battery.maximumBatteryCapacity"))
        battery_state_percentage = battery_state / battery_maximum_capacity

        # calculate average battery consumption if the ring buffer is at least filled with 10 battery consumption values; else define average as 1
        if len(battery_consumption_buffer) < 10:
            battery_consumption_average = 1
        else:
            battery_consumption_average = sum(battery_consumption_buffer) / len(battery_consumption_buffer)

        # avoiding negative average battery consumption values due to possible recuperation of the simulated vehicle
        if battery_consumption_average < 0:
            battery_consumption_average = 0

        # print statements for potential debugging
        print("\n----------New Simulation Step----------")
        print("Distance: ".ljust(30), traci.vehicle.getDistance("main_vehicle"))
        print("Distance_To_Target: ".ljust(30), trip_distance)
        print("Accumulated_Waiting_Time: ".ljust(30), traci.vehicle.getAccumulatedWaitingTime("main_vehicle"))
        print("Battery_Capacity: ".ljust(30), traci.vehicle.getParameter("main_vehicle", "device.battery.actualBatteryCapacity"))
        print("Energy_Consumption: ".ljust(30), traci.vehicle.getParameter("main_vehicle", "device.battery.energyConsumed"))
        print("TotalEnergy_Consumed: ".ljust(30), traci.vehicle.getParameter("main_vehicle", "device.battery.totalEnergyConsumed"))
        print("Energy_Charged: ".ljust(30), traci.vehicle.getParameter("main_vehicle", "device.battery.energyCharged"))
        print("Electricity_Consumption: ".ljust(30), traci.vehicle.getElectricityConsumption("main_vehicle"))
        print("Vehicle_Position (long, lat): ".ljust(30), long, lat)
        print("Following_Car: ".ljust(30), traci.vehicle.getFollower("main_vehicle"))

        # sending the retrieved vehicle values
        if sock:
            context_information = {'battery_state': battery_state_percentage, 'battery_consumption': battery_consumption_average,
                                   'trip_distance': trip_distance / 1000,
                                   'location': (lat, long), 'follower': following_car_distance[1], 'elicitation_date': datetime.now().strftime(time_format),
                                   'message_type': 'context_information'}
            sock.send(bytes(json.dumps(context_information), encoding='utf-8'))
            print("\nSending: ", json.dumps(context_information))

        else:
            print("\n[Error]: Couldn't establish socket connection for context information message")
