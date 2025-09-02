# CubeRaspberryLib3

CubeRaspberryLib driver adapted to Python 3 version.

**This is a personal project and has nothing to do with any commercial activity.**

## Preparation

Please check if there is any `i2c-*` device in `/dev`. If not, please use `raspi-config`->`3 Interface Options`->`I5 I2C` to enable it.

## Installation

### Developer Local Installation

Download the source file from [here](https://github.com/rikonaka/CubeRaspberryLib3)

```bash
pip install -e .
```

### Normal installation

```bash
pip install CubeRaspberryLib3
```

## Examples

```python3
from CubeRaspberryLib3 import Cube
cube = Cube(i2c_bus_number=1)
cube.set_fan(0)
```
