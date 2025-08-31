# PyWiliot: wiliot-core #

wiliot-core is a python library for accessing Wiliot's core functions such as communicating with
Wiliot's local gateway and working on the packets data

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
pip install wiliot-core
````

### Using pyWiliot
Wiliot package location can be found, by typing in the command line:
````commandline
pip show wiliot-core
````
please check out our examples, including:
* [gateway communication](wiliot_core/local_gateway/examples)
* [packet data](wiliot_core/packet_data) (at the end of each script)

For more documentation and instructions, please contact us: support@wiliot.com


## Release Notes:
Version 5.11.1:
----------------
* Management:
  * updated requirements

* Packet Data:
  * Added inlay 179
  * Added bugfix for sprinkler calculation parameters (e.g. tbp, per) for packets with bad crc

* Gateway core
	* added the new gateway firmware
  * updated command description for gateway_app and new commands based on the new firmware
  * improve exit app to handle failure in stop process

*  Gateway Firmware 4.4.9:
  * Added command to initialize gateway timestamp: !init_gw_timestamp <MODE>
  * for instance, mode 2 = (EVERY_APP_START) elapse timer every time gateway radio application is invoked
  * Added support for setting different Baud Rate in FW using !set_uart_baudrate <BAUDRATE>
  * Added bugfix for '!enable_hw_dual_band' to return gateway acknowledgment


Version 5.10.1:
-----------------
* General: 
	* update requirements
	* fix the get api key pop up get stuck if running when wiliotGUI is running as well

* packet data:
	*  added support to pointer packets
	* fixed statistics calculation when calculating the number of cycles
	* added inlay 170
	* added flow version 0x800 to packet version 3.3
	* index the packet using the payloads and not the raw packet when using packet list, this means that packets with bad crc that their payload was not affected, can be “fixed” if another sprinkler was received.
	* added option to import the timestamp from file when using wiliot-core to parse it

* Gateway core
	* added the option to disable reset time from start when using reset command and so on
	* improve is_gw_alive function and add delay before check gw response
	* when selecting symbol as 2Mhz, also the preamble length is changed to 16
	* fix function get_time_of_controlled_start_app to sync data between two gateways

Version 5.9.1:
-----------------
* packet data core:
	* PacketList.get_generic_df_col() - get all attributes names and types generated from the PacketList.get_df()
	* PacketList.get_df() - change the default value of add_sprinkler_info (tbp and per) to True
	* PacketList.import_packet_df() - improve performance for when specified import_all=True for adding all others columns to the packet list custom_data

* Gateway core
	* Added gateway command description.
	* added improvement for GW signals handling (inputs from its GPIO), by using WiliotGateway.get_gw_signals() instead of WiliotGateway.get_gw_responses()
	* Fixed hex file for gateway version 4.4.0
	* Added new Gateway Firmware version 4.4.3

* Gateway Firmware 4.4.3
  * add verification for the sub1z energy mode in the print_config_extended (pce) command
  * added new GW command: !set_sub_1_ghz_starting_point set the Gateway sub1g time sync w.r.t the 2.4 transmission. mode 0 = starts with the first beacon [default], 1 = starts after completing beacons in 2.4 transmission. default 0, e.g. 1
  * improve GW RX UART to handle high rate of received messages (such as gw configurations)

Version 5.8.3:
-----------------
* added support to python version 3.12
* gateway_core:
  * added support to import export gateway configuration using set_configuration function
  * added support ot run gateway listener process as multi-process for MACOS
  * get gateway signals, GPIO input, in a more robust way
  * support 2mhz-nrf mode for radio scanner
  * gateway firmware - new version was added

* Gateway Firmware 4.4.0:
  * clean set_rssi_config commands and set the status return of reset and bootloader false
  * filter out brg-to-brg packets
  * added sub1g energy modes - for FCC hopping:
    * the new GW command: !set_sub_1_ghz_energizing_mode <SUB1G_ENERGY_MODE>
      * 0 → SUB1G_ENERGY_CONSTANT, default value based on the sub1g freq.
      * 1 → SUB1G_ENERGY_FCC_HOPPING, energize on different frequency every cycle based on the following method - starts from 905Mhz till 920 Mhz with 300 Khz intervals
  * fix memory leakage
  
* packet data:
  * added first transmitted packet indication to packet structure
  * added a function to retrieve all packets statistics output and column type for database handling
  * added parsing of bridge packet
  * fixed tbp bug for tag gen2 when 3 packets received


Version 5.7.4:
-----------------
* update wiliot gui
  
* gateway_core:
  * add the option to configure only the gw without getting packets from it for a nest gateways setup
  * improved identification of ACK from gateway.
  * added function to get the output power command based on the absolute power
  * added function to get the symbol configuration.
  * bug fixes for the new gateway configuration function set_configuration()
  * Added function to set a gw to be the controller or controlled by other gateway for a nest gateways setup
  * Added a list of all available energy patterns
  * updated the list of all available commands
  * Added a list of all available output power
  
* packet data:
  * improved support and bug fix for cloud payload to raw packet conversion.
  * Added flow version and asset id to statistics outputs.
  * Added function to PacketList to convert .log file to Wiliot packets structure
  

Version 5.6.10:
-----------------
* update requirements
  
* gateway core:
  * added all option for gw commands based on the latest firmware
  * improve write and read function for more robust serial communication with the gateway
  * added new configuration function to configure the gateway
  * added logger to data based on get_packets function input
  * added new gateway firmware version
  
* packets data core:
  * added full support for data extract from cloud database, including supports of packet from bridge and enrich packets table
  * added mapping to gw packet to allow reconstructing gw packet from a specified data
  * added the option to ignore data with bad crc and calculate the analysis and statistics without it
  * added inlay 160, 168, 169
  * added the option to get dataframe of the only n last packets in packet list
  * improve get_avg_rssi function
  * added the option to import dataframe or csv to any pywiliot packet object available
  * added the option for adi per packet even if packet from the same sprinkler
  * added logging to TagCollection
  * added the option to run statistics on specified dataframe and not only the object dataframe
  
* utils:
  * added more options to set_logger function and reduce the must fields to specified
  * added gui based on ttk to retrieve api key from user


Version 5.5.8:
-----------------
* update requirements
* gateway core:
  * add support to listen to two or more gw and merge data
  * support auto time reset based on GW msg
  * added support to connect to gw based on its name/uid
  * added wrapper to get all gw responses similar to get packets
  * added function of reconnect
  * added function to control output signal (GPIO) from the GW
  * added new firmware version
* packets data core:
  * support packets from cloud (payload)
  * added new packet fields - gw clock, crc, adi (relevant to ble5 only) - effective only for the new firmware version
  * add function to manipulate packets
  
Version 5.4.3:
-----------------
* gateway core:
  * Added new firmware version to local gateway
  * added the option to restart the gateway time based on command and control the log for buffer overload
* packets data core:
  * Support Gen3 wiliot tags - tbp, per calculation
  * fix bug for parsing ADI for BLE5 packets and parsing packets from bridge
  * bug fixed in packet list, filter packets function
* improve examples

Version 5.0.4:
-----------------
* Added new mechanism to parse packet for supporting BLE5 protocol
* Improved support to Linux OS
* Improved recovery flow for multi-process GW communication
* Added more packet types to get_packet from GW
* Added a return indication if GW app stopped
* GW's configuration parameters validity check was removed
* Added new GW FW 4.1.3
* Added logging mechanism to all packet’s classes
* Improved support to packets from bridge including option to set the packet version by the user
* improved performance of get dataframe from packet list
* Fixed bug in tag collection concat function

Version 4.1.0:
-----------------
* add new version for GW FW
* improve socket connection for tcp/ip communication with GW
* improve get df for tag collection class

Version 4.0.13:
-----------------
* improve visualization of GW FW version updates.
* add new version for GW FW

Version 4.0.9:
-----------------
* improve Wiliot Dir
* add support to multiple api keys for the same owner id and environment bud different clients
  
Version 4.0.8:
-----------------
* continuous listener as multi-processes:
    * add option to specify log path and communicate reading error using event
    * connect to gw in a more robust way including printing exceptions if needed
* local gw core:
    * connect only to “Silicon Lab”/"CP210.." ports (Wiliot's gw driver)
    * added a function to check gw response using version command check_gw_responds including is_gw_alive function
    * better handling ACK msg from the GW
    * get reading status function get_read_error_status. 
    * better stop gw app including writing a log if no ACK was received for the cancel command
    * add new GW FW version
* packet:
    * add new function to packet to retrieve basic data: get_adva, get_flow, get_rssi


Version 4.0.6:
-----------------
* First version


The package previous content was published under the name 'wiliot' package.
for more information please read 'wiliot' package's release notes
  
  
   



