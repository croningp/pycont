# -*- coding: utf-8 -*-

import time
import json
import serial

import logging
module_logger = logging.getLogger(__name__)

import qlock
import pump_protocol

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

INITIALIZE_VALVE_RIGHT = 'right'
INITIALIZE_VALVE_LEFT = 'left'
INITIALIZE_NO_VALVE = 'no_valve'

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
        self.logger = logging.getLogger(self.__class__.__name__)

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
        self.logger.debug("Opening port '%s'", self.port,
                          extra={'port': self.port,
                                 'baudrate': self.baudrate,
                                 'timeout': self.timeout})

    def close(self):
        self._serial.close()
        self.logger.debug("Closing port '%s'", self.port,
                          extra={'port': self.port,
                                 'baudrate': self.baudrate,
                                 'timeout': self.timeout})

    def flushInput(self):
        self._serial.flushInput()

    def write(self, packet):
        str_to_send = packet.to_string()
        self.logger.debug("Sending {}".format(str_to_send))
        self._serial.write(str_to_send)

    def readline(self):
        msg = self._serial.readline()
        if msg:
            self.logger.debug("Received {}".format(msg))
            return msg
        else:
            raise PumpIOTimeOutError


class PumpIOTimeOutError(Exception):
    pass


class C3000Controller(object):

    def __init__(self, pump_io, name, address, total_volume, micro_step_mode=MICRO_STEP_MODE_2, top_velocity=6000, initialize_mode=INITIALIZE_VALVE_RIGHT, initialize_operand=0):
        self._io = pump_io
        self.qlock = qlock.QLock()

        self.name = name

        self.address = address
        self._protocol = pump_protocol.C3000Protocol(self.address)

        self.initialize_mode = initialize_mode
        self.initialize_operand = initialize_operand

        self.micro_step_mode = micro_step_mode
        if self.micro_step_mode == MICRO_STEP_MODE_0:
            self.number_of_steps = int(N_STEP_MICRO_STEP_MODE_0)  # float
        elif self.micro_step_mode == MICRO_STEP_MODE_2:
            self.number_of_steps = int(N_STEP_MICRO_STEP_MODE_2)  # float
        else:
            raise ValueError('Microstep mode {} is not handled'.format(self.micro_step_mode))

        self.total_volume = float(total_volume)  # in ml (float)
        self.steps_per_ml = int(self.number_of_steps / self.total_volume)

        self.default_top_velocity = top_velocity
        self.current_top_velocity = -1

    @classmethod
    def from_config(cls, pump_io, pump_name, pump_config):

        pump_config['address'] = C3000SwitchToAddress[pump_config['switch']]
        del(pump_config['switch'])

        pump_config['total_volume'] = float(pump_config['volume'])  # in ml (float)
        del(pump_config['volume'])

        return cls(pump_io, pump_name, **pump_config)

    ##
    def write_and_read_from_pump(self, packet):
        self.qlock.acquire()
        self._io.flushInput()
        self._io.write(packet)
        try:
            response = self._io.readline()
            self.qlock.release()
            return self._protocol.decode_packet(response)
        except PumpIOTimeOutError:
            self.qlock.release()
            return False

    ##
    def volume_to_step(self, volume_in_ml):
        return int(round(volume_in_ml * self.steps_per_ml))

    def step_to_volume(self, step):
        return step / float(self.steps_per_ml)

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
    def is_initialized(self):
        initialized_packet = self._protocol.forge_report_initialized_packet()
        (_, _, init_status) = self.write_and_read_from_pump(initialized_packet)
        return bool(int(init_status))

    def smart_initialize(self, valve_position=None, operand_value=None):
        if not self.is_initialized():
            self.initialize(valve_position, operand_value)
        self.init_all_pump_parameters()

    def initialize(self, valve_position=None, operand_value=None, wait=True):

        if valve_position is None:
            valve_position = self.initialize_mode

        if operand_value is None:
            operand_value = self.initialize_operand

        if valve_position == INITIALIZE_VALVE_RIGHT:
            self.initialize_valve_right(operand_value)
        elif valve_position == INITIALIZE_VALVE_LEFT:
            self.initialize_valve_left(operand_value)
        elif valve_position == INITIALIZE_NO_VALVE:
            self.initialize_no_valve(operand_value)
        else:
            raise ValueError('Initialization with valve {} not handled'.format(valve_position))
        if wait:
            self.wait_until_idle()

    def initialize_valve_right(self, operand_value=0):
        self.write_and_read_from_pump(self._protocol.forge_initialize_valve_right_packet(operand_value))

    def initialize_valve_left(self, operand_value=0):
        self.write_and_read_from_pump(self._protocol.forge_initialize_valve_right_packet(operand_value))

    def initialize_no_valve(self, operand_value=0):
        self.write_and_read_from_pump(self._protocol.forge_initialize_no_valve_packet(operand_value))

    ##
    def init_all_pump_parameters(self):
        self.set_microstep_mode(self.micro_step_mode)
        self.wait_until_idle()

        self.set_top_velocity(self.default_top_velocity)
        self.wait_until_idle()

    ##
    def set_microstep_mode(self, micro_step_mode):
        if self.is_initialized():
            self.write_and_read_from_pump(self._protocol.forge_microstep_mode_packet(micro_step_mode))

    ##
    def check_top_velocity_within_range(self, top_velocity):
        if self.micro_step_mode == MICRO_STEP_MODE_0:
            max_range = MAX_TOP_VELOCITY_MICRO_STEP_MODE_0
        elif self.micro_step_mode == MICRO_STEP_MODE_2:
            max_range = MAX_TOP_VELOCITY_MICRO_STEP_MODE_2

        if top_velocity in range(1, max_range + 1):
            return True
        else:
            raise ValueError('Top velocity {} is not in range'.format(self.micro_step_mode))

    def set_default_top_velocity(self, top_velocity):
        self.check_top_velocity_within_range(top_velocity)
        self.default_top_velocity = top_velocity

    def get_default_top_velocity(self):
        return self.default_top_velocity

    def ensure_default_top_velocity(self):
        if self.current_top_velocity != self.default_top_velocity:
            self.set_top_velocity(self.default_top_velocity)

    def set_top_velocity(self, top_velocity, wait=True):
        if self.is_initialized():
            if self.current_top_velocity != top_velocity:
                self.check_top_velocity_within_range(top_velocity)
                self.write_and_read_from_pump(self._protocol.forge_top_velocity_packet(top_velocity))
                self.current_top_velocity = top_velocity

                if wait:
                    self.wait_until_idle()

                return True
        else:
            return False

    def get_top_velocity(self):
        top_velocity_packet = self._protocol.forge_report_peak_velocity_packet()
        (_, _, top_velocity) = self.write_and_read_from_pump(top_velocity_packet)
        return int(top_velocity)

    ##
    def get_plunger_position(self):
        plunger_position_packet = self._protocol.forge_report_plunger_position_packet()
        (_, _, steps) = self.write_and_read_from_pump(plunger_position_packet)
        return int(steps)

    @property
    def current_steps(self):
        return self.get_plunger_position()

    @property
    def remaining_steps(self):
        return self.number_of_steps - self.current_steps

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
        steps = self.volume_to_step(volume_in_ml)
        return steps <= self.remaining_steps

    def pump(self, volume_in_ml, from_valve=None, speed_in=None, wait=False):
        """
        warning change of speed will last after the scope of this function but will be reset to default each time speed_in != None
        """
        if self.is_volume_pumpable(volume_in_ml):

            if speed_in is not None:
                self.set_top_velocity(speed_in)
            else:
                self.ensure_default_top_velocity()

            if from_valve is not None:
                self.set_valve_position(from_valve)

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
        steps = self.volume_to_step(volume_in_ml)
        return steps <= self.current_steps

    def deliver(self, volume_in_ml, to_valve=None, speed_out=None, wait=False):
        """
        warning change of speed will last after the scope of this function but will be reset to default each time speed_out != None
        """
        if self.is_volume_deliverable(volume_in_ml):

            if speed_out is not None:
                self.set_top_velocity(speed_out)
            else:
                self.ensure_default_top_velocity()

            if to_valve is not None:
                self.set_valve_position(to_valve)

            steps_to_deliver = self.volume_to_step(volume_in_ml)
            packet = self._protocol.forge_deliver_packet(steps_to_deliver)
            self.write_and_read_from_pump(packet)

            if wait:
                self.wait_until_idle()

            return True
        else:
            return False

    ##
    def transfer(self, volume_in_ml, from_valve, to_valve, speed_in=None, speed_out=None):
        volume_transfered = min(volume_in_ml, self.remaining_volume)
        self.pump(volume_transfered, from_valve, speed_in=speed_in, wait=True)
        self.deliver(volume_transfered, to_valve, speed_out=speed_out, wait=True)

        remaining_volume_to_transfer = volume_in_ml - volume_transfered
        if remaining_volume_to_transfer > 0:
            self.transfer(remaining_volume_to_transfer, from_valve, to_valve, speed_in, speed_out)

    ##
    def is_volume_valid(self, volume_in_ml):
        return 0 <= volume_in_ml <= self.total_volume

    def go_to_volume(self, volume_in_ml, speed=None, wait=False):
        """
        warning change of speed will last after the scope of this function but will be reset to default each time speed != None
        """
        if self.is_volume_valid(volume_in_ml):

            if speed is not None:
                self.set_top_velocity(speed)
            else:
                self.ensure_default_top_velocity()

            steps = self.volume_to_step(volume_in_ml)
            packet = self._protocol.forge_move_to_packet(steps)
            self.write_and_read_from_pump(packet)

            if wait:
                self.wait_until_idle()

            return True
        else:
            return False

    def go_to_max_volume(self, speed=None, wait=False):
        self.go_to_volume(self.total_volume, speed=speed, wait=wait)

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

    def set_eeprom_config(self, operand_value):
        eeprom_config_packet = self._protocol.forge_eeprom_config_packet(operand_value)
        self.write_and_read_from_pump(eeprom_config_packet)
        print("####################################################")
        print("Unpower and repower the pump to make changes active!")
        print("####################################################")

    def flash_eeprom_3_way_valve(self):
        self.set_eeprom_config("1")

    def flash_eeprom_4_way_valve(self):
        self.set_eeprom_config("2")

    def get_eeprom_config(self):
        (_, _, eeprom_config) = self.write_and_read_from_pump(self._protocol.forge_report_eeprom_packet())
        return eeprom_config


class MultiPumpController(object):

    def __init__(self, setup_config):
        self.logger = logging.getLogger(self.__class__.__name__)

        self._io = PumpIO.from_config(setup_config['io'])

        if 'default' in setup_config:
            self.default_config = setup_config['default']
        else:
            self.default_config = {}

        if 'groups' in setup_config:
            self.groups = setup_config['groups']
        else:
            self.groups = {}

        self.pumps = {}
        for pump_name, pump_config in setup_config['pumps'].items():
            defaulted_pump_config = self.default_pump_config(pump_config)
            self.pumps[pump_name] = C3000Controller.from_config(self._io, pump_name, defaulted_pump_config)
        self.set_pumps_as_attributes()

    @classmethod
    def from_configfile(cls, setup_configfile):
        with open(setup_configfile) as f:
            return cls(json.load(f))

    def default_pump_config(self, pump_config):
        defaulted_pump_config = dict(self.default_config)  # make a copy

        for k, v in pump_config.items():
            defaulted_pump_config[k] = v

        return defaulted_pump_config

    def set_pumps_as_attributes(self):
        for pump_name, pump in self.pumps.items():
            if hasattr(self, pump_name):
                self.logger.warning("Pump named {pump_name} is already a reserved attribute, please change name or do not use this pump in attribute mode, rather use pumps[{pump_name}]".format(pump_name=pump_name))
            else:
                setattr(self, pump_name, pump)

    def get_pumps(self, pump_names):
        pumps = []
        for pump_name in pump_names:
            pumps.append(self.pumps[pump_name])
        return pumps

    def apply_command_to_pumps(self, pump_names, command, *args, **kwargs):

        returns = {}
        for pump_name in pump_names:
            func = getattr(self.pumps[pump_name], command)
            returns[pump_name] = func(*args, **kwargs)

        return returns

    def apply_command_to_all_pumps(self, command, *args, **kwargs):
        return self.apply_command_to_pumps(self.pumps.keys(), command, *args, **kwargs)

    def apply_command_to_group(self, group_name, command, *args, **kwargs):
        return self.apply_command_to_pumps(self.groups[group_name], command, *args, **kwargs)

    ##
    def smart_initialize(self, valve_position=INITIALIZE_VALVE_RIGHT, operand_value=0):
        for _, pump in self.pumps.items():
            if not pump.is_initialized():
                pump.initialize(valve_position, operand_value, wait=False)
        self.wait_until_all_pumps_idle()

        self.apply_command_to_all_pumps('init_all_pump_parameters')
        self.wait_until_all_pumps_idle()

    def wait_until_all_pumps_idle(self):
        self.apply_command_to_all_pumps('wait_until_idle')

    def are_pumps_idle(self):
        for _, pump in self.pumps.items():
            if not pump.is_idle():
                return False
        return True

    def are_pumps_busy(self):
        return not self.are_pumps_idle()

    def pump(self, pump_names, volume_in_ml, from_valve=None, speed_in=None, wait=False):
        """
        reimplemented as MultiPump so it is really synchronous
        """
        if speed_in is not None:
            self.apply_command_to_pumps(pump_names, 'set_top_velocity', speed_in)
        else:
            self.apply_command_to_pumps(pump_names, 'ensure_default_top_velocity')

        if from_valve is not None:
            self.apply_command_to_pumps(pump_names, 'set_valve_position', from_valve)

        self.apply_command_to_pumps(pump_names, 'pump', volume_in_ml, speed_in=speed_in, wait=False)

        if wait:
            self.apply_command_to_pumps(pump_names, 'wait_until_idle')

    def deliver(self, pump_names, volume_in_ml, to_valve=None, speed_out=None, wait=False):
        """
        reimplemented as MultiPump so it is really synchronous
        """
        if speed_out is not None:
            self.apply_command_to_pumps(pump_names, 'set_top_velocity', speed_out)
        else:
            self.apply_command_to_pumps(pump_names, 'ensure_default_top_velocity')

        if to_valve is not None:
            self.apply_command_to_pumps(pump_names, 'set_valve_position', to_valve)

        self.apply_command_to_pumps(pump_names, 'deliver', volume_in_ml, speed_out=speed_out, wait=False)

        if wait:
            self.apply_command_to_pumps(pump_names, 'wait_until_idle')

    def transfer(self, pump_names, volume_in_ml, from_valve, to_valve, speed_in=None, speed_out=None):
        """
        reimplemented as MultiPump so it is really synchronous, needed
        """
        volume_transfered = 1000000  # some big number 1000L is more than any descent person will try
        for pump in self.get_pumps(pump_names):
            candidate_volume = min(volume_in_ml, pump.remaining_volume)
            volume_transfered = min(candidate_volume, volume_transfered)

        self.pump(pump_names, volume_transfered, from_valve, speed_in=speed_in, wait=True)
        self.deliver(pump_names, volume_transfered, to_valve, speed_out=speed_out, wait=True)

        remaining_volume_to_transfer = volume_in_ml - volume_transfered
        if remaining_volume_to_transfer > 0:
            self.transfer(pump_names, remaining_volume_to_transfer, from_valve, to_valve, speed_in, speed_out)
