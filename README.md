# Implementation of a Context-Aware and Adaptive Vehicle Security System

This implementaion concludes the research to the Diploma Thesis "Context-Awareness for Adaptive Security in Vehicles"

## About this Project

To address the Research Problem given in the Diploma Thesis, the given implementaion aims to prove a designed concept to adapt the security mechanisms of vehicles concerning the contextual evaluation of data, respetively, information. The implementation is a small-scale system that is able to send context information and new instructions in the form of Python source code or JSON packets via a Python socket connection to the [Client](../felixschn/Diplomarbeit/Client) structure using the [Server](../felixschn/Diplomarbeit/Server) structure. The client represents a fictitious smart vehicle that can select and execute suitable combinations of security mechanisms based on a context evaluation. To demonstrate the functionality, a simulation is created with the SUMO tool.

## Requierements

### Python

In order to execute the implementation the [Python 3.10](https://www.python.org/downloads/release/python-31012/) (or) higher interpreter is required


Additional requiered packages:


+ colorama==0.4.6
+ sumolib==1.16.0
+ tqdm==4.64.1
+ traci==1.16.0

### SUMO

For demonstration purposes the [Server](../felixschn/Diplomarbeit/Server) structure of the system uses the TraCi API of the Sumo Simulation tool that needs to be installed in order to send context information.


SUMO is an open source tool and can be downloaded here: [SUMO Installation](https://sumo.dlr.de/docs/Downloads.php)



## Running the System

Normally, the system should start without complications when all [Requirements](#requierements) are installed. However, should the dynamically path declarations not work, you can edit them directly in the affected files. For other issues, see the console output. 
In order to run the system, the Client can be activated by executing the Python file [network_class](../felixschn/Diplomarbeit/Client/Application_Area/network_class.py) in the Client's [Application_Area](../felixschn/Diplomarbeit/Client/Application_Area) directory. Once the Client is activated, it will wait for incoming messages that can be triggered in various ways:


### Adding Necessary Files and Instructions

One of the two core functionalities of this systems is to send new Python files or instructions during runtime. Although the Client already covers the mandatory requierements for a basic context evaluation, it depends on the database entries as well as the already existing files at the [Client](../felixschn/Diplomarbeit/Client) how sophisticated the context evaluation will be.

#### Adding New Keystore Entries

For extending the Context Model and incorporating new context information for the evaluation process, the [send_keystore_information.py](../felixschn/Diplomarbeit/Server/Messages/send_keystore_information.py) can be executed. To send new Keystore parameters, you can alter line 33, which creates the KeystoreUpdate object, to suit your needs. Note that the Client needs to be executed to receive and process the message. Now the Context Model includes the context information when the simulation sends the designated values in its evaluation

#### Adding Filter Files

Filter files can be added by transmitting a Python file from the [Instruction_Files/Filter](../felixschn/Diplomarbeit/Server/Instruction_Files/Filter) directory by executing [send_filter_files.py](../felixschn/Diplomarbeit/Server/Messages/send_filter_files.py) and modifying the path declaration to the desired file.

#### Adding High-Level Derivation Files

High-level derivation files can be added by transmitting a Python file from the [Instruction_Files/High_Level_Derivation_Files](../felixschn/Diplomarbeit/Server/Instruction_Files/High_Level_Derivation_Files) directory by executing [send_filter_files.py](../felixschn/Diplomarbeit/Server/Messages/send_filter_files.py) and modifying the path declaration to the desired file.

#### Adding Security Mechanisms

For sending new Security Mechanisms to the Client, a new Python file and instructions need to be send:

1. The Context Model requires the in the Diploma Thesis mentioned security mechanism information, such as the name, modes, costs and values. This can be achived by executing the [send_security_mechanism_information.py](../felixschn/Diplomarbeit/Server/Messages/send_security_mechanism_information.py) file. Note you can customise the informatoin to your needs by altering the SecurityMechanismInformation object in line 31.
2. In addition to security mechanism information, the Client expects a Python file containing instructions on what to execute when one of the modes is executed following the evaluation. Security mechanism files can be added by transmitting a Python file from the [Instruction_Files/Security_Mechanism](../felixschn/Diplomarbeit/Server/Instruction_Files/Security_Mechanism) directory by executing [send_security_mechanism_file.py](../felixschn/Diplomarbeit/Server/Messages/send_security_mechanism_file.py) and modifying the path declaration to the desired file.


### Start the Simulation and Send Context Information

The second core functionality is the execution of the SUMO scenario created for this Diploma Thesis. The necessary files to start the simulation are already in the [Simulation/Sumo_Configuration](../felixschn/Diplomarbeit/Server/Simulation/Sumo_Configuration) directory. When correctly installed, SUMO will start the scenario by executing the [run_sumo.py](../felixschn/Diplomarbeit/Simulation/run_sumo.py). 

With each simulation step, the Server sends a package of context information to the Client. In the Python console of the Client, the evaluation process will print important evaluation steps, the result of the evaluation, and the started security mechanism modes
