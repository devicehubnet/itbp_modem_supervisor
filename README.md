# GPRS/3G/4G modem supervisor & control script

This software will monitor the internet connection and perform modem hardware reset using GPIO pins.

## Installation

### Using pip
    pip install DHModemSupervisor
    
### Download and install 
    sudo ./setup.py install
    sudo apt install python-pip ppp
    sudo pip install -r requirements.txt

## TODO
 * Configure modem settings (serial port, baud) from dhmsupervisord.ini
 * Configure APN setting directly from dhmsupervisord.ini
 * Stop GPRS connection if wlan or ethernet is functional
 * Create deb package for installation using apt

## Platforms

This software was tested on the following hardware platforms:

 * RaspberryPi
 * BeagleBone Black
 * FriendlyArm mini2440
