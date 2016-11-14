# pycont

pycont is a python library to control Tricontinent C3000 pumps. It is meant to be easy to use, and transparent such that when reading your program you can actually know what is going on.

## Documentation
For documentation on using this library and it's associated methods, please see the [pycont Github Pages](https://croningp.github.io/pycont/).

## Tutorial

### Wiring the pumps

[Components to buy](docs/useful_links.md)

Some documents are available in the [docs folder](docs).

### Setting up the pumps

Be sure which type of valve you are using (see [p28-31](docs/pumps/tricont%20software%20man.pdf)) and that the pump is using the appropriate EEPROM setting (see example below).

If you are using a 3-way valve (Y-shape) you will need to put a jumper on [J2 pin 5](docs/pumps/pumps_wiring.pdf). This doesn't require change to EEPROM.

Remove all other jumpers except [J2 pin 1](docs/pumps/pumps_wiring.pdf), which is a spare.

(RS485 termination jumpers not required since communication baudrate is only 9600.)


### Installing the library

```
git clone http://datalore.chem.gla.ac.uk/JOG/pycont.git
cd pycont
python setup.py install  # with the appropriate rights, might need to use sudo
```

Alternatively, if you plan to work on the library itself, use
```
python setup.py develop
```
which make a direct link to the folder you are working on

### Using the library

An example is availbale in the [tests folder](tests).

Using a [config file](tests/pump_setup_config.json), you can define:
- the communication port you are using
- some default configuration for pumps that will be applied to pumps unless otherwise specified
- a description of each pumps you use in your system, for each pump you define:
    - it's name, e.g. "acetone", which will ease the reuse of your code if you decide to change pump, the name can stay the same and your code work the same
    - a config field which can contain:
      - the "back switch" value which represent the pumps id
      - the volume of the syringe (such that you only play with volume in your program, most intuitive)
      - the speed at which you want to operate (this can obviously be change while in operation)
      - the micro_step_mode

A config file looks like this:
```python
{
  "io": {
      "port": "/dev/ttyUSB0",
      "baudrate": 9600,
      "timeout": 1
  },
  "default": {
    "volume": 5,
    "micro_step_mode": 2,
    "top_velocity": 24000,
    "initialize_valve_position": "I",
  },
  "groups": {
    "chemicals": ["acetone", "water"]
  },
  "pumps": {
      "acetone": {
        "switch": "0"
      },
      "water": {
          "switch": "1",
          "top_velocity": 12000
      }
  }
}
```

You can then instantiate a MultiPumpController, and have fun:

```python
import time

import logging
logging.basicConfig(level=logging.INFO)

# simply import the module
import pycont.controller

# link to your config file
SETUP_CONFIG_FILE = './pump_setup_config.json'

# and load the config file in a MultiPumpController
controller = pycont.controller.MultiPumpController.from_configfile(SETUP_CONFIG_FILE)

# initialize the pumps in a smart way, if they are already initialized we do not want to reinitialize them because they go back to zero position
controller.smart_initialize()

# individual pumps can be accessed in two ways:
# - in the dict ```controller.pumps['pump_name']```
# - directly as an attribute ```controller.pump_name```
# the two above method link to the same pump instance
# we use the first convention becuase it highlight well the name of the pumps
# the second convention is certainly more convenient for online testing using ipython

# ask a pump to go to a specific position, calling it by its name
# the wait argument signifies if the command is blocking or non-blocking
# if wait=False (default), the function returns immediately and let you go on
# volumes are always in mL
controller.pumps['acetone'].go_to_volume(0.5, wait=False)
# if wait=True, the function returns only after the pump finished his move
controller.pumps['water'].go_to_volume(0.5, wait=True)

# of course you can pump and deliver volumes
controller.pumps['water'].pump(0.5, wait=True)
controller.pumps['water'].deliver(0.5, wait=True)

# and those function tells you is the action what feasible or not
succeed = controller.pumps['water'].pump(1000, wait=True)
if succeed:
    print('How could you pump 1000 mL')
else:
    print('You cannot pump 1000 mL!')

# the pump and deliver function respectively have a from_valve and to_valve argument
# if set, the valve position is set before the pump moves
controller.pumps['water'].pump(0.5, from_valve=pycont.controller.VALVE_INPUT, wait=True) # pycont.controller.VALVE_INPUT is 'I', idem for output 'O', bypass 'B', and extra 'E'
controller.pumps['water'].deliver(0.5, to_valve='O', wait=True)

# you can also transfer volume from valve to valve
# the function is recursive so even of the volume is bigger than the syringe, it will iterate as many times as needed
controller.pumps['acetone'].transfer(7, 'I', 'O')  # this function is blocking, no wait argument
# note that it pump from and to the position it is currently set to, made it easy to leave a small volume in the pump if needed

# you can also iterate on all the pumps
for _, pump in controller.pumps.items():
    pump.go_to_volume(0)  # here wait=False by default, all pumps move in parallel
# wait until all pumps are ready to operate again
controller.wait_until_all_pumps_idle()

# you can apply command to all pumps in parallel, in one command!
# this is the purpose of the controller.apply_command_to_all_pumps
# let's have the pumps go to their max volume
# the below function go through the list of pumps and run the 'go_to_max_volume' function without argument
controller.apply_command_to_all_pumps('go_to_max_volume')
while controller.are_pumps_busy():
    # and record the volume in real time as the pumps are moving
    print(controller.apply_command_to_all_pumps('get_volume'))

# and you set pump group in the config file and apply command to a group of pumps
# check the config file for group definition
# in this example 'chemicals' contains ['water', 'acetone']
controller.apply_command_to_group('chemicals', 'go_to_volume', 1)
controller.wait_until_all_pumps_idle()

# the two above function call the more generic apply_command_to_pumps function
# which take a list of pumps to apply the command to
controller.apply_command_to_pumps(['water', 'acetone'], 'go_to_volume', 1.5)
controller.wait_until_all_pumps_idle()

# So the three above way are different way to do the same things
# groups are a powerful way to automate initialization of your setup

time.sleep(1)  # just to pause so that you can hear the sound of valve movements

# of course you can change valve position
# for this you should use the command set_valve_position(valve_position) using for valvle position the global variable define in pycont. They are VALVE_INPUT, VALVE_OUTPUT, VALVE_BYPASS, VALVE_EXTRA
controller.pumps['acetone'].set_valve_position(pycont.controller.VALVE_OUTPUT)
controller.pumps['water'].set_valve_position(pycont.controller.VALVE_OUTPUT)

time.sleep(1)  # just to pause so that you can hear the sound of valve movements

# of course you can change all the valve position at once
# apply_command_to_all_pumps will forward all additional argument
controller.apply_command_to_all_pumps('set_valve_position', pycont.controller.VALVE_INPUT)

# get valve position
print(controller.pumps['water'].get_valve_position())
print(controller.apply_command_to_all_pumps('get_valve_position'))

# and compare it with global defined variable
if controller.pumps['water'].get_valve_position() == pycont.controller.VALVE_INPUT:
    print('The valve for water is indeed in input position')
else:
    print('Something went wrong when setting the valve position')


# finally there is some tools to track the status of the pumps
print(controller.pumps['water'].is_idle())  # is the pump ready?
print(controller.pumps['water'].is_busy())  # is the pump busy?
print(controller.pumps['water'].current_volume)  # what volume is in the syringe, this is a direct reading from the pump position, we actually ask the pump!
print(controller.pumps['water'].remaining_volume)  # what volume can still be pump
print(controller.pumps['water'].is_volume_pumpable(1))  # can I pump 1 ml?
print(controller.pumps['water'].is_volume_deliverable(1))  # can I deliver 1 ml?

# But note that the above tools are mostly encompassed in the higher level functions such as controller.wait_until_all_pumps_idle() which check is_idle() for all pumps

# Have fun!
```

### EEPROM settings

The EEPROM flash memory on the pumps can be changed using the following commands:

```python
# There are 4 commands for the 4 types of valve

#controller.pumps['water'].flash_eeprom_3_way_y_valve()         # Not strictly necessary since a jumper pin will do the same thing regardless of EEPROM setting
#controller.pumps['water'].flash_eeprom_3_way_t_valve()
#controller.pumps['water'].flash_eeprom_4_way_nondist_valve()
controller.pumps['water'].flash_eeprom_4_way_dist_valve()
```

## Dialout Issues
On initial use, there may be an issue with permissions when trying to communicate over the USB connection on Unix-based OS'. This can be solved by adding the main user to the 'dialout' group on the computer:
```
sudo adduser <username> dialout
```
As this library was develop for Unix-based OS', this issue may not be encountered on Windows.
