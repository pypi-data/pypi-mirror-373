# EKSMA Optics Motorized Devices

[![PyPI - Version](https://img.shields.io/pypi/v/eksma-optics-motorized-devices.svg)](https://pypi.org/project/eksma-optics-motorized-devices)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/eksma-optics-motorized-devices.svg)](https://pypi.org/project/eksma-optics-motorized-devices)

A library for controlling EKSMA Optics motorized devices.

## Getting Started

### Installation

```shell
pip install eksma-optics-motorized-devices[standard]
```

### Usage

```python
from eksma_optics_motorized_devices.control import Control
from eksma_optics_motorized_devices.transport import SerialTransport

# Initialize the serial transport with the appropriate serial port
transport = SerialTransport(port="/dev/ttyUSB0")  # Replace with your actual port

# Create a Control instance using the transport
device = Control(transport)

# Query the device identification
try:
    identification = device.get_identification()
    print("Device Identification:", identification)
except Exception as e:
    print("Failed to get identification:", e)
```

## License

MIT
