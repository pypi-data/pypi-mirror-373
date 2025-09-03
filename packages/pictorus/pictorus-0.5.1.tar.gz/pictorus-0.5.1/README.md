# Pictorus Device Manager

Python library for managing pictorus apps on devices

## Development

We use [Flit](https://flit.pypa.io/en/stable/index.html) for package management

### Setup

Run `./script/setup` to setup your dev environment

### Tests

Run `pytest` from the root directory

### Releasing

1. Update the package version in the package init [src/pictorus/\_\_init\_\_.py](src/pictorus/__init__.py)
1. Run `flit publish`
   - If you want to publish to the test PyPi repository, use `FLIT_INDEX_URL=https://test.pypi.org/legacy/ flit publish`
   - Credentials are in 1password.

## Installation

### Local

You can install locally by running `flit install`

### Remote device

Install the latest release on your device `ssh <host> "sudo pip3 install pictorus"`
For Test: `sudo pip install -i https://test.pypi.org/simple/ pictorus`

To install a local version for testing:

1. `flit build`
1. SCP the resulting wheel to your device: `scp dist/pictorus-<version>-py3-none-any.whl <host>:/tmp/`
1. Pip install the wheel on your device `ssh <host> "sudo pip3 install --force-reinstall /tmp/pictorus-<version>-py3-none-any.whl --break-system-packages"`

## Usage

Installing the package will place a `pictorus-cli` bin in the systems $PATH. Run `sudo pictorus-cli --help` to see available commands

To configure, run `sudo PICTORUS_ENV=<test | prod> pictorus-cli configure`

This should also automatically set up `pictorus-device-manager` to run using systemd.
