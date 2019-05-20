# -*- coding: utf-8 -*-

import time

import logging
logging.basicConfig(level=logging.INFO)

# simply import the module
import pycont.controller

# link to your config file
SETUP_CONFIG_FILE = './pump_test_config.json'

# and load the config file in a MultiPumpController
controller = pycont.controller.MultiPumpController.from_configfile(SETUP_CONFIG_FILE)

# initialize the pumps in a smart way, if they are already initialized we do not want to reinitialize them because they got back to zero position
# controller.smart_initialize()
# print(controller.pumps['acetone'].get_current_valve_config())
# input("Flashing EEPROM! Press enter to confirm")
# controller.pumps['acetone'].flash_eeprom_4_way_dist_valve()
# input("Reboot pump and press enter to continue...")

controller.smart_initialize()
print(controller.pumps['acetone'].get_current_valve_config())
print("Pumping from inlet to outlet")
controller.pumps['acetone'].transfer(volume_in_ml=0.5, from_valve='I', to_valve='O')
# controller.pumps['acetone'].transfer(volume_in_ml=5, from_valve='I', to_valve='E')
controller.pumps['acetone'].go_to_volume(0)

controller.wait_until_all_pumps_idle()

