# -*- coding: utf-8 -*-

import dtprotocol

CMD_EXECUTE = 'R'
CMD_INITIALIZE_RIGHT = 'Z'
CMD_MICROSTEPMODE = 'N'
CMD_MOVE_TO = 'A'
CMD_PUMP = 'P'
CMD_DELIVER = 'D'
CMD_TOPVELOCITY = 'V'

CMD_VALVE_INPUT = 'I'
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

STATUS_IDLE_ERROR_FREE = '`'
STATUS_BUSY_ERROR_FREE = '@'


class C3000Protocol(object):

    def __init__(self, address):
        self.address = address

    def forge_packet(self, dtcommands):
        if type(dtcommands) == dtprotocol.DTCommand:
            dtcommands = [dtcommands]
        dtcommands.append(dtprotocol.DTCommand(CMD_EXECUTE))
        return dtprotocol.DTInstructionPacket(self.address, dtcommands)

    # handling answers
    def decode_packet(self, dtresponse):
        return dtprotocol.DTStatus(dtresponse).decode()

    # the functions below should be generated automatically but not really  needed for now

    def forge_initialize_right_packet(self, operand_value=0):
        dtcommand = dtprotocol.DTCommand(CMD_INITIALIZE_RIGHT, str(operand_value))
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

    def forge_valve_input_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_VALVE_INPUT))

    def forge_valve_output_packet(self):
        return self.forge_packet(dtprotocol.DTCommand(CMD_VALVE_OUTPUT))

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
