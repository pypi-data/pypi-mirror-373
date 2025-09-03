# PyWiliot: wiliot-testers #

wiliot-testers is a python library for accessing Wiliot's Testers scripts

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
pip install wiliot-testers
````

### Using pyWiliot
Wiliot package location can be found, by typing in the command line:
````commandline
pip show wiliot-testers
````
please check out our scriptd, including:
* [Offline Tester](wiliot_testers/offline/offline_tester.py)
* [Sample Test](wiliot_testers/sample/sample_test.py)
* [Yield Tester](wiliot_testers/yield_tester/assembly_yield_tester.py)
* [Association and Verification Tester](wiliot_testers/association_tester/association_and_verification_tester.py)

For more documentation and instructions, please contact us: support@wiliot.com


## Release Notes:

Version 5.11.1:
-----------------
* General:
    * deprecate the sample chamber script

* Wiliot Tester:
    * Added support to use the sensors fields same as all other fields, e.g. as quality param and mixed with other field types such as num_packets
    * added support to packet version 3.5 for sensors statistics

* Offline Tester
	* Changed preprint mode behavior:
    	* Reel name (batch name) must be 4 upper case alphabetic chars.
    	* Conversion label must be provided by operator.
    	* Reel id can change once in a run, but the new reel id must be ordered (ascending or descending) with no gaps.
        * Added Get Reel ID Application For Material Preprint
    * Added indication when internet/internet cable disconnected during light/humidity sensor
    * Updated light tags default test suite
    * updated "PRINTER_90_DEG_WAIT_TIME" parameter

* SMU Sweeper:
    * Improve UX appearance and infrastructure
    * Added support for CSV and html reports generation
    * Added more technical capabilities and reference results


Version 5.10.3:
-----------------
* Association Tester
	* added new slim tester for continuous scanning including association using CLI
* Failure Analysis Tester (SMU Sweep)
	* UI improvements
	* Added an option to run only specific tests by key (e.g. VDD_CAP, LORA, etc)

* Offline Tester: 
	* added new tests suites for light and humidity sensors tag testing
	* added indication about the tag sensor type
* Wiliot Tag Test: 
	* use reconnection function on the reset_and_config function
* Assembly Tester:
	* update default parameters for indication during the application graphs
	* improve visualization upon application completion

Version 5.9.1:
-----------------
* General
	* update requirements

* offline tester
	* added Gateway Error cases including an instruction for Gateway Error
	* try to get the printer status when no PRC is received
	* added option to define the start counter of the r2r object
	* added the option to have a default owner id to use
	* stop the run if the environmental sensors are disconnected during run
	* bugfix for machine got stuck sometimes when user click on the stop button

* Sample test:
	* added the option to run using test suites such as in offline tester
	* added surface to Gen3 tags
	* added option to control the attenuation during sub-tests

* Assembly/Conversion Tester:
	* New architecture to enhance performance
	* Improved GUI and data handling

* Association and Verification Tester
	* improve GUI
	* added support to connect with additional hardware like printer and verification scanner
	* added support to run without RF testing
	* added support to run it on offline tester machine

* Upload Testers Data:
	* bugfix when uploading big files (>15Mb) with fail bin END_OF_TEST

* Wiliot Tester:
	* improve wiliot_tester_example.py
	* Cleanup the timers usage for better performance

Version 5.8.1:
-----------------
* offline tester
	* Added duplication handling by checking the external id of the tag using resolve api to determine if duplication has occurred.
	* fix bugs on bi-directional printing support
	* Update tests suite and defaults values for first time launch
	* bugfix for the first printing counter for application crash.
	* bugfix when tag was considered a missing label but pass RF test is considered as pass and the number of missing label is decreased.
    * added production configuration option to distinguish between pixels run and labels runs
* yield-tester:
	* bugfix for first GUI Matrix tags: label
	* Add owner id to upload to cloud window
	* Add external id data to log lines.
	* Remove light sensor from GUI, CSV and LOG for conversion yield tester.
	* Cleaning & Improve data handling.
	* bugfix for getting stuck when filling API key for the first time.
	* Remove Arduino from yield tester.
	* Correct tester type in run data.
* test suite generator:
	* added the option to add float numbers to test suite

Version 5.7.8:
-----------------
* hotfix for offline-tester when missing label do respond

Version 5.7.1:
-----------------
* added support for python 3.12
* updated GUIs inlay
* move test+equipwmwnt and sensors_and_hardware files to wiliot-tools package
* added script to convert gateway gui output to offlines logs to enable data uploading and post-process results

* Tester  SDK:
    * added the option to send gw commands for the entire test
    * added the option to get the gw signals responses based on gpio interface
    * bug fix when power is not specified on the specified test suite
    * added support to tag trasnmitting with zero advertising address

* Offline Testers:
    * cleanup and improvements
    * Added tag reel location on the main gui
    * bug fix for enabling ignore-stop-criteri option
    * bug fix for bad crc counter on NO-RESPONSES locations
    * added support for extract new reel id for SGTIN, for GEN3 tags
    * added pop up message if batch name was invalid
    * added support for bi-directional printing
    * printing offset alue convestion was changed
    * added the conversation label code to the offline for gen3 tags
    * added environement setup script for first installations and release update


* Sample Test:
    * added stop citeria for number of packet and/or number of unique per tag

* Yield Tester:
    * added converastion tester - to run during conversation process
    * change name to assembly tester - for running during assembly
    * added inlay data engineering file
    * bug fix for ttfp calculation per matrix
    * added feature for resolve live packet to get the tag external id and calculate yield based on that.
    * update logs and columns names

* Test Suite Editor:
    * added all optional gw commands
    * added all optional stop criteria and quality parameters

Version 5.6.13:
-----------------
* bugfix for offline tester to detect successive missing labels.

Version 5.6.7:
-----------------
* updated requirements
* added new wiliot-gui and updated all GUIs app

* Tester SDK:
  * added support of working with multiple testers board (nested gateways setup)
  * using the new gateway configuration function.
  * added support to test shorter than 1 sec
  
* offline:
  * add the option to start from any tag run location (engineering)
  * add more time for printer to print new tags
  * improve multiple offline run code including add time between runs and allow repeating for several cycles
  * Added analysis log file to receive the time performance of an offline run.
  * fixed bug for missing label logging.
  * fixed bug for logging a case of re-scanning failed tag.
  * print on the error screen the expected and scanned external id.
  * added the option to enable/disable flash on the scanner
  * added a new reel name structure for Gen3
  
* sample Tester:
  * using the new gateway configuration function
  * added support symbol configuration
  * added support to stop run only after n tbp samples
  
* Yield Tester:
  * using the new gateway configuration function
  * improve plots and UI for advanced setting
  * restrict wafer lot and wafer number user input
  
  

Version 5.5.8:
-----------------
* tester SDK:
  * added a gui to generate new and modify existing test suite
  * added support to extract the estimating environment noise of the tag testing

* Association and Verification Tester: added new tester for verify and association wiliot pixel based on a label on label method
    
* Offline Tester:
    * added to log the environment noise based on the bad crc packet.
    * added support to scan tags without print on them based on a file from the user
    * added support to test a smaller amount of tags that the offset between the validation station to the test station
    * added tag gen indication in the gui, including verify user selection based on the tag packets
    * added feature to stop the run on specific tag based on specific stop criteria
    * fix bug when test printing format for printing calibration
    * support new cloud api for retrieving gen3 tags reel id
  
* Sample Test:
  * fix bug when new api key need to be inserted by the user
  * fix bug when run resolve on specific api key
  
* Yield Tester:
  * added support to gen3 tags
  * added back the support in arduino label counter
  * improve timestamp logging.
  * added support in pause-continue test feature
  * fix bug in upload date logging

* Equipment:
  * improve sdk for Cognex scanner 

Version 5.4.13:
-----------------
    
* tester SDK:
    * raise exception if bad gateway configuration occurs
    * even if test stopped by the user, first update and analyze results and then exit the test
    * if fail bin was set outside the test, all functions should be updated accordingly
    
* sensors and hardware:
    * improve light sensor calibration
    * added a script to configure attenuator
    * added beacons power calibration for chambers
    
* test equipment:
    * improve chamber handling
    * add more options to work with Cognex scanner
    
* offline tester
    * added support for GW gpio new functionalities and control PLC using GW only
    * added support to more external sensors
    * added support to handle duplication if tag was not printed yet
    * added support to label missing label case
    
* sample test
    * new architecture for sample test including adding sample test sdk class based on the tester sdk.
    * added a resolver class to get external id from packet based on api key
    
    
* yield-tester:
    * add support to clout wafer matrix using the GW and not Arduino.
    * update graph and labels
    * fix bug in temperature calculation


Version 5.3.9:
-----------------
* offline tester: HOTFIX for running without printing

Version 5.3.8:
-----------------
* offline tester: HOTFIX for printer communication

Version 5.3.6:
-----------------
* offline tester:
    * support preprinting procedure 
    * allow to re-scan after scanner exception 
    * added "end of test" tags to the log to keep the reel location, the physical tag location on the reel
    * optimize Cognex scanner performance 
    * filter out un-usable inlays
    * fixed bug when error handling while waiting to end of RF test
    * start scanning before printer ends the operation
    * update reel and run location every iteration
    * improve scanner exception handling
    * fixed bug where the tester moved to the next tag at the end of the run
    * check printer ack every cycle
    * added a protection from uploading big files 
    * improve communication with Rtscanner

* yield tester:
    * add recovery flow for hardware disconnections
    * added simulation code for testing and development
    * improved gui and indication when events occur
    * wafer and lot number are mandatory
  
* sample test:
    * added calibration and support different surfaces in sample slim script
    * support rssi threshold
    * added fail bin based on tbp, tag response and serialization errors
    * improve GUI different modes
    * added indication if files were uploaded to cloud
    
* tester sdk:
    * better implementation to stop gw at the end of a test
    
* added support to specific tests based on partners request
* fixed bug for uploading big files.
* all cloud requests are using client functions from wiliot-api package
* improved light sensor calibration script.
* added function to check if external id is Wiliot's or not


Version 5.1.6:
-----------------
* yield tester: fix logging bugs

Version 5.1.4:
-----------------
* offline tester:
    * Added support to use Cognex scanner
    * improve exceptions handling
    * enable the option to run all test per tag even if one of the test failed
    * support new cloud platform
    * add functions for offline log editing
* sample test:
    * added a stand-alone script to run sample test in a simple manner using command line interface.
    * fix bug when offline mode and improve calibration interface
 * testers equipment:
    * add support to Cognex scanner including improvements and different communication protocols
* tester sdk
    * check at the end of the run if stop criteria was reached just before end of time.
* yield:
    * add more testing and sanity check
    * improve GUI and logs
    * improved arduino communication


Version 5.0.13:
-----------------
* offline tester:
    * new architecture and major reformatting
* sample test:
    * stop run if connection to temperature sensor failed
    * support new platform address
    * modify criteria for pass/fail the reel
* testers equipment:
    * add support more sensors including sensor calibration
    * add support to Cognex scanner
* new tool for retrieve post process for partners output
* tester sdk
    * log: add more functionalities to wiliot log
    * allow to store test info inside results class
    * improved function to load test suite
* yield:
    * working on tag matrix and not per column
    * improve application visualization and robustness
    * clean tags till first trigger
    * add supports in more sensors
    
    
Version 4.0.14:
-----------------
* sample tester:
    * add fail bin for the whole test
    * add the option to construct specific tests including number of tested tags and the parameters for the test to pass/fail
* upload data to cloud:
    * supports also dev env
    * reduce the max size of a big file
* test equipment:
    * improve scanner configuration
    * add logging
* tester sdk:
    * add more fail bins    
    

Version 4.0.12:
-----------------
* offline tester:
    * add responded yield to gui
    * add the option to change the max number of bad QR
    * fix bug in test format
    * fix bug when working with two gw
    * add pop up when upload failed
    * change default line selection to True
    * improve code for printing GUI - production and test
* improve harvester test
* improve function to upload tester data to cloud including big files (>15Mb)
* tester sdk:
    * add more function to the tester log
    * fix bug when stop event is not specified
* yield:
    * add more logging including progress data

Version 4.0.11:
-----------------
* offline tester:
    * fix bug when several tags under test and test status is still pass
    * support 8 characters barcode label
    * Support label scanner for both barcode and QR
    * check printer communication during the run
    
* upload data:
    * fix .bat file for upload data to the cloud
    
* sample test:
    * fix script error when installing on a clean environment
    
    
Version 4.0.6:
-----------------
* offline tester:
    *  update test suite.
    *  enable line selection using text communication with the printing (currently available only if printing offset > 0 and no QR check.
    *  add tag reel location to packet data csv (i.e. the location on the reel even if multiple runs were done on the same reel)
    *  check gw trigger (optic sensor signal) and apply printing validation, right after a trigger was received (or missing label was decided)
    *  check differences between responding yield and pass yield, if the difference is larger than what is defined at the gui json file, the run shall stop. the default values are: "pass_response_diff": 10, (if more than 10% diff the run will stop) "pass_response_diff_offset": 100(ignore this stop criteria until you reached at least 100 tags).
    *  improve test total time calculation to enable “extended test” mode (more than 999 seconds per tag)
    *  add listener process log to the same folder as the offline tester logs.
    *  fix bug when having multiple api keys from different owner id.
    *  add exception if Arduino connection was failed.
*  Sample test:
    *  add new default configuration that can be edited. on the same file new config can be added as well. ('.default_test_configs.json' under sample test folder script → config)
    *  save the above file at the appdata folder for view including the last pywiliot version (so data would not be overwrite if a new pywiliot installation is done).
    *  fix bug where the emulated surface would not be saved from run to run.
    *  update value for emulated surfaces
    *  add the selected sub1g freq to the run data
    *  add inlay types according to all supported antennas.
    *  remove edit tester hw version from the GUI (can be done only by edit .defaults.json
    *  enable testing the same tag multiple times.
    *  add checkbox for the multiple sample test modes: send to cloud, offline mode, calibration mode, send to test env (develop mode)
    *  add calculation for std tbp.
*  tag class (“tester sdk”)
    *  check gw response after reset for robust connection and communication after rest.
    *  delete old commands that are not relevant to the new FW (>4.0.14)
    *  check if trigger was received during the test (i.e. can indicates that the r2r moved before we finished the test or that we have some noise in the system) and stops the run if it was.
    *  if trigger was not received by the gw (e.g. missing label), the gw is reset and re-config to reduce “missing labels” due to problems with the gw.
    *  fix bug where cancel commands did not get ACK from the gw
    *  add a warning when more than one packet was pulled from the queue to monitor low performance of the script.
    *  print a better line per each packet including adva and rssi
    *  check if we had error during gw reading and if gw connection is stable. if not a reset and re-config of the gw are done, if the problem was not fixed an exception is raised.
    *  reset the listener buffer before waiting for trigger and not after.
    *  config between different tests only if the test suite contains more than 1 test
*  yield tester:
    *  improve GUI, including saving previous input.
    *  fix bug for connecting to Arduino
    *  enable upload to cloud data

Version 4.0.0:
-----------------
* First version


The package previous content was published under the name 'wiliot' package.
for more information please read 'wiliot' package's release notes
