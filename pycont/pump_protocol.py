"""
.. module:: pump_protocol
   :platform: Unix
   :synopsis: A module which outlines the protocol for which the pumps will follow.

.. moduleauthor:: Jonathan Grizou <Jonathan.Grizou@gla.ac.uk>

"""
# -*- coding: utf-8 -*-
from ._logger import create_logger

from . import dtprotocol

#: Command to execute
CMD_EXECUTE = 'R'
#: Command to initialise with the right valve position as output
CMD_INITIALIZE_VALVE_RIGHT = 'Z'
#: Command to initialise with the left valve position as output
CMD_INITIALIZE_VALVE_LEFT = 'Y'
#: Command to initialise with no valve
CMD_INITIALIZE_NO_VALVE = 'W'
#: Command to initialise with valves only
CMD_INITIALIZE_VALVE_ONLY = 'w'
#: Command to invoke microstep mode
CMD_MICROSTEPMODE = 'N'
#: Command to move the pump to a location
CMD_MOVE_TO = 'A'
#: Command to access a specific pump
CMD_PUMP = 'P'
#: Command to deliver payload
CMD_DELIVER = 'D'
#: Command to achieve top velocity
CMD_TOPVELOCITY = 'V'
#: Command to access the EEPROM configuration
CMD_EEPROM_CONFIG = 'U'      # Requires power restart to take effect
CMD_EEPROM_LOWLEVEL_CONFIG = 'u'      # Requires power restart to take effect
#: Command to terminate current operation
CMD_TERMINATE = 'T'

#: Command for the valve init_all_pump_parameters
#: .. note:: Depending on EEPROM settings (U4 or U11) 4-way distribution valves either use IOBE or I<n>O<n>
CMD_VALVE_INPUT = 'I'   # Depending on EEPROM settings (U4 or U11) 4-way distribution valves either use IOBE or I<n>O<n>
#: Command for the valve output
CMD_VALVE_OUTPUT = 'O'
#: Command for the valve bypass
CMD_VALVE_BYPASS = 'B'
#: Command for the extra valve
CMD_VALVE_EXTRA = 'E'

#: Command for the reporting the status
CMD_REPORT_STATUS = 'Q'
#: Command for reporting hte plunger position
CMD_REPORT_PLUNGER_POSITION = '?'
#: Command for reporting the start velocity
CMD_REPORT_START_VELOCITY = '?1'
#: Command for reporting the peak velocity
CMD_REPORT_PEAK_VELOCITY = '?2'
#: Command for reporting the cutoff velocity
CMD_REPORT_CUTOFF_VELOCITY = '?3'
#: Command for reporting the valve position
CMD_REPORT_VALVE_POSITION = '?6'
#: Command for reporting initialisation
CMD_REPORT_INTIALIZED = '?19'
#: Command for reporting the EEPROM
CMD_REPORT_EEPROM = '?27'
#: Command for reporting the status of J2-5 for 3 way-Y valve (i.e. 120 deg rotation)
CMD_REPORT_JUMPER_3WAY = '?28'

#: Idle status when there are no errors
STATUS_IDLE_ERROR_FREE = '`'
#: Busy status when there are no errors
STATUS_BUSY_ERROR_FREE = '@'

# ERROR STATUSES
#: Idle status for initialization failure
STATUS_IDLE_INIT_FAILURE = 'a'
#: Busy status for initialization failure
STATUS_BUSY_INIT_FAILURE = 'A'
#: Idle status for invalid command
STATUS_IDLE_INVALID_COMMAND = 'b'
#: Busy status for invalid command
STATUS_BUSY_INVALID_COMMAND = 'B'
#: Idle status for invalid operand
STATUS_IDLE_INVALID_OPERAND = 'c'
#: Busy status for invalid operand
STATUS_BUSY_INVALID_OPERAND = 'C'
#: Idle status for EEPROM failure
STATUS_IDLE_EEPROM_FAILURE = 'f'
#: Busy status for EEPROM failure
STATUS_BUSY_EEPROM_FAILURE = 'F'
#: Idle status for pump not initialized
STATUS_IDLE_NOT_INITIALIZED = 'g'
#: Busy status for pump not initialized
STATUS_BUSY_NOT_INITIALIZED = 'G'
#: Idle status for plunger overload error
STATUS_IDLE_PLUNGER_OVERLOAD = 'i'
#: Busy status for plunger overload error
STATUS_BUSY_PLUNGER_OVERLOAD = 'I'
#: Idle status for valve overload error
STATUS_IDLE_VALVE_OVERLOAD = 'j'
#: Busy status for plunger overload error
STATUS_BUSY_VALVE_OVERLOAD = 'J'
#: Idle status for plunger not allowed to move
STATUS_IDLE_PLUNGER_STUCK = 'k'
#: Busy status for plunger not allowed to move
STATUS_BUSY_PLUNGER_STUCK = 'K'

ERROR_STATUSES_IDLE = (STATUS_IDLE_INIT_FAILURE, STATUS_IDLE_INVALID_COMMAND, STATUS_IDLE_INVALID_OPERAND,
                       STATUS_IDLE_EEPROM_FAILURE, STATUS_IDLE_NOT_INITIALIZED, STATUS_IDLE_PLUNGER_OVERLOAD,
                       STATUS_IDLE_VALVE_OVERLOAD, STATUS_IDLE_PLUNGER_STUCK)
ERROR_STATUSES_BUSY = (STATUS_BUSY_INIT_FAILURE, STATUS_BUSY_INVALID_COMMAND, STATUS_BUSY_INVALID_OPERAND,
                       STATUS_BUSY_EEPROM_FAILURE, STATUS_BUSY_NOT_INITIALIZED, STATUS_BUSY_PLUNGER_OVERLOAD,
                       STATUS_BUSY_VALVE_OVERLOAD, STATUS_BUSY_PLUNGER_STUCK)


class C3000Protocol(object):
    """
    This class is used to represent the protocol which the pumps will follow when controlled.

    Args:
        address (str): Address of the pump.

    """
    def __init__(self, address):
        self.logger = create_logger(self.__class__.__name__)

        self.address = address

    def forge_packet(self, dtcommands, execute=True):
        """
        Creates a packet which will be sent to the device.

        Args:
            dtcommands (list): List of dtcommands.

            execute (bool): Sets the execute value, True by default.

        Returns:
            DTInstructionPacket: The packet created.

        """
        self.logger.debug("Forging packet with {} and execute set to {}".format(dtcommands, execute))
        if type(dtcommands) == dtprotocol.DTCommand:
            dtcommands = [dtcommands]
        if execute:
            dtcommands.append(dtprotocol.DTCommand(CMD_EXECUTE))
        return dtprotocol.DTInstructionPacket(self.address, dtcommands)

    # handling answers
    def decode_packet(self, dtresponse):
        """
        Decodes the response packet form the device.

        Args:
            dtresponse (str): The response from the device.

        Returns:
            DTStatus: The decoded status of the device.

        """
        return dtprotocol.DTStatus(dtresponse).decode()

    """

    .. note:: The following functions should be generated automatically but not necessary as of yet.

    .. todo:: Generate these functions automatically.

    """

    # the functions below should be generated automatically but not really needed for now

    def forge_initialize_valve_right_packet(self, operand_value=0):
        """
        Creates a packet for initialising the right valve.

        Args:
            operand_value (int): The value of the supplied operand, 0 by default.

        Returns:
            DTInstructionPacket: The packet created for initialising the right valve.

        """
        dtcommand = dtprotocol.DTCommand(CMD_INITIALIZE_VALVE_RIGHT, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_initialize_valve_left_packet(self, operand_value=0):
        """
        Creates a packet for initialising the left valve.

        Args:
            operand_value (int): The value of the supplied operand, 0 by default.

        Returns:
            DTInstructionPacket: The packet created for initialising the left valve.

        """
        dtcommand = dtprotocol.DTCommand(CMD_INITIALIZE_VALVE_LEFT, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_initialize_no_valve_packet(self, operand_value=0):
        """
        Creates a packet for initialising with no valves.

        Args:
            operand_value (int): The value of the supplied operand, 0 by default.

        Returns:
            DTInstructionPacket: The packet created for initialising with no valves.

        """
        dtcommand = dtprotocol.DTCommand(CMD_INITIALIZE_NO_VALVE, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_initialize_valve_only_packet(self, operand_string=None):
        """
        Creates a packet for initialising with valves only.

        Args:
            operand_string (str): String representing the operand, None by default

        Returns:
            DTInstructionPacket: The packet created for initialising with valves only

        """
        dtcommand = dtprotocol.DTCommand(CMD_INITIALIZE_VALVE_ONLY, operand_string)
        return self.forge_packet(dtcommand)

    def forge_microstep_mode_packet(self, operand_value):
        """
        Creates a packet for initialising microstep mode.

        Args:
            operand_value (int): The value of the supplied operand.

        Returns:
            DTInstructionPacket: The packet created for initialising microstep mode.

        """
        if operand_value not in list(range(3)):
            raise ValueError('Microstep operand must be in [0-2], you entered {}'.format(operand_value))
        dtcommand = dtprotocol.DTCommand(CMD_MICROSTEPMODE, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_move_to_packet(self, operand_value):
        """
        Creates a packet for moving the device to a location.

        Args:
            operand_value (int): The value of the supplied operand.

        Returns:
            DTInstructionPacket: The packet created for moving the device to a location.

        """
        dtcommand = dtprotocol.DTCommand(CMD_MOVE_TO, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_pump_packet(self, operand_value):
        """
        Creates a packet for the pump action of the device.

        Args:
            operand_value (int): The value of the supplied operand

        Returns:
            DTInstructionPacket: The packet created for the pump action of the device.

        """
        dtcommand = dtprotocol.DTCommand(CMD_PUMP, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_deliver_packet(self, operand_value):
        """
        Creates a packet for delivering the payload.

        Args:
            operand_value (int): The value of the supplied operand.

        Returns:
            DTInstructionPacket: The packet created for delivering the payload.

        """
        dtcommand = dtprotocol.DTCommand(CMD_DELIVER, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_top_velocity_packet(self, operand_value):
        """
        Creates a packet for the top velocity of the device.

        Args:
            operand_value (int): The value of the supplied operand.

        Returns:
            DTInstructionPacket: The packet created for the top velocity of the device.

        """
        dtcommand = dtprotocol.DTCommand(CMD_TOPVELOCITY, str(int(operand_value)))
        return self.forge_packet(dtcommand)

    def forge_eeprom_config_packet(self, operand_value):
        """
        Creates a packet for accessing the EEPROM configuration of the device.

        Args:
            operand_value (int): The value of the supplied operand.

        Returns:
            DTInstructionPacket: The packet created for accessing the EEPROM configuration of the device.

        """
        dtcommand = dtprotocol.DTCommand(CMD_EEPROM_CONFIG, str(operand_value))
        return self.forge_packet(dtcommand, execute=False)

    def forge_eeprom_lowlevel_config_packet(self, sub_command=20, operand_value="pycont1"):
        """
        Creates a packet for accessing the EEPROM configuration of the device.

        Args:
            sub_command (int):  Sub-command value (0-20)
            operand_value (str): The value of the supplied operand.

        Returns:
            DTInstructionPacket: The packet created for accessing the EEPROM configuration of the device.

        """

        dtcommand = dtprotocol.DTCommand(CMD_EEPROM_LOWLEVEL_CONFIG, str(sub_command) + "_" + str(operand_value))
        return self.forge_packet(dtcommand, execute=False)

    def forge_valve_input_packet(self):
        """
        Creates a packet for the input into a valve on the device.

        Returns:
            DTInstructionPacket: The packet created for the input into a valve on the device.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_VALVE_INPUT))

    def forge_valve_output_packet(self):
        """
        Creates a packet for the output from a valve on the device.

        Returns:
            DTInstructionPacket: The packet created for the output from a valve on the device.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_VALVE_OUTPUT))

    def forge_valve_bypass_packet(self):
        """
        Creates a packet for bypassing a valve on the device.

        Returns:
            DTInstructionPacket: The packet created for bypassing a valve on the device.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_VALVE_BYPASS))

    def forge_valve_extra_packet(self):
        """
        Creates a packet for an extra valve.

        Returns:
            DTInstructionPacket: The packet created for an extra valve.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_VALVE_EXTRA))

    def forge_valve_6way_packet(self, valve_position):
        """
        Creates a packet for the 6way valve on the device.

        Returns:
            DTInstructionPacket: The packet created for the input into a valve on the device.

        """
        return self.forge_packet(dtprotocol.DTCommand('{}{}'.format(CMD_VALVE_INPUT, valve_position)))

    def forge_report_status_packet(self):
        """
        Creates a packet for reporting the device status.

        Returns:
            DTInstructionPacket: The packet created for reporting the device status.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_STATUS))

    def forge_report_plunger_position_packet(self):
        """
        Creates a packet for reporting the device's plunger position.

        Returns:
            DTInstructionPacket: The packet created for reporting the device's plunger position.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_PLUNGER_POSITION))

    def forge_report_start_velocity_packet(self):
        """
        Creates a packet for reporting the device's start velocity.

        Returns:
            DTInstructionPacket: The packet created for reporting the device's starting velocity.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_START_VELOCITY))

    def forge_report_peak_velocity_packet(self):
        """
        Creates a packet for reporting the device's peak velocity.

        Returns:
            DTInstructionPacket: The packet created for reporting the device's peak velocity.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_PEAK_VELOCITY))

    def forge_report_cutoff_velocity_packet(self):
        """
        Creates a packet for reporting the device's cutoff velocity.

        Returns:
            DTInstructionPacket: The packet created for reporting the device's cutoff velocity.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_CUTOFF_VELOCITY))

    def forge_report_valve_position_packet(self):
        """
        Creates a packet for reporting the device's valve position.

        Returns:
            DTInstructionPacket: The packet created for reporting the device's valve position.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_VALVE_POSITION))

    def forge_report_initialized_packet(self):
        """
        Creates a packet for reporting the initialisation of the device.

        Returns:
            DTInstructionPacket: The packet created for reporting the initialisation of the device.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_INTIALIZED))

    def forge_report_eeprom_packet(self):
        """
        Creates a packet for reporting the EEPROM.

        Returns:
            The packet for reporting the EEPROM.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_EEPROM))

    def forge_report_jumper_packet(self):
        """
        Creates a packet for reporting the position of Jumper 2-5, used in 3-way Y-valves.

        Returns:
            The packet for reporting the EEPROM.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_JUMPER_3WAY))

    def forge_terminate_packet(self):
        """
        Creates the data packet for terminating the current command

        Returns:
            The packet for terminating any running command.

        """
        return self.forge_packet(dtprotocol.DTCommand(CMD_TERMINATE))
