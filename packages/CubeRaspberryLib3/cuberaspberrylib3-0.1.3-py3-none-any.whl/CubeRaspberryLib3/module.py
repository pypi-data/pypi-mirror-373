import smbus2
import time


class Cube(object):
    def __init__(self, i2c_bus_number: int = 1, delay: float = 0.002):
        self.__delay = delay
        self.__i2c_bus_connection = smbus2.SMBus(i2c_bus_number)

        self.__i2c_addr = 0x0E
        self.__reg_fan = 0x08
        self.__reg_rgb_effect = 0x04
        self.__reg_rgb_speed = 0x05
        self.__reg_rgb_color = 0x06

    def __del__(self):
        print("Cube End!")

    def set_fan(self, state: int):
        """
        Control fan:
        start=0 close, start=1 open
        """

        if not isinstance(state, int):
            raise TypeError("state must be of type int")

        if state > 0:
            state = 1
        else:
            state = 0

        conn = self.__i2c_bus_connection
        i2c_addr = self.__i2c_addr
        reg_fan = self.__reg_fan
        delay = self.__delay

        try:
            conn.write_byte_data(i2c_addr, reg_fan, state)
            if delay > 0:
                time.sleep(delay)
        except Exception as e:
            print("set_fan failed: {}".format(e))

    def set_rgb_effect(self, effect: int):
        """
        Control RGB light effect:
        0 off effect, 1 breathing light, 2 marquee light, 3 rainbow light
        4 dazzling lights, 5 running water lights, 6 circulation breathing lights
        """

        if not isinstance(effect, int):
            raise TypeError("effect must be of type int")

        if effect < 0:
            effect = 0
        elif effect > 6:
            effect = 6

        conn = self.__i2c_bus_connection
        i2c_addr = self.__i2c_addr
        reg_rgb_effect = self.__reg_rgb_effect
        delay = self.__delay

        try:
            conn.write_byte_data(i2c_addr, reg_rgb_effect, effect)
            if delay > 0:
                time.sleep(delay)
        except Exception as e:
            print("set_rgb_effect failed: {}".format(e))

    def set_rgb_speed(self, speed: int):
        """
        Set RGB light effect speed:
        1 low speed, 2 medium speed, 3 high speed
        """

        if not isinstance(speed, int):
            raise TypeError("speed must be of type int")

        if speed < 1:
            speed = 1
        elif speed > 3:
            speed = 3

        conn = self.__i2c_bus_connection
        i2c_addr = self.__i2c_addr
        reg_rgb_speed = self.__reg_rgb_speed
        delay = self.__delay

        try:
            conn.write_byte_data(i2c_addr, reg_rgb_speed, speed)
            if self.delay > 0:
                time.sleep(delay)
        except Exception as e:
            print("set_rgb_peed failed: {}".format(e))

    def set_rbg_color(self, color: int):
        """
        Set RGB light effect color:
        0 red, 1 green, 2 blue, 3 yellow, 4 purple, 5 cyan, 6 white
        """

        if not isinstance(color, int):
            raise TypeError("color must be of type int")

        conn = self.__i2c_bus_connection
        i2c_addr = self.__i2c_addr
        reg_rgb_color = self.__reg_rgb_color
        delay = self.__delay

        if color < 0:
            color = 0
        elif color > 6:
            color = 6

        try:
            conn.write_byte_data(i2c_addr, reg_rgb_color, color)
            if delay > 0:
                time.sleep(delay)
        except Exception as e:
            print("set_rgb_color failed: {}".format(e))

    def set_single_color(self, index: int, r: int, g: int, b: int):
        """
        Set the individual RGB light color:
        index indicates the serial number of the lamp bead 0-13, index=255 means to control all lamps,
        r stands for red, g stands for green, and b stands for blue
        """

        if not isinstance(index, int):
            raise TypeError("index must be of type int")
        if not isinstance(r, int):
            raise TypeError("r must be of type int")
        if not isinstance(g, int):
            raise TypeError("g must be of type int")
        if not isinstance(b, int):
            raise TypeError("b must be of type int")

        conn = self.__i2c_bus_connection
        i2c_addr = self.__i2c_addr
        reg_rgb_effect = self.__reg_rgb_effect
        delay = self.__delay

        try:
            # Turn off RGB light effects
            conn.write_byte_data(i2c_addr, reg_rgb_effect, 0)
            if delay > 0:
                time.sleep(delay)
            conn.write_byte_data(i2c_addr, 0x00, index & 0xFF)
            if delay > 0:
                time.sleep(delay)
            conn.write_byte_data(i2c_addr, 0x01, r & 0xFF)
            if delay > 0:
                time.sleep(delay)
            conn.write_byte_data(i2c_addr, 0x02, g & 0xFF)
            if delay > 0:
                time.sleep(delay)
            conn.write_byte_data(i2c_addr, 0x03, b & 0xFF)
            if delay > 0:
                time.sleep(delay)
        except Exception as e:
            print("set_single_color failed: {}".format(e))

    def get_Version(self):
        """Obtain the firmware version number"""

        conn = self.__i2c_bus_connection
        i2c_addr = self.__i2c_addr

        conn.write_byte(i2c_addr, 0x00)
        version = conn.read_byte(i2c_addr)
        return version
