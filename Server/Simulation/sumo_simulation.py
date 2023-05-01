import collections
import json
import os
import sys
from datetime import datetime

import traci

battery_consumption_buffer = collections.deque(maxlen=100)


def simulation_data(sock):
    print("Thread 6")
    if "SUMO_HOME" in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)

    else:
        sys.exit("please declare environment variable SUMO HOME")

    sumoBinary = r"C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui.exe"
    sumoCmd = [sumoBinary, "-c", r"C:\Users\felix\Sumo\diplomarbeit_simulation\osm.sumocfg"]

    traci.start(sumoCmd)
    while True:
        traci.simulationStep()

        # check if the vehicle "main_trip" reached its destination and close the simulation
        if "main_trip" not in traci.vehicle.getLoadedIDList():
            traci.close()
            return

        traci.vehicle.setColor("main_trip", (0, 255, 255))

        # retrieve current position and long and lat of the simulated vehicle
        vehicle_position_x, vehicle_position_y = traci.vehicle.getPosition("main_trip")
        long, lat = traci.simulation.convertGeo(vehicle_position_x, vehicle_position_y)

        # retrieve driven distance and remaining trip distance
        # TODO Ask Sebastian how to deal with additional meters on the last edge
        driven_distance = traci.vehicle.getDistance("main_trip")
        trip_distance = traci.vehicle.getDrivingDistance("main_trip", "-5115636#7", traci.vehicle.getLanePosition("main_trip"))
        trip_distance -= traci.vehicle.getLanePosition("main_trip")
        if trip_distance < 0:
            trip_distance = 0.0001

        # retrieve name and distance to potential followers
        following_car_distance = traci.vehicle.getFollower("main_trip")

        # retrieve waiting time of simulated vehicle
        accumulated_waiting_time = float(traci.vehicle.getAccumulatedWaitingTime("main_trip"))

        # retrieve battery properties of simulated car
        battery_state = float(traci.vehicle.getParameter("main_trip", "device.battery.actualBatteryCapacity"))
        battery_consumption = float(traci.vehicle.getParameter("main_trip", "device.battery.energyConsumed"))
        battery_consumption_buffer.append(battery_consumption)
        total_energy_consumption = float(traci.vehicle.getParameter("main_trip", "device.battery.totalEnergyConsumed"))
        battery_maximum_capacity = float(traci.vehicle.getParameter("main_trip", "device.battery.maximumBatteryCapacity"))
        battery_state_percentage = battery_state / battery_maximum_capacity

        # calculate average battery consumption if buffer is at least filled with 10 battery consumption values; else define average as 1
        if len(battery_consumption_buffer) < 10:
            battery_consumption_average = 1
        else:
            battery_consumption_average = sum(battery_consumption_buffer) / len(battery_consumption_buffer)

        if battery_consumption_average < 0:
            battery_consumption_average = 0

        print("----------------------------\nDistance: ", traci.vehicle.getDistance("main_trip"))
        print("Distance_To_Target : ", traci.vehicle.getDrivingDistance("main_trip", "-5115636#7", traci.vehicle.getLanePosition("main_trip")))
        print("Accumulated Waiting Time: ", traci.vehicle.getAccumulatedWaitingTime("main_trip"))
        print("Following Car: ", traci.vehicle.getFollower("main_trip"))
        print("Battery Capacity: ", traci.vehicle.getParameter("main_trip", "device.battery.actualBatteryCapacity"))
        print("Energy_Consumption: ", traci.vehicle.getParameter("main_trip", "device.battery.energyConsumed"))
        print("TotalEnergy_Consumed: ", traci.vehicle.getParameter("main_trip", "device.battery.totalEnergyConsumed"))
        print("Energy_Charged: ", traci.vehicle.getParameter("main_trip", "device.battery.energyCharged"))
        print("Electricity_Consumption: ", traci.vehicle.getElectricityConsumption("main_trip"))
        print("vehicle position: ", long, lat)

        # traci.vehicle.setParameter("main_trip", "device.battery.actualBatteryCapacity", 500)
        # print("Battery Capacity: ", traci.vehicle.getParameter("main_trip", "device.battery.actualBatteryCapacity"))

        if sock:
            time_format = '%Y-%m-%dT%H:%M:%S.%f'
            context_information = {'battery_state': battery_state_percentage, 'battery_consumption': battery_consumption_average,
                                   'trip_distance': trip_distance / 1000,
                                   'location': (lat,long), 'follower': following_car_distance[1], 'elicitation_date': datetime.now().strftime(time_format), 'message_type': 'context_information'}
            sock.send(bytes(json.dumps(context_information), encoding='utf-8'))
            print(json.dumps(context_information))



        else:
            print("Couldn't establish socket connection for context information message")
            print("Will try again after 10 sec ...\n")
