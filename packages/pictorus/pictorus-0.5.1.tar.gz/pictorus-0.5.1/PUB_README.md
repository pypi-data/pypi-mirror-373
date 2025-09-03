# Pictorus Device Manager
Python library for managing devices connected to a [Pictorus](https://pictor.us) account

## Installation
`sudo pip3 install pictorus`

Note: The package is installed/run using `sudo` so it can create and manage the required systemd services on your machine. You can install/run without `sudo`. This will still let you register your device, but you may need to manually configure `pictorus-device-manager` to run using your preferred process manager.

## Usage
Run `sudo pictorus-cli --help` to see available commands

### Configure
```
sudo pictorus-cli configure
```
This allows you to register the current device with your pictorus account, and sets up `pictorus-device-manager` to run as a systemd process.
