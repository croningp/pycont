# -*- coding: utf-8 -*-

import itertools


DTStart = '/'
DTStop = '\r'


class DTInstructionPacket(object):
    """ This class is used to represent a DT instruction packet.

        Args:
            address (str): The address to talk to
            dtcommands (list): List of DTCommand

        (for more details see http://www.tricontinent.com/products/cseries-syringe-pumps)
        """

    def __init__(self, address, dtcommands):
        self.address = address.encode()
        self.dtcommands = dtcommands

    def to_array(self):
        commands = ''.encode()
        for dtcommand in self.dtcommands:
            commands += dtcommand.to_string()
        return bytearray(itertools.chain(DTStart.encode(),
                                         self.address,
                                         commands,
                                         DTStop.encode(), ))

    def to_string(self):
        return bytes(self.to_array())


class DTCommand(object):

    """ This class is used to represent a DTcommand.

        Args:
            command (str): The command to be sent
            operand (str): The parameter of the command, None by default

        (for more details see http://www.tricontinent.com/products/cseries-syringe-pumps)
        """

    def __init__(self, command, operand=None):
        self.command = command.encode()
        if operand is not None:
            self.operand = operand.encode()
        else:
            self.operand = None

    def to_array(self):
        if self.operand is None:
            chain = itertools.chain(self.command)
        else:
            chain = itertools.chain(self.command, self.operand)
        return bytearray(chain)

    def to_string(self):
        return bytes(self.to_array())


class DTStatus(object):

    """ This class is used to represent a DTstatus, the response of the device from a command.

        Args:
            response (str): The response from the device

        (for more details see http://www.tricontinent.com/products/cseries-syringe-pumps)
        """

    def __init__(self, response):
        self.response = response.decode()

    def decode(self):
        info = self.response.rstrip().rstrip('\x03').lstrip(DTStart)
        address = info[0]
        status = info[1]
        data = info[2:]
        return (address, status, data)
