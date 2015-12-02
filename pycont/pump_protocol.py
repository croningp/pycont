# -*- coding: utf-8 -*-
import logging
module_logger = logging.getLogger(__name__)

import dtprotocol

CMD_EXECUTE = 'R'
CMD_INITIALIZE_VALVE_RIGHT = 'Z'
CMD_INITIALIZE_VALVE_LEFT = 'Y'
CMD_INITIALIZE_NO_VALVE = 'W'
CMD_MICROSTEPMODE = 'N'
CMD_MOVE_TO = 'A'
CMD_PUMP = 'P'
CMD_DELIVER = 'D'
CMD_TOPVELOCITY = 'V'
CMD_EEPROM_CONFIG = 'U'      # Requires power restart to take effect     [donk]

CMD_VALVE_INPUT = 'I'       # Depending on EEPROM settings (U4 or U11) 4-way distribution valves either use IOBE or I<n>O<n>     [donk]
CMD_VALVE_OUTPUT = 'O'
CMD_VALVE_BYPASS = 'B'
CMD_VALVE_EXTRA = 'E'

CMD_REPORT_STATUS = 'Q'
CMD_REPORT_PLUNGER_POSITION = '?'
CMD_REPORT_START_VELOCITY = '?1'
CMD_REPORT_PEAK_VELOCITY = '?2'
CMD_REPORT_CUTOFF_VELOCITY = '?3'
CMD_REPORT_VALVE_POSITION = '?6'
CMD_REPORT_INTIALIZED = '?19'
CMD_REPORT_EEPROM = '?27'

STATUS_IDLE_ERROR_FREE = '`'
STATUS_BUSY_ERROR_FREE = '@'


class C3000Protocol(object):

    def __init__(self, address):
        self.logger = logging.getLogger(self.__class__.__name__)

        self.address = address

    def forge_packet(self, dtcommands, execute=True):
        if type(dtcommands) == dtprotocol.DTCommand:
            dtcommands = [dtcommands]
        if execute:
            dtcommands.append(dtprotocol.DTCommand(CMD_EXECUTE))
        return dtprotocol.DTInstructionPacket(self.address, dtcommands)

    # handling answers
    def decode_packet(self, dtresponse):
        return dtprotocol.DTStatus(dtresponse).decode()

    # the functions below should be generated automatically but not really  needed for now

    def forge_initialize_valve_right_packet(self, operand_value=0):
        dtcommand = dtprotocol.DTCommand(CMD_INITIALIZE_VALVE_RIGHT, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_initialize_valve_left_packet(self, operand_value=0):
        dtcommand = dtprotocol.DTCommand(CMD_INITIALIZE_VALVE_LEFT, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_initialize_no_valve_packet(self, operand_value=0):
        dtcommand = dtprotocol.DTCommand(CMD_INITIALIZE_VALVE_LEFT, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_microstep_mode_packet(self, operand_value):
        if operand_value not in range(3):
            raise ValueError('Microstep operand must be in [0-2], you entered {}'.format(operand_value))
        dtcommand = dtprotocol.DTCommand(CMD_MICROSTEPMODE, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_move_to_packet(self, operand_value):
        dtcommand = dtprotocol.DTCommand(CMD_MOVE_TO, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_pump_packet(self, operand_value):
        dtcommand = dtprotocol.DTCommand(CMD_PUMP, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_deliver_packet(self, operand_value):
        dtcommand = dtprotocol.DTCommand(CMD_DELIVER, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_top_velocity_packet(self, operand_value):
        dtcommand = dtprotocol.DTCommand(CMD_TOPVELOCITY, str(operand_value))
        return self.forge_packet(dtcommand)

    def forge_eeprom_config_packet(self, operand_value):
        dtcommand = dtprotocol.DTCommand(CMD_EEPROM_CONFIG, str(operand_value))
        return self.forge_packet(dtcommand, execute=False)

    def forge_valve_input_packet(self, operand_value=None):
        if operand_value:
            dtcommand = dtprotocol.DTCommand(CMD_VALVE_INPUT, str(operand_value))
        else:
            dtcommand = dtprotocol.DTCommand(CMD_VALVE_INPUT)
        return self.forge_packet(dtcommand)

    def forge_valve_output_packet(self, operand_value=None):
        if operand_value:
            dtcommand = dtprotocol.DTCommand(CMD_VALVE_OUTPUT, str(operand_value))
        else:
            dtcommand = dtprotocol.DTCommand(CMD_VALVE_OUTPUT)
        return self.forge_packet(dtcommand)

    def forge_valve_bypass_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_VALVE_BYPASS))

    def forge_valve_extra_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_VALVE_EXTRA))

    def forge_report_status_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_STATUS))

    def forge_report_plunger_position_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_PLUNGER_POSITION))

    def forge_report_start_velocity_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_START_VELOCITY))

    def forge_report_peak_velocity_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_PEAK_VELOCITY))

    def forge_report_cutoff_velocity_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_CUTOFF_VELOCITY))

    def forge_report_valve_position_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_VALVE_POSITION))

    def forge_report_initialized_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_INTIALIZED))

    def forge_report_eeprom_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_REPORT_EEPROM))
