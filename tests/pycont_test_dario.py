# -*- coding: utf-8 -*-

import time

import logging
logging.basicConfig(level=logging.DEBUG)

# simply import the module
import pycont.controller

# link to your config file
SETUP_CONFIG_FILE = './pump_test_config.json'

# and load the config file in a MultiPumpController
controller = pycont.controller.MultiPumpController.from_configfile(SETUP_CONFIG_FILE)

# initialize the pumps in a smart way, if they are already initialized we do not want to reinitialize them because they got back to zero position
# controller.smart_initialize()

# controller.apply_command_to_group(group_name="oils", command="go_to_max_volume")
# controller.apply_command_to_group(group_name="oils", command="wait_until_idle")
# controller.apply_command_to_group(group_name="oils", command="transfer", volume_in_ml=5, from_valve='I', to_valve='O')

# print(controller.pumps['acetone'].transfer(volume_in_ml=1, from_valve=1, to_valve=) )
# input("Flashing EEPROM! Press enter to confirm")
# controller.pumps['acetone'].flash_eeprom_3_way_y_valve()
#
# input("Reboot pump and press enter to continue...")


# controller.smart_initialize()
# controller.pumps['acetone'].initialize()
# print(controller.pumps['acetone'].get_current_valve_config())
# print(controller.pumps['acetone'].get_eeprom_config())
controller.pumps['acetone'].go_to_max_volume()
# Set max motor speed to 90%
# controller.pumps['acetone'].set_eeprom_lowlevel_config(2, 75)
# print("Pumping from inlet to outlet")

# for _ in range(0, 5):
#     controller.pumps['acetone'].transfer(volume_in_ml=0.5, from_valve='I', to_valve='O', speed_in=20000, speed_out=20000)

# controller.pumps['acetone'].transfer(volume_in_ml=1, from_valve='I', to_valve='O')
# controller.pumps['acetone'].transfer(volume_in_ml=1, from_valve='I', to_valve='E')

# for _ in range(0, 100):
#     controller.pumps['acetone'].go_to_volume(0, speed=3500, wait=True)
#     controller.pumps['acetone'].go_to_max_volume(speed=3500, wait=True)

