# -*- coding: utf-8 -*-

import os
import sys
# add parent folder to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import pycont


SETUP_CONFIG_FILE = './pump_setup_config.json'

with open(SETUP_CONFIG_FILE) as f:
    setup_config = json.load(f)

controller = pycont.MultiPumpController(setup_config)

controller.smart_initialize()

for _, pump in controller.pumps.items():
    pump.go_to_volume(0)
controller.wait_until_all_pumps_idle()

controller.pumps['pump0'].go_to_volume(0.5)
controller.pumps['pump1'].go_to_volume(0.5)
controller.wait_until_all_pumps_idle()

controller.apply_command_to_all_pumps('go_to_max_volume')
while controller.are_pumps_busy():
    print(controller.apply_command_to_all_pumps('get_volume'))
