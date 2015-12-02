# pycont

pycont is a python library to control Tricontinent C3000 pumps. It is meant to be easy to use, and transparent such that when reading your program you can actually know what is going on.

## TODO

 - be more robust to errors from the pumps, handle timeout
 <!-- - global default setting in config file -->
 <!-- - implement initialized different per pump if set in config file -->
 <!-- - remove field name for pumps and make it a dict -->
 <!-- - remove C3000... in class method and replace by cls -->
 - set pump as attribute of the class
 <!-- - pump and deliver with from_valve and speed -->
 <!-- - implement a transfer function, transferring volume from valve to valve -->
 - flash eeprom 3 way, 4 way
 <!-- - set function should have a parameter set the variable and send if pump is initialized -->



## Tutorial

### Wiring the pumps

Some documents are available in the [docs folder](http://datalore.chem.gla.ac.uk/JOG/pycont/tree/master/docs).

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

An example is availbale in the [tests folder](http://datalore.chem.gla.ac.uk/JOG/pycont/tree/master/tests).

Using a [config file](http://datalore.chem.gla.ac.uk/JOG/pycont/blob/master/tests/pump_setup_config.json), you can define:
- the communication port you are using
- a description of each pumps you use in your system, for each pump you define:
    - give a name to your pump, e.g. "acetone", which will ease the reuse of your code if you decide to change pump, the name can stay the same and your code work the same
    - the "back switch" value which represent the pumps id
    - the volume of the syringe (such that you only play with volume in your program, most intuitive)
    - the speed at which you want to operate (this can obviously be change while in operation)

A config file looks like this:
```python
{
  "io": {
      "port": "/dev/ttyUSB0",
      "baudrate": 9600,
      "timeout": 1
  },
  "pumps": [
      {
        "name": "acetone",
        "switch": "0",
        "volume": 5,
        "micro_step_mode": 2,
        "top_velocity": 24000
      },
      {
          "name": "water",
          "switch": "1",
          "volume": 5,
          "micro_step_mode": 2,
          "top_velocity": 24000
      }
  ]
}

```

You can then instantiate a MultiPumpController, and have fun:

```python

# simply import the module
import pycont.controller

# link to your config file
SETUP_CONFIG_FILE = './pump_setup_config.json'

# and load the config file in a MultiPumpController
controller = pycont.controller.MultiPumpController.from_configfile(SETUP_CONFIG_FILE)

# initialize the pumps in a smart way, if they are already initialized we do not want to reinitialize them because they got back to zero position
controller.smart_initialize()

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

# you can also iterate on all the pumps
for _, pump in controller.pumps.items():
    pump.go_to_volume(0)  # here wait=False by default, all pumps move in parrallel
# wait until all pumps are ready to operate again
controller.wait_until_all_pumps_idle()

# you can apply command to all pumps in parrallel, in one command!
# this is the purpose of the controller.apply_command_to_all_pumps
# let's have the pumps go to their max volume
# the below function go through the list of pumps and run the 'go_to_max_volume' function without argument
controller.apply_command_to_all_pumps('go_to_max_volume')
while controller.are_pumps_busy():
    # and record the volume in real time as the pumps are moving
    print(controller.apply_command_to_all_pumps('get_volume'))

time.sleep(1)  # just to pause so that you can hear the sound of valve movements

# of course you can change valve position
# for this you should use the command set_valve_position(valve_position) using for valvle position the global variable define in pycont. They are VALVE_INPUT, VALVE_OUTPUT, VALVE_BYPASS, VALVE_EXTRA
controller.pumps['acetone'].set_valve_position(pycont.VALVE_OUTPUT)
controller.pumps['water'].set_valve_position(pycont.VALVE_OUTPUT)

time.sleep(1)  # just to pause so that you can hear the sound of valve movements

# of course you can change all the valve position at once
# apply_command_to_all_pumps will forward all additional argument
controller.apply_command_to_all_pumps('set_valve_position', pycont.VALVE_INPUT)

# get valvel position
print(controller.pumps['water'].get_valve_position())
print(controller.apply_command_to_all_pumps('get_valve_position'))

# and compare it with global defined variable
if controller.pumps['water'].get_valve_position() == pycont.VALVE_INPUT:
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
