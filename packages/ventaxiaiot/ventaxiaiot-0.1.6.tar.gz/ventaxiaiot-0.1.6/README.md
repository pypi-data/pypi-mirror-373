# ventaxiaiot

An async Python library to comunicate with the Wifi module of the Vent Axia Sentinel Kinetic Advance S. It was [reverse engineering using the Vent Axia Connect App](https://github.com/JosyBan/ventaxiaiot/blob/main/background.md)



This is an early release and **under active development**, so use at your own risk.


> [!IMPORTANT]
> ## Disclaimer
> This project is a community-developed integration and **not officially affiliated with or supported by Vent-Axia**. 
> Functionality may break at any time if the Vent-Axia API changes without warning.
> All reverse engineering was performed for interoperability purposes only.
> No proprietary binaries or copyrighted material are distributed.



## Installation

The easiest method is to install using pip (`pip`/`pip3`):

```bash
pip install ventaxiaiot
```


Installing within a [Python virtual environment](https://docs.python.org/3/library/venv.html) is recommended:


```bash
python -m venv .venv
source .venv/bin/activate
pip install ventaxiaiot
```

To upgrade  to the latest version:

```bash
pip install --upgrade ventaxiaiot
```

## Features
> Connects securely to VentAxia devices using native TLS-PSK cipher suites
> 
> Fully async Python client with message parsing and event handling
> 
> Automatic reconnect and robust error handling
> 
> Home Assistant integration with sensors for exhaust/supply airflow, humidity, and device status
> 
> CLI tool for manual testing and debugging
> 
> Logs detailed connection and message flow for troubleshooting


## Running as CLI.


```bash
cli.py status 
```

Configuration file will be searched for in `./.config.json` 

### Example configuration file

```config.json
{
  "host": "host-ip",
  "port": 0,
  "identity": "secert-id",
  "psk_key": "device-wifi-password",
  "wifi_device_id": "your-device-model"
}
```
