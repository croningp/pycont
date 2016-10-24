.. _examples_label:

Examples
********
Here you will find an in-depth example of using the Pycont library.

Pump Usage Example
==================
This is an example of how to control a Tricontinent pump, using the Pycont library.

Below are samples of a .json configuration file which holds the parameters for the pump, and the python script which will control the pump.

JSON Configuration File (pump_setup_config.json)
++++++++++++++++++++++++++++++++++++++++++++++++

This is the structure of a .json configuration file.

* io
    This is the I/O port which will communicate with the pump from the host PC.
    Below is an example of communicating on a UNIX based system.

    * baudrate
        This is the communication baudrate for serial communication. This is usually set to 9600

    * timeout
        The default time to wait until the communication times out. (This is repeated several times)

* default
    These are the default setting for all the pumps on the line. Here is where you set parameters, such as speed and volume.

    * volume
        The maximum volume available to pump

    * micro_step_mode
        This is the default microstep mode for the pumps. Mode 2 should suffice.

    * top_velocity
        This is the top speed for all the pumps.

    * initialize_valve_position
        The default position for the 3/4-way valve on top of the pump.

* groups
    These are the collection of pumps connected on the line. Here, they are named after the chemicals which they hold.

* pumps
    This is where we can set the individual settings for each pump.
    Each pump listed in the "group" section, must have it's "switch" position initialised here.

    * switch
        The switch setting on the back of the pump. This identifies each pump on the line, hardware-wise.

**JSON configuration file example:**

::

    {
        "io":
        {
            "port": "/dev/ttyUSB0",
            "baudrate": 9600,
            "timeout": 1
        },
        "default":
        {
            "volume": 5,
            "micro_step_mode": 2,
            "top_velocity": 5000,
            "initialize_valve_position": "I"
        },
        "groups":
        {
            "chemicals": ["acetone", "water"]
        },
        "pumps":
        {
            "acetone":
            {
                "switch": "0"
            },
            "water":
            {
                "switch": "1"
            }
        }
    }

Python Script (pycont_test.py)
++++++++++++++++++++++++++++++
This is an example of a Python script which uses Pycont to control a set of pumps.

The steps are easy:

1. First, import the appropriate module. Here, it is: 'pycont.controller'
2. Load the .json configuration file in a Controller object, e.g. 'MultiPumpController'
3. Smart initialize the pumps with 'smart_initialize()' function.
4. The pumps are now initialized and ready for use!
5. The pumps can be accessed in two ways:

    * 'controller.pumps['pump_name']'
    * 'controller.pump_name'
    * These are personal preference, use whichever you like.
    
6. Have fun!

**Python Script Example:**

::

    # simply import the module
    import pycont.controller

    # link to your config file
    SETUP_CONFIG_FILE = './pump_setup_config.json'

    # and load the config file in a MultiPumpController
    controller = pycont.controller.MultiPumpController.from_configfile(SETUP_CONFIG_FILE)

    # initialize the pumps in a smart way, if they are already initialized we do not want to reinitialize them because they got back to zero position
    controller.smart_initialize()

    # individual pumps can be accessed in two ways:
    # - in the dict ```controller.pumps['pump_name']```
    # - directly as an attribute ```controller.pump_name```
    # the two above method link to the same pump instance
    # we use the first convention because it highlight well the name of the pumps
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
    controller.pumps['water'].pump(0.5, from_valve=pycont.controller.VALVE_INPUT, wait=True)
    controller.pumps['water'].deliver(0.5, to_valve=pycont.controller.VALVE_OUTPUT, wait=True)

    # you can also transfer volume from valve to valve
    # the function is recusive so even of the volume is bigger than the syringe, it will iterate as many times as needed
    controller.pumps['acetone'].transfer(7, pycont.controller.VALVE_INPUT, pycont.controller.VALVE_OUTPUT)  # this function is blocking, no wait argument
    # note that it pump from and to the position it is currently set to, made it easy to leave a small volume in the pump if needed

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

.. note:: Insert more examples here!
