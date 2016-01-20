
# have two pump plugged with switch at 0 and 1

import pycont.controller

io = pycont.controller.PumpIO('/dev/ttyUSB0')

p1 = pycont.controller.C3000Controller(io, 'test', '1', 5)
p1.smart_initialize()

p2 = pycont.controller.C3000Controller(io, 'test2', '2', 5)
p2.smart_initialize()
