# flacktek-ball-mill
Python class for the remote control of FlackTek ball mill.

# Description
This module defines a class that establishes modbus communication with an FlackTek ball mill and permits basic control and readout of the ball mill. Control is implemented by reading and writing to registers as defined in the technical manual. 

# Typical use
```python
#Creating an instance of ball mill class as a context manager
with FlackTekBallMillDriver(host='10.10.1.2', port=503) as ball_mill:
    ball_mill.close_lid(prog_info=data)
    mixer_status = ball_mill.load_program_and_run_cycle(prog_info=data)
    if mixer_status is None:
        exit()

    if mixer_status['mixer_running'] == '0':
        time.sleep(.5)
        print('Cycle is over.')
        ball_mill.open_lid(prog_info=data)
```

# Features
The following functionality is implemented:
  - Parse device status
  - Open and close lid
  - Load, start and stop a program
  - Error resetting

