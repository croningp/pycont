## pycont

pycont is a python library to control Tricontinent C3000 pumps used in the Cronin Lab

It is meant to be easy to use, especially for understanding what is going on in your program.

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
        "name": "pump0",
        "switch": "0",
        "volume": 5,
        "micro_step_mode": 2,
        "top_velocity": 24000
      },
      {
          "name": "pump1",
          "switch": "1",
          "volume": 5,
          "micro_step_mode": 2,
          "top_velocity": 24000
      }
  ]
}
```