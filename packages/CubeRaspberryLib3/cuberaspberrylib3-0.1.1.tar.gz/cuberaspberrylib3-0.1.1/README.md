# CubeRaspberryLib3

CubeRaspberryLib driver adapted to Python 3 version.

**This is a personal project and has nothing to do with any commercial activity.**

## Preparation

Please check if there is any `i2c-*` device in `/dev`. If not, please use `raspi-config`->`3 Interface Options`->`I5 I2C` to enable it.

## Installation

### Developer Local Installation

```
pip install -e .
```

### Normal installation

```
pip install .
```

## Examples

```python3
from CubeRaspberryLib3 import Cube
cube = Cube(i2c_bus_number=1)
cube.set_fan(0)
```
