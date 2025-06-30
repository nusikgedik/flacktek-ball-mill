class data:
    # 3000-3012 Mix Name ASCII 24 Bytes (12 Characters max)
    mix_name = 'Remote Test             '

    # 3043 & 3044 Acceleration / Deceleration.
    options = {'acceleration': 500,
               'deceleration': 500}

    # 3013-3022 Speeds in RPM
    speeds = {'speed1': 500,
              'speed2': 0,
              'speed3': 0,
              'speed4': 0,
              'speed5': 0,
              'speed6': 0,
              'speed7': 0,
              'speed8': 0,
              'speed9': 0,
              'speed10': 0}

    # 3023-3032 Times in Seconds
    times = {'time1': 30,
             'time2': 0,
             'time3': 0,
             'time4': 0,
             'time5': 0,
             'time6': 0,
             'time7': 0,
             'time8': 0,
             'time9': 0,
             'time10': 0}

    # 3033-3042 Vacuum in mmHg
    vacuum_setpoints = {'vacuum1': 0,
                        'vacuum2': 0,
                        'vacuum3': 0,
                        'vacuum4': 0,
                        'vacuum5': 0,
                        'vacuum6': 0,
                        'vacuum7': 0,
                        'vacuum8': 0,
                        'vacuum9': 0,
                        'vacuum10': 0}

    # Selected Vacuum Scale Unit (1 = Torr, 2 = mBar, 3 = inHg, 4 = PSIA)
    vacuum_scale = 4

    # Define instructions sent to machine
    instruction = {'program': 1,
                   'open': 50,
                   'close': 75,
                   'start_cycle': 100,
                   'secure_lid': 0,  # Set to 0 to disable | 150 to enable
                   'stop_cycle': 200,
                   'reset_error': 300,
                   'go_home': 400}

    # Store machine feedback to be called
    feedback = {'speed': 0,
                'position': 0,
                'vacuum_lid': 0}
