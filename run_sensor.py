import os
import time
import board
import logging
import adafruit_scd4x
from datetime import datetime

try:
    with open('status.txt', 'w') as w:
        w.write('Connecting')

    # Get the start time
    now_time = datetime.now()

    # Set up logging
    logger = logging.getLogger(__name__)

    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    file_handler = logging.FileHandler(f"co2sensor.log", mode="a", encoding="utf-8")
    formatter = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s- %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Connect to the sensor
    i2c = board.I2C()
    scd4x = adafruit_scd4x.SCD4X(i2c)
    logger.info(f"Serial number: {[hex(i) for i in scd4x.serial_number]}")

    scd4x.self_calibration_enabled = False
    calib_flag = scd4x.self_calibration_enabled
    logger.info(f'Calibration enabled: {calib_flag}')

    logger.info('Running self test')
    print(scd4x.self_test())

    # Initialise measurements
    scd4x.start_periodic_measurement()
    logger.info("Waiting for first measurement....")

    # Ensure the results directory exists
    if not os.path.isdir('Results'):
        os.makedirs('Results')

    # Create the output file
    outfname = f'Results/{now_time.strftime("%Y%m%dT%H%M%S")}_co2.csv'
    with open(outfname, 'w') as w:
        w.write('Time,CO2 (ppm),Temperature (C),Humidity (%)\n')

    # Set infinite loop to read data
    while True:
        if scd4x.data_ready:
            with open('status.txt', 'w') as w:
                w.write('Measuring')
            with open(outfname, 'a') as w:
                w.write(
                    f'{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")},'
                    f'{scd4x.CO2},{scd4x.temperature},'
                    f'{scd4x.relative_humidity}\n'
                )
            logger.info("Measurement recieved")
        time.sleep(0.1)

except Exception:
    with open('status.txt', 'w') as w:
        w.write('Error')
    logger.error('Error encountered!', exc_info=True)
