import smbus2
import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import Adafruit_SSD1306 as SSD


class OLED(object):
    """Control of OLED display equipment"""

    def __init__(
        self, i2c_bus_number: int = 1, row_height: int = 8, debug: bool = False
    ):
        if not isinstance(i2c_bus_number, int):
            raise TypeError("i2c_bus_number must be of type int")
        if not isinstance(row_height, int):
            raise TypeError("row_height must be of type int")
        if not isinstance(debug, bool):
            raise TypeError("debug must be of type bool")

        self.__i2c_bus = i2c_bus_number
        self.__row_height = row_height
        self.__debug = debug

        # Maximize the use of the entire OLED screen
        self.__init_y = -2
        self.__init_x = 0

        # OLED sceen width and height
        self.__width = 128
        self.__height = 32
        self.__image = Image.new("1", (self.__width, self.__height))
        self.__draw = ImageDraw.Draw(self.__image)
        self.__font = ImageFont.load_default()

    def __del__(self):
        if self.__debug:
            print("OLED End!")

    def init(self) -> bool:
        """Initialize OLED, return True on success, False on failure"""

        i2c_bus = self.__i2c_bus

        try:
            oled = SSD.SSD1306_128_32(rst=None, i2c_bus=i2c_bus, gpio=1)
        except Exception as e:
            print("init SSD1306_128_32 failed: {}".format(e))
            print("OLED device no found: i2c_bus[{}]".format(i2c_bus))
            return False
        else:
            if self.__debug:
                print("init oled done")

        try:
            oled.begin()
        except Exception as e:
            print("init begin failed: {}".format(e))
            return False
        else:
            if self.__debug:
                print("oled begin")

        try:
            oled.clear()
        except Exception as e:
            print("init clear failed: {}".format(e))
            return False
        else:
            if self.__debug:
                print("oled clear")

        try:
            oled.display()
        except Exception as e:
            print("init display failed: {}".format(e))
            return False
        else:
            if self.__debug:
                print("oled display")

        self.__oled = oled
        return True

    def clear(self, refresh: bool = False) -> bool:
        """
        Clear the display:
        refresh =True refresh immediately, refresh=False opposite.
        """

        if not isinstance(refresh, bool):
            raise TypeError("refresh must be of type bool")

        draw = self.__draw
        width = self.__width
        height = self.__height

        # Upper left corner coordinates is (0, 0)
        # Lower right corner coordinates is (width, height)
        # Border color is 0 (black)
        # Inner fill color is 0 (black)
        draw.rectangle((0, 0, width, height), outline=0, fill=0)

        if refresh:
            try:
                self.refresh()
            except Exception as e:
                print("OLED refresh failed: {}".format(e))
                return False
            else:
                return True
        else:
            if self.__debug:
                print("not refresh right now")

        return True

    def add_text(self, start_x: int, start_y: int, text: str, refresh: bool = False):
        """
        Add characters:
        start_x and start_y indicates the starting point, text is the character to be added,
        refresh =True refresh immediately, refresh=False opposite.
        """

        if not isinstance(start_x, int):
            raise TypeError("start_x must be of type int")
        if not isinstance(start_y, int):
            raise TypeError("start_y must be of type int")
        if not isinstance(text, str):
            raise TypeError("text must be of type str")
        if not isinstance(refresh, bool):
            raise TypeError("refresh must be of type bool")

        draw = self.__draw
        width = self.__width
        height = self.__height
        font = self.__font

        if start_x > width or start_x < 0 or start_y < 0 or start_y > height:
            print("input () out of display range")
        else:
            init_x = self.__init_x
            init_y = self.__init_y
            x = start_x + init_x
            y = start_y + init_y
            # The upper left corner of the text is (x, y) with white text (fill=255)
            draw.text((x, y), text, font=font, fill=255)
            if self.__debug:
                print("draw text now")
            if refresh:
                self.refresh()

    def add_row(self, text: str, row: int = 0, refresh: bool = False):
        """
        Write a line of character text:
        refresh =True, refresh immediately, refresh=False opposite,
        line=0, 1, 2, 3, total 4 rows.
        """

        if not isinstance(text, str):
            raise TypeError("text must be of type str")
        if not isinstance(row, int):
            raise TypeError("row must be of type int")
        if not isinstance(refresh, bool):
            raise TypeError("refresh must be of type bool")

        if row < 0 or row > 3:
            print("oled line input error")
        else:
            row_height = self.__row_height
            y = row_height * row
            self.add_text(0, y, text, refresh)
            if self.__debug:
                print("add row now")

    def refresh(self):
        """Refresh the OLED to display the content"""
        oled = self.__oled
        image = self.__image
        oled.image(image)
        oled.display()


class Cube(object):
    """Control of peripheral devices such as fans and lights"""

    def __init__(
        self, i2c_bus_number: int = 1, delay: float = 0.002, debug: bool = False
    ):
        if not isinstance(i2c_bus_number, int):
            raise TypeError("i2c_bus_number must be of type int")
        if not isinstance(delay, float):
            raise TypeError("delay must be of type float")
        if not isinstance(debug, bool):
            raise TypeError("debug must be of type bool")

        self.__delay = delay
        self.__debug = debug

        self.__i2c_bus = smbus2.SMBus(i2c_bus_number)

        self.__i2c_addr = 0x0E
        self.__reg_fan = 0x08
        self.__reg_rgb_effect = 0x04
        self.__reg_rgb_speed = 0x05
        self.__reg_rgb_color = 0x06

    def __del__(self):
        if self.__debug:
            print("Cube End!")

    def set_fan(self, state: int):
        """
        Control fan:
        start=0 close, start=1 open.
        """

        if not isinstance(state, int):
            raise TypeError("state must be of type int")

        if state > 0:
            state = 1
        else:
            state = 0

        conn = self.__i2c_bus
        i2c_addr = self.__i2c_addr
        reg_fan = self.__reg_fan
        delay = self.__delay

        try:
            conn.write_byte_data(i2c_addr, reg_fan, state)
            if delay > 0:
                time.sleep(delay)
        except Exception as e:
            print("set_fan failed: {}".format(e))
        else:
            if self.__debug:
                print("set_fan ok")

    def set_rgb_effect(self, effect: int):
        """
        Control RGB light effect:
        0 off effect, 1 breathing light, 2 marquee light, 3 rainbow light,
        4 dazzling lights, 5 running water lights, 6 circulation breathing lights.
        """

        if not isinstance(effect, int):
            raise TypeError("effect must be of type int")

        if effect < 0:
            effect = 0
        elif effect > 6:
            effect = 6

        conn = self.__i2c_bus
        i2c_addr = self.__i2c_addr
        reg_rgb_effect = self.__reg_rgb_effect
        delay = self.__delay

        try:
            conn.write_byte_data(i2c_addr, reg_rgb_effect, effect)
            if delay > 0:
                time.sleep(delay)
        except Exception as e:
            print("set_rgb_effect failed: {}".format(e))
        else:
            if self.__debug:
                print("set_rgb_effect ok")

    def set_rgb_speed(self, speed: int):
        """
        Set RGB light effect speed:
        1 low speed, 2 medium speed, 3 high speed.
        """

        if not isinstance(speed, int):
            raise TypeError("speed must be of type int")

        if speed < 1:
            speed = 1
        elif speed > 3:
            speed = 3

        conn = self.__i2c_bus
        i2c_addr = self.__i2c_addr
        reg_rgb_speed = self.__reg_rgb_speed
        delay = self.__delay

        try:
            conn.write_byte_data(i2c_addr, reg_rgb_speed, speed)
            if delay > 0:
                time.sleep(delay)
        except Exception as e:
            print("set_rgb_speed failed: {}".format(e))
        else:
            if self.__debug:
                print("set_rgb_speed ok")

    def set_rbg_color(self, color: int):
        """
        Set RGB light effect color:
        0 red, 1 green, 2 blue, 3 yellow, 4 purple, 5 cyan, 6 white.
        """

        if not isinstance(color, int):
            raise TypeError("color must be of type int")

        conn = self.__i2c_bus
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
        else:
            if self.__debug:
                print("set_rgb_color ok")

    def set_single_color(self, index: int, r: int, g: int, b: int):
        """
        Set the individual RGB light color:
        index indicates the serial number of the lamp bead 0-13, index=255 means to control all lamps,
        r stands for red, g stands for green, and b stands for blue.
        """

        if not isinstance(index, int):
            raise TypeError("index must be of type int")
        if not isinstance(r, int):
            raise TypeError("r must be of type int")
        if not isinstance(g, int):
            raise TypeError("g must be of type int")
        if not isinstance(b, int):
            raise TypeError("b must be of type int")

        conn = self.__i2c_bus
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
        else:
            if self.__debug:
                print("set_single_color ok")

    def get_Version(self):
        """Obtain the firmware version number"""

        conn = self.__i2c_bus
        i2c_addr = self.__i2c_addr

        conn.write_byte(i2c_addr, 0x00)
        version = conn.read_byte(i2c_addr)
        return version
