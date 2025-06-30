from pyModbusTCP.client import ModbusClient
from program_recipe import data
import time

class FlackTekBallMillDriver(ModbusClient):
    """
    FlackTek ball mill driver.

    This class permits the control of a FlackTek ball mill. The following functionality is implemented:
        - Parse device status
        - Open and close lid
        - Load, start and stop a program
        - Error resetting

    To program the ball mill, pass a configuration dataclass as defined in program_recipe.py.

    Important: The class instance must be closed by calling `close()` when you are done with it. Alternatively,
    use it as a context manager to automatically  call `close()`, as in the example below.

    # Example use:
    ```
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
    """

    def __init__(self, host, port, unit_id=1, auto_open=True, timeout=5.0):
        """
        Initialize the superclass ModbusClient. Refer to that class for documentation on how to instantiate.
        """
        super().__init__(host=host, port=port, unit_id=unit_id, auto_open=auto_open, timeout=timeout)

    def load_program_and_run_cycle(self, prog_info):
        """
        Load the program, check if machine is ready, start the cycle, and wait for cycle to end.
        Args:
            prog_info: Program recipe containing the program to run

        Returns:
            status: Dictionary of status bits as returned from parse_status(). Optionally None if the machine is
                not ready to run.
        """
        self._load_name(prog_info)
        program_return = self.load_program(prog_info)
        print(f'\tMix Name: [{prog_info.mix_name}]\n'
              f'\tSpeeds: {program_return[0]}\n'
              f'\tTimes: {program_return[1]}\n')
        time.sleep(.25)

        if self.parse_status(prog_info)['ready_to_run'] == '0':
            print('Machine is not ready to run.')
            return

        self.start_cycle()
        time.sleep(.5)

        # while the ball_mill is running AND there is no error status is printed every 0.5 sec
        status = self.parse_status(prog_info)
        while status['mixer_error'] == '0' and status['mixer_running'] == '1':
            time.sleep(.5)
            status = self.parse_status(prog_info)
            print(status)

        # it exits while loop EITHER it stops running (in a normal way) OR there is an error
        # reset error must be run if status indicates that there is an error
        return status

    def parse_status(self, prog_info):
        """
        Read register 3100 and return the result as a dictionary of status bits.

        Args:
            prog_info: Program recipe containing the program to run

        Returns:
            status : Dictionary of status bits. Keys include 'robot_at_home', 'lid_closed', etc.
        """
        prog_info.feedback['machine_status'] = self.read_holding_registers(3100, 1)
        bin_status = list(bin(prog_info.feedback['machine_status'][0])[2:])  # Convert the decimal number to binary
        if len(bin_status) < 8:  # Check if the binary number is less than 8 bits, if so, add leading zeros
            bin_status = ['0'] * (8 - len(bin_status)) + bin_status
        status = {'robot_at_home': bin_status[0],
                  'na': bin_status[1],
                  'safety_ok': bin_status[2],
                  'lid_closed': bin_status[3],
                  'lid_open': bin_status[4],
                  'mixer_error': bin_status[5],
                  'mixer_running': bin_status[6],
                  'ready_to_run': bin_status[7]}
        return status

    def load_program(self, prog_info):
        """
        Loads a program to run.

        Args:
            prog_info: Program recipe containing the program to run

        Returns:
            speeds : A list of the speeds that were programmed
            times  : A list of the times for each speed that were programmed
        """
        print("Loading program...")
        # Setpoints
        speeds = [i for i in prog_info.speeds.values()]
        times = [i for i in prog_info.times.values()]

        # Proram Options
        accel = [prog_info.options['acceleration']]
        decel = [prog_info.options['deceleration']]

        # Write all to Mixer
        self.write_multiple_registers(3013, speeds)
        self.write_multiple_registers(3023, times)
        self.write_multiple_registers(3043, accel)
        self.write_multiple_registers(3044, decel)

        self._load()
        print("Program loaded.")

        return speeds, times

    def start_cycle(self):
        """
        Starts the machine cycle.
        """
        print("Starting cycle...")
        self.write_multiple_registers(3053, [100])
        self._load()
        return

    def stop_cycle(self):
        """
        Stops the machine cycle.
        """
        print("Stopping cycle...")
        self.write_multiple_registers(3053, [200])
        self._load()
        return

    def open_lid(self, prog_info):
        """
        Opens the lid.
        """
        print("Opening lid...")
        self.write_multiple_registers(3053, [50])
        self._load()

        # check if the lid is open every 0.5 sec for 10 sec
        # if ['lid_open'] == '0' for 10 sec, time outs. The OSError is displayed
        # it only exists while loop if ['lid_open'] == '1' which means the lid is open
        timeout = 10
        start_time = time.time()
        while self.parse_status(prog_info)['lid_open'] == '0':
            time.sleep(0.5)

            time_since_command = time.time() - start_time
            if time_since_command > timeout:
                raise OSError("Lid opening timed out.")

        print("Lid open!")
        return

    def close_lid(self, prog_info):
        """
        Closes the lid.
        """
        print("Closing lid...")
        self.write_multiple_registers(3053, [75])
        self._load()

        # check if the lid is close every 0.5 sec for 10 sec
        # if ['lid_close'] == '0' for 10 sec, time outs. The OSError is displayed
        # it only exists while loop if ['lid_close'] == '1' which means the lid is close
        timeout = 10
        start_time = time.time()
        while self.parse_status(prog_info)['lid_closed'] == '0':
            time.sleep(0.5)

            time_since_command = time.time() - start_time
            if time_since_command > timeout:
                raise OSError("Lid closing timed out.")

        print("Lid closed!")
        return

    # Keeps the connection alive and returns the machine status
    # It has not yet been necessary to use this method, but it is kept for the future.
    def keep_alive(self, prog_info):
        # Read register 3100 and return to feedback {machine_status}
        prog_info.feedback['speed'] = self.read_holding_registers(3101, 1)
        prog_info.feedback['position'] = self.read_holding_registers(3102, 1)
        prog_info.feedback['vacuum_lid'] = self.read_holding_registers(3103, 1)
        return prog_info.feedback

    def reset_error(self):
        """
        Resets the machine error.
        """
        print("Resetting error...")
        self.write_multiple_registers(3053, [300])
        time.sleep(.25)
        self._load()
        return

    def _load(self):
        self.write_multiple_registers(3053, [0])
        time.sleep(.25)
        self.write_multiple_registers(3053, [1])
        time.sleep(.25)
        self.write_multiple_registers(3053, [0])
        return

    # Parses the mix name from a string to ASCII
    def _load_name(self, prog_info):
        name_hex = [int(''.join(list(reversed(list(hex(ord(prog_info.mix_name[i]))[2:] for i in range(j, j + 2))))), 16)
                    for j
                    in range(0, len(prog_info.mix_name), 2)]
        self.write_multiple_registers(3000, name_hex)
        self._load()
        return name_hex

if __name__ == "__main__":
    with FlackTekBallMillDriver(host='10.10.1.2', port=503) as ball_mill:
        ball_mill.close_lid(prog_info=data)
        mixer_status = ball_mill.load_program_and_run_cycle(prog_info=data)
        if mixer_status is None:
            exit()

        if mixer_status['mixer_running'] == '0':
            time.sleep(.5)
            print('Cycle is over.')
            ball_mill.open_lid(prog_info=data)
