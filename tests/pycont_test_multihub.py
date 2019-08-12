# -*- coding: utf-8 -*-

import time

import logging
logging.basicConfig(level=logging.DEBUG)

# Import the controller
from pycont import MultiPumpController

# link to your config file
SETUP_CONFIG_FILE = './pump_multihub_config.json'

# and load the config file in a MultiPumpController
controller = MultiPumpController.from_configfile(SETUP_CONFIG_FILE)

# Initialize the pumps in a smart way. Smart way here means that:
#
# - if they are already initialized they are not re-initialized (this would cause their plunger to go back to volume=0)
# - before initializing the plunger, the valve is set to the position specified as 'initialize_valve_position'
#   this is defaulted to 'I' and is important as initialization with valve connected to a fluidic path characterized by
#   high pressure drop is likely to fail due to the relatively high plunger speeds normally used during initialization
controller.smart_initialize()

controller.apply_command_to_group(group_name="oils", command="transfer", volume_in_ml=5, from_valve='I', to_valve='O')
controller.apply_command_to_group(group_name="oils", command="wait_until_idle")
