import os
import time
import board
import logging
import numpy as np
import adafruit_scd4x
from datetime import datetime
from gps import GPS
from subprocess import call

logger = logging.getLogger(__name__)

class CO2Sensor(object):
    
    def __init__(self, gps):
        
        # Set the i2c and GPS variables
        self.i2c = board.I2C()
        self.gps = gps
                
    def begin_reading_loop(self, file_n):
        
        # Check if GPS is connected
        if self.gps.connected:

            # Find the location and time
            ts, lat, lon, alt, gps_flag = self.gps.get_fix(30)
            
            # If fix is successful then set the time and location
            if gps_flag:
                logger.info(f'GPS fix found, updating system time to {ts}')
                tstr = ts.strftime('%Y-%m-%d %H:%M:%S')
                call(f'sudo date --set="{tstr}"', shell=True)
                logger.info(f'Latitude = {lat}, Longitude = {lon}, Altitude = {alt} m')

            # If no fix is found then default to the Pi time
            else:
                logger.warning('GPS fix failed, using Pi time')
                lat = lon = alt = np.nan
             
        # If not GPS is connected then use the Pi time
        else:
            logger.warning('No GPS, using Pi time')
            gps_flag = False
            lat = lon = alt = np.nan

        # Get the start time
        now_time = datetime.now()
        
        # Connect to the sensor
        self.connect()

        # Ensure the results directory exists
        if not os.path.isdir('Results'):
            os.makedirs('Results')

        # Create the output file
        outfname = f'Results/co2_data_{file_n+1}_{now_time.strftime("%Y%m%dT%H%M%S")}.csv'
        
        # Write the results file header
        with open(outfname, 'w') as w:
            w.write(
                f'Latitude,{lat}\nLongitude,{lon}\nAltitude,{alt} m\n'
            )
            w.write('Time,CO2 (ppm),Temperature (C),Humidity (%)\n')
        
        # Start the loop
        while True:
            
            # Try to take a measurement
            try:
                
                # Check the sensor is ready
                if self.scd4x.data_ready:
                    
                    # Get the time
                    ts = datetime.now()
                        
                    # Pull the CO2, temperature and humidity
                    co2 = self.scd4x.CO2
                    temp = self.scd4x.temperature
                    relhum = self.scd4x.relative_humidity
                    
                    # logger.info(f'CO2 = {co2} ppm')

                    # Update status
                    with open('status.txt', 'w') as w:
                        w.write('Measuring')
                        
                    # Write to the results file
                    with open(outfname, 'a') as w:
                        w.write(
                            f'{ts.strftime("%Y-%m-%dT%H:%M:%S")},'
                            f'{co2},{temp},{relhum}\n'
                        )
                time.sleep(0.1)
                
            # If something has gone wrong attempt to reconnect
            except Exception:
                self.connect()
            
    def connect(self):
        
        logger.info('Connecting to the CO2 sensor')
    
        with open('status.txt', 'w') as w:
            w.write('Connecting to sensor...')
        
        flag = False
        
        # Set 10 attempts
        for i in range(10):
            try:
                # Wait a second
                time.sleep(1)
                logger.info(f'Connection attempt {i+1}')
                
                # Try to connect
                self.scd4x = adafruit_scd4x.SCD4X(self.i2c)
                
                # Print the serial number
                logger.info(
                    f"Serial number: {[hex(i) for i in self.scd4x.serial_number]}"
                )
                
                # Set the sensor to be measuring
                self.scd4x.start_periodic_measurement()
                logger.info("Sensor measuring")
                flag = True
                break
                
            # Report errors
            except Exception as e:
                logger.warning(f'Connection failed!\n{e}')
                
        # Finally, if the connection fails too many times then raise
        if not flag:
            raise Exception('Unable to connect to sensor!')
                
# Overall code loop
if __name__ == '__main__':
    try:
        
        # Ensure the log directory exists
        if not os.path.isdir('log'):
            os.makedirs('log')

        file_n = len(os.listdir('log/'))

        # Set up logging
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(
            f"log/co2_log_{file_n+1}.log", mode="a", encoding="utf-8"
        )
        formatter = logging.Formatter(
            '%(asctime)s-%(name)s-%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        # Try to connect to the GPS
        with open('status.txt', 'w') as w:
            w.write('Waiting for GPS...')

        # Connect to GPS
        with open('status.txt', 'w') as w:
            w.write('Connecting to GPS...')
        logger.info('Connecting to GPS...')
        gps = GPS()

        # Connect to the sensor
        co2_sensor = CO2Sensor(gps)
        
        # Set infinite loop to read data
        co2_sensor.begin_reading_loop(file_n)

    # Report any error
    except Exception:
        with open('status.txt', 'w') as w:
            w.write('Error')
        logger.error('Error encountered!', exc_info=True)
