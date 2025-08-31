# PyWiliot: wiliot-tools #

wiliot-tools is a python library for accessing Wiliot's Tools

## Public Library

### MAC Installation
#### Getting around SSL issue on Mac with Python 3.7 and later versions

Python version 3.7 on Mac OS has stopped using the OS's version of SSL and started using Python's implementation instead. As a result, the CA
certificates included in the OS are no longer usable. To avoid getting SSL related errors from the code when running under this setup you need
to execute Install Certificates.command Python script. Typically you will find it under
~~~~
/Applications/Python\ 3.7/Install\ Certificates.command
~~~~

#### Python 3 on Mac
The default Python version on mac is 2.x. Since Wiliot package requires Python 3.x you should download Python3 
(e.g.  Python3.7) and make python 3 your default.
There are many ways how to do it such as add python3 to your PATH (one possible solution https://www.educative.io/edpresso/how-to-add-python-to-the-path-variable-in-mac) 

#### Git is not working after Mac update
please check the following solution:
https://stackoverflow.com/questions/52522565/git-is-not-working-after-macos-update-xcrun-error-invalid-active-developer-pa


### Installing pyWiliot
````commandline
pip install wiliot-tools
````

### Using pyWiliot
Wiliot package location can be found, by typing in the command line:
````commandline
pip show wiliot-tools
````
please check out our tools, including:
* [Local Gateway GUI](wiliot_tools/local_gateway_gui/local_gateway_gui.py)

For more documentation and instructions, please contact us: support@wiliot.com


## Release Notes:

Version 4.11.1:
-----------------
* General:
	updated requirements

* Association Tools:
	* added support to run association based on user base URL on the associate_by_file script
	* for the CloudAssociation class:
		* added the option to use the user base URL
		* added the option to auto re-connect if needed
		* bugfix for re-try bad association call

* Gateway GUI:
	* added support in different baud rate based on the new Gateway firmware 4.4.8 (see wiliot-core release notes for more info)

* Sensors and Hardware:
	* added new example for network communication with Cognex scanner
	* updated the network Cognex class to use TCP/IP protocol

Version 4.10.1:
-----------------
* Association Tool
	* added support to use the initiator name when associating using the tool

* Gateway GUI:
	* add option to resolve packets from GCP and change it to thread instead of multi-process
	* added list of the received tag ids and external ids below the data when full uid mode is selected
	* bugfix to see more indication from the gateway when using gpio

* Resolver Tool
	* added support to resolve GCP
	* added support to batch resolve using thread pool

* Test equipments
	* added function to use humidity sensor
	* improve Cognex Network class and Cognex Data class
	* added option to get temperature data from several sensors

* Wiliot GUI
	* added exit function when user close the window
	* added more option to change checkbox style

Version 4.9.1:
-----------------
* Gateway GUI:
  * add output power to GW GUI
  * added option to see GW received signals from GPIO on the console.
  * added gw command description on the command info button

Version 4.8.1:
-----------------
* generic gui cleanup so all GUIs are WiliotGui class

* Gateway GUI:
  * added support to pull external ids during live testing
  * added button to show all gateway commands options
  * added button of clean data and clean console instead of general clean button
  * support symbol configuration

* New tool for Gen3 Production Manufacturing Labeling and Data Collection
* Owner change Tool:
  * added fail check for all tags that failed to change owner (internal only)

* Shipment approval api:
  * bugfixes and improvements.

* Added resolver tool to wiliot-tools package (moved from wiliot-testers package)
  * class for handling live packet resolving to external ids

* Added test equipment to wiliot-tools package (moved from wiliot-testers package)
  * list of classes to interact with different hardware


Version 4.7.5:
-----------------
* updated requirements
* added new wiliot-gui and updated all GUIs app
  
* Gateway GUI:
  * added support to change the radio frequency (symbol)
  * utilize the new gateway configuration function
  * bug fixed for rssi threshold featured


Version 4.6.3:
-----------------
* Association:
  * added a tool to associate or disassociate assets from file 
  * allow to change the time between requests for CloudAssociation class
  
* gateway gui:
  * added rssi threshold option to gui
  * added the option to filer packets based on packet flow version
  * added rssi to full uid mode.
  
* scanning ground-truth tool - new tool to send generic events when scanner scan wiliot pixels


Version 4.5.4:
-----------------
* Gateway GUI:
  * use the multi-process option when handling the GW if system allow it
  * print the GW response as well and not only the packets
  * add more options to the macro
  * add options to run and config gw separately
  
* owner change GUI:
  * added support to move tags from AWS to GCP

Version 4.4.4:
-----------------
* Added association tool to associate between tags and id for GCP and AWS platforms

* local gw gui:
  * add start/stop gw app instead of only reset option
  

Version 4.2.2:
-----------------
* Gateway GUI
  * add logger and improving data logging
  * improve UID only mode
  * added macro for Gateway firmware update
* Owner change GUI - new tool for changing owner to pixels

Version 4.1.0:
-----------------
* Gateway GUI
  * add the option to wrap it up as application
  * handle better packet parsing exceptions

Version 4.0.5:
-----------------
* Gateway GUI - Live Plots:
  * improve visualization - add sample points, clear after changing feature
  * add empty feature
  * add option to save the last configuration
* Gateway GUI - General:
  * add sample points
  * fix libraries compatibility
  * improve logging from all data type and fix bugs
  * enhance gw macros

Version 4.0.4:
-----------------
* Gateway GUI
    * add mode for printing full UID, advertising address
    * show only Silicon Lab port as options for the gw GUI
    * add button to print the macro file to create new macros.
    * update GUI visualization

Version 4.0.2:
-----------------
* First version


The package previous content was published under the name 'wiliot' package.
for more information please read 'wiliot' package's release notes
