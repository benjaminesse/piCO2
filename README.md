# piCO2

Raspberry Pi based CO2 sensor

## Setup

On a fresh Raspberry Pi (bookworm) install, follow these steps. Note that the username should be `lava` and the hostname should be `picarbon`. These can be set when writing the SD card using the Raspberry Pi imager.

Clone this repository and enter it

```
git clone https://github.com/benjaminesse/piCO2
cd piCO2
```

Create a virtual environment and activate it

```
python -m venv venv
source venv/bin/activate
```

Install the required libraries

```
pip install numpy pandas plotly dash dash-bootstrap-components adafruit-circuitpython-scd4x gunicorn
```

Active I2C connections from the terminal using

```
sudo raspi-config
```

and navigating to `5 Interfacing Options` and then `P5 I2C`. Alternatively this can be done from the desktop through Menu > Preferences > Raspberry Pi Configuration > Interfaces.

Setup the WiFi hotspot (from https://www.raspberryconnect.com/projects/65-raspberrypi-hotspot-accesspoints/203-automated-switching-accesspoint-wifi-network)

```
curl "https://www.raspberryconnect.com/images/scripts/AccessPopup.tar.gz" -o AccessPopup.tar.gz
tar -xvf ./AccessPopup.tar.gz
cd AccessPopup
sudo ./installconfig.sh
```

Add the following lines to crontab to run on startup

```
@reboot cd /home/lava/piCO2/ && . venv/bin/activate && python run_sensor.py
@reboot cd /home/lava/piCO2/ && . venv/bin/activate && gunicorn -w 4 -b 0.0.0.0:4000 app:server -D --log-file=gunicorn.log
```

Now you should be able to connect to the network (named AccessPoint).

## Connecting

You can conect to the Pi over its WiFi network using ssh:

```
ssh lava@192.168.50.5
```

To view the webpage of the Pi open a browser and go to `http://192.168.50.5:4000`. Note that it can take some time to load, and only one connection should be applied at once!
