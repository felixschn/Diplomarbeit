import json
import os
import sys
from datetime import datetime

import traci


def simulation_data(sock):
    if "SUMO_HOME" in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)

    else:
        sys.exit("please declare environment variable SUMO HOME")

    sumoBinary = r"C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui.exe"
    sumoCmd = [sumoBinary, "-c", r"C:\Users\felix\Sumo\2023-04-01-09-51-10\osm.sumocfg"]

    traci.start(sumoCmd)
    step = 0
    while True:
        traci.simulationStep()

        # check if the vehicle "main_trip" reached its destination and close the simulation
        if "main_trip" not in traci.vehicle.getLoadedIDList():
            traci.close()
            return


        traci.vehicle.setColor("main_trip", (0, 255, 255))
        driven_distance = traci.vehicle.getDistance("main_trip")
        charging_station_distance = traci.vehicle.getDrivingDistance("main_trip", "-5115636#7", traci.vehicle.getLanePosition("main_trip"))
        following_car_distance = traci.vehicle.getFollower("main_trip")
        accumulated_waiting_time = traci.vehicle.getAccumulatedWaitingTime("main_trip")
        battery_state = traci.vehicle.getParameter("main_trip", "device.battery.actualBatteryCapacity")
        battery_consumption = traci.vehicle.getParameter("main_trip", "device.battery.energyConsumed")
        total_energy_consumption = traci.vehicle.getParameter("main_trip", "device.battery.totalEnergyConsumed")

        print("----------------------------\nDistance: ", traci.vehicle.getDistance("main_trip"))
        print("Distance_To_Target : ", traci.vehicle.getDrivingDistance("main_trip", "-5115636#7", traci.vehicle.getLanePosition("main_trip")))
        print("Accumulated Waiting Time: ", traci.vehicle.getAccumulatedWaitingTime("main_trip"))
        print("Following Car: ", traci.vehicle.getFollower("main_trip"))
        print("Battery Capacity: ", traci.vehicle.getParameter("main_trip", "device.battery.actualBatteryCapacity"))
        print("Energy_Consumption: ", traci.vehicle.getParameter("main_trip", "device.battery.energyConsumed"))
        print("TotalEnergy_Consumed: ", traci.vehicle.getParameter("main_trip", "device.battery.totalEnergyConsumed"))
        print("Energy_Charged: ", traci.vehicle.getParameter("main_trip", "device.battery.energyCharged"))
        print("Electricity_Consumption: ", traci.vehicle.getElectricityConsumption("main_trip"))

        #traci.vehicle.setParameter("main_trip", "device.battery.actualBatteryCapacity", 500)
        #print("Battery Capacity: ", traci.vehicle.getParameter("main_trip", "device.battery.actualBatteryCapacity"))

        traci.vehicle.getRoute("main_trip")

        if sock:
            time_format = '%Y-%m-%dT%H:%M:%S.%f'
            context_information = {'battery_state': battery_state, 'battery_consumption': battery_consumption, 'charging_station_distance': charging_station_distance, 'location': 125, 'elicitation_date': datetime.now().strftime(time_format), 'message_type': 'context_information'}
            sock.send(bytes(json.dumps(context_information), encoding='utf-8'))
            print(json.dumps(context_information))



        else:
            print("Couldn't establish socket connection for context information message")
            print("Will try again after 10 sec ...\n")
