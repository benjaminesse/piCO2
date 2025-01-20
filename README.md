# piCO2
Raspberry Pi based CO2 sensor

## Setup
On a fresh Raspberry Pi (bookworm) install, follow these steps.

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
