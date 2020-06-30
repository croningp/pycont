# -*- coding: utf-8 -*-

import itertools
from typing import List, Tuple, Optional

from ._logger import create_logger

DTStart = '/'
DTStop = '\r'


class DTCommand(object):

    """ This class is used to represent a DTcommand.

        Args:
            command: The command to be sent

            operand: The parameter of the command, None by default

        (for more details see http://www.tricontinent.com/products/cseries-syringe-pumps)
        """

    def __init__(self, command: str, operand: str = None):
        self.command = command.encode()
        if operand is not None:
            self.operand = operand.encode()
        else:
            self.operand = None  # type: ignore

    def to_array(self) -> bytearray:
        if self.operand is None:
            chain = itertools.chain(self.command)
        else:
            chain = itertools.chain(self.command, self.operand)
        return bytearray(chain)

    def to_string(self) -> bytes:
        return bytes(self.to_array())

    def __str__(self):
        return "command: " + str(self.command.decode()) + " operand: " + str(self.operand)


class DTInstructionPacket:
    """ This class is used to represent a DT instruction packet.

        Args:
            address: The address to talk to

            dtcommands: List of DTCommand

        (for more details see http://www.tricontinent.com/products/cseries-syringe-pumps)
        """

    def __init__(self, address: str, dtcommands: List[DTCommand]):
        self.address = address.encode()
        self.dtcommands = dtcommands

    def to_array(self) -> bytearray:
        commands = ''.encode()
        for dtcommand in self.dtcommands:
            commands += dtcommand.to_string()
        return bytearray(itertools.chain(DTStart.encode(),
                                         self.address,
                                         commands,
                                         DTStop.encode(), ))

    def to_string(self) -> bytes:
        return bytes(self.to_array())


class DTStatus(object):
    """ This class is used to represent a DTstatus, the response of the device from a command.

        Args:
            response: The response from the device

        (for more details see http://www.tricontinent.com/products/cseries-syringe-pumps)
        """

    def __init__(self, response: bytes):
        self.logger = create_logger(self.__class__.__name__)
        try:
            self.response = response.decode()
        except UnicodeDecodeError:
            self.logger.debug('Could not decode  {!r}'.format(response))
            self.response = None  # type: ignore

    def decode(self) -> Optional[Tuple[str, str, str]]:
        if self.response is not None:
            info = self.response.rstrip().rstrip('\x03').lstrip(DTStart)
            address = info[0]
            # try:
            status = info[1]
            data = info[2:]
            # except IndexError:
            #     return None
            return address, status, data
        else:
            return None
