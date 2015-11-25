# -*- coding: utf-8 -*-

import time
import json
import serial
import logging


import pump_protocol

logger = logging.getLogger(__name__)

C3000Broadcast = '_'

C3000SwitchToAddress = {
    '0': '1',
    '1': '2',
    '2': '3',
    '3': '4',
    '4': '5',
    '5': '6',
    '6': '7',
    '7': '8',
    '8': '9',
    '9': ':',
    'A': ';',
    'B': '<',
    'C': '=',
    'D': '>',
    'E': '?',
    'BROADCAST': C3000Broadcast,
}

VALVE_INPUT = 'I'
VALVE_OUTPUT = 'O'
VALVE_BYPASS = 'B'
VALVE_EXTRA = 'E'

MICRO_STEP_MODE_0 = 0
MICRO_STEP_MODE_2 = 2

N_STEP_MICRO_STEP_MODE_0 = 3000
N_STEP_MICRO_STEP_MODE_2 = 24000

MAX_TOP_VELOCITY_MICRO_STEP_MODE_0 = 6000
MAX_TOP_VELOCITY_MICRO_STEP_MODE_2 = 48000

DEFAULT_IO_BAUDRATE = 9600
DEFAULT_IO_TIMEOUT = 1

WAIT_SLEEP_TIME = 0.1


class PumpIO(object):

    def __init__(self, port, baudrate=DEFAULT_IO_BAUDRATE, timeout=DEFAULT_IO_TIMEOUT):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout

        self.open(port, baudrate, timeout)

    @classmethod
    def from_config(cls, io_config):
        port = io_config['port']

        if 'baudrate' in io_config:
            baudrate = io_config['baudrate']
        else:
            baudrate = DEFAULT_IO_BAUDRATE

        if 'timeout' in io_config:
            timeout = io_config['timeout']
        else:
            timeout = DEFAULT_IO_TIMEOUT

        return cls(port, baudrate, timeout)

    @classmethod
    def from_configfile(cls, io_configfile):
        with open(io_configfile) as f:
            return cls.from_config(json.load(f))

    def __del__(self):
        self.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def open(self, port, baudrate=DEFAULT_IO_BAUDRATE, timeout=DEFAULT_IO_TIMEOUT):
        self._serial = serial.Serial(port, baudrate, timeout=timeout)
        logger.info("Opening port '%s'", self.port,
                    extra={'port': self.port,
                           'baudrate': self.baudrate,
                           'timeout': self.timeout})

    def close(self):
        self._serial.close()
        logger.info("Closing port '%s'", self.port,
                    extra={'port': self.port,
                           'baudrate': self.baudrate,
                           'timeout': self.timeout})

    def flushInput(self):
        self._serial.flushInput()

    def write(self, packet):
        self._serial.write(packet.to_string())

    def readline(self):
        return self._serial.readline()


class C3000Controller(object):

    def __init__(self, pump_io, name, address, total_volume, micro_step_mode=2, top_velocity=6000):
        self._io = pump_io

        self.name = name
        self.address = address
        self.total_volume = float(total_volume)  # in ml (float)

        self.micro_step_mode = micro_step_mode
        if self.micro_step_mode == MICRO_STEP_MODE_0:
            self.number_of_steps = float(N_STEP_MICRO_STEP_MODE_0)  # float
        elif self.micro_step_mode == MICRO_STEP_MODE_2:
            self.number_of_steps = float(N_STEP_MICRO_STEP_MODE_2)  # float
        else:
            raise ValueError('Microstep mode {} is not handled'.format(self.micro_step_mode))

        self.top_velocity = top_velocity
        self.steps_per_ml = self.number_of_steps / self.total_volume

        self._protocol = pump_protocol.C3000Protocol(self.address)

    @classmethod
    def from_config(cls, pump_io, pump_config):
        name = pump_config['name']
        address = C3000SwitchToAddress[pump_config['switch']]
        total_volume = float(pump_config['volume'])  # in ml (float)

        kwargs = {}
        if 'micro_step_mode' in pump_config:
            kwargs['micro_step_mode'] = pump_config['micro_step_mode']

        if 'top_velocity' in pump_config:
            kwargs['top_velocity'] = pump_config['top_velocity']

        return C3000Controller(pump_io, name, address, total_volume, **kwargs)

    ##
    def write_and_read_from_pump(self, packet):
        self._io.flushInput()
        self._io.write(packet)
        response = self._io.readline()
        if response:
            return self._protocol.decode_packet(response)
        # if no reponse (timeout) return False, should be handled better, maybe raising an error
        return False
    
    ##
    def volume_to_step(self, volume_in_ml):
        return int(round(volume_in_ml * self.steps_per_ml))

    def step_to_volume(self, step):
        return step / self.steps_per_ml

    ##
    def is_idle(self):
        report_status_packet = self._protocol.forge_report_status_packet()
        (_, status, _) = self.write_and_read_from_pump(report_status_packet)
        if status == pump_protocol.STATUS_IDLE_ERROR_FREE:
            return True
        elif status == pump_protocol.STATUS_BUSY_ERROR_FREE:
            return False
        else:
            raise ValueError('The pump replied status {}, Not handled'.format(status))

    def is_busy(self):
        return not self.is_idle()

    def wait_until_idle(self):
        while self.is_busy():
            time.sleep(WAIT_SLEEP_TIME)
    
    ##
    def eeprom_config(self, argument):
        eeprom_packet = self._protocol.forge_eeprom_config_packet(argument)
        (_, _, eeprom_response) = self.write_and_read_from_pump(eeprom_packet)
        return bool(int(eeprom_response))
    
    ##
    def is_initialized(self):
        initialized_packet = self._protocol.forge_report_initialized_packet()
        (_, _, init_status) = self.write_and_read_from_pump(initialized_packet)
        return bool(int(init_status))

    def smart_initialize(self, valve_position='right'):
        if not self.is_initialized():
            self.initialize(valve_position)
        self.set_all_pump_parameters()

    def initialize(self, valve_position='right'):
        if valve_position == 'right':
            self.initialize_right()
        if valve_position == 'left':
            self.initialize_left()
        else:
            raise ValueError('Initialization with valve {} not hadled'.format(valve_position))
        self.wait_until_idle()

    def initialize_right(self):
        self.write_and_read_from_pump(self._protocol.forge_initialize_right_packet())

    def initialize_left(self):
        self.write_and_read_from_pump(self._protocol.forge_initialize_left_packet())

    ##
    def set_all_pump_parameters(self):
        self.set_microstep_mode()
        self.wait_until_idle()

        self.set_top_velocity()
        self.wait_until_idle()

    ##
    def set_microstep_mode(self):
        self.write_and_read_from_pump(self._protocol.forge_microstep_mode_packet(self.micro_step_mode))

    ##
    def is_top_velocity_within_range(self, top_velocity):
        if self.micro_step_mode == MICRO_STEP_MODE_0:
            max_range = MAX_TOP_VELOCITY_MICRO_STEP_MODE_0
        elif self.micro_step_mode == MICRO_STEP_MODE_2:
            max_range = MAX_TOP_VELOCITY_MICRO_STEP_MODE_2
        else:
            raise ValueError('Top velocity {} is not in range'.format(self.micro_step_mode))

        return top_velocity in range(1, max_range + 1)

    def get_top_velocity(self):
        top_velocity_packet = self._protocol.forge_report_peak_velocity_packet()
        (_, _, top_velocity) = self.write_and_read_from_pump(top_velocity_packet)
        return int(top_velocity)

    def set_top_velocity(self):
        self.write_and_read_from_pump(self._protocol.forge_top_velocity_packet(self.top_velocity))

    def change_top_velocity(self, new_top_velocity):
        self.top_velocity = new_top_velocity
        self.set_top_velocity()

    ##
    def get_plunger_position(self):
        plunger_position_packet = self._protocol.forge_report_plunger_position_packet()
        (_, _, steps) = self.write_and_read_from_pump(plunger_position_packet)
        return int(steps)

    def get_volume(self):
        return self.step_to_volume(self.get_plunger_position())  # in ml

    @property
    def current_volume(self):
        return self.get_volume()

    @property
    def remaining_volume(self):
        return self.total_volume - self.current_volume

    ##
    def is_volume_pumpable(self, volume_in_ml):
        return volume_in_ml <= self.remaining_volume

    def pump(self, volume_in_ml, wait=False):
        if self.is_volume_pumpable(volume_in_ml):
            steps_to_pump = self.volume_to_step(volume_in_ml)

            packet = self._protocol.forge_pump_packet(steps_to_pump)
            self.write_and_read_from_pump(packet)

            if wait:
                self.wait_until_idle()

            return True
        else:
            return False

    ##
    def is_volume_deliverable(self, volume_in_ml):
        return volume_in_ml <= self.current_volume

    def deliver(self, volume_in_ml, wait=False):
        if self.is_volume_deliverable(volume_in_ml):
            steps_to_deliver = self.volume_to_step(volume_in_ml)

            packet = self._protocol.forge_deliver_packet(steps_to_deliver)
            self.write_and_read_from_pump(packet)

            if wait:
                self.wait_until_idle()

            return True
        else:
            return False

    ##
    def is_volume_valid(self, volume_in_ml):
        return 0 <= volume_in_ml <= self.total_volume

    def go_to_volume(self, volume_in_ml, wait=False):
        if self.is_volume_valid(volume_in_ml):
            steps = self.volume_to_step(volume_in_ml)

            packet = self._protocol.forge_move_to_packet(steps)
            self.write_and_read_from_pump(packet)

            if wait:
                self.wait_until_idle()

            return True
        else:
            return False

    def go_to_max_volume(self, wait=False):
        self.go_to_volume(self.total_volume, wait=wait)

    # valve
    def get_raw_valve_postion(self):
        valve_position_packet = self._protocol.forge_report_valve_position_packet()
        (_, _, raw_valve_position) = self.write_and_read_from_pump(valve_position_packet)
        return raw_valve_position

    def get_valve_position(self):
        raw_valve_position = self.get_raw_valve_postion()
        if raw_valve_position == 'i':
            return VALVE_INPUT
        elif raw_valve_position == 'o':
            return VALVE_OUTPUT
        elif raw_valve_position == 'b':
            return VALVE_BYPASS
        elif raw_valve_position == 'e':
            return VALVE_EXTRA
        else:
            raise ValueError('Valve position received was {}. It is unknown'.format(raw_valve_position))

    def set_valve_position(self, valve_position, wait=True):

        if valve_position == VALVE_INPUT:
            valve_position_packet = self._protocol.forge_valve_input_packet()
        elif valve_position == VALVE_OUTPUT:
            valve_position_packet = self._protocol.forge_valve_output_packet()
        elif valve_position == VALVE_BYPASS:
            valve_position_packet = self._protocol.forge_valve_bypass_packet()
        elif valve_position == VALVE_EXTRA:
            valve_position_packet = self._protocol.forge_valve_extra_packet()
        else:
            raise ValueError('Valve position {} unknown'.format(valve_position))

        self.write_and_read_from_pump(valve_position_packet)

        if wait:
            self.wait_until_idle()


class MultiPumpController(object):

    def __init__(self, setup_config):
        self._io = PumpIO.from_config(setup_config['io'])

        self.pumps = {}
        for pump_config in setup_config['pumps']:
            pump_name = pump_config['name']
            self.pumps[pump_name] = C3000Controller.from_config(self._io, pump_config)

    @classmethod
    def from_configfile(cls, setup_configfile):
        with open(setup_configfile) as f:
            return cls(json.load(f))

    def apply_command_to_pumps(self, pump_names, command, *args, **kwargs):

        returns = {}
        for pump_name in pump_names:
            func = getattr(self.pumps[pump_name], command)
            returns[pump_name] = func(*args, **kwargs)

        return returns

    def apply_command_to_all_pumps(self, command, *args, **kwargs):
        return self.apply_command_to_pumps(self.pumps.keys(), command, *args, **kwargs)

    ##
    def smart_initialize(self):
        self.apply_command_to_all_pumps('smart_initialize')

    def wait_until_all_pumps_idle(self):
        self.apply_command_to_all_pumps('wait_until_idle')

    def are_pumps_idle(self):
        for _, pump in self.pumps.items():
            if not pump.is_idle():
                return False
        return True

    def are_pumps_busy(self):
        return not self.are_pumps_idle()
