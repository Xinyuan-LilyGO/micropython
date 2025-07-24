import time
import machine
from micropython import const

class ST7796:
    WHITE = const(0xFFFF)
    BLACK = const(0x0000)
    RED = const(0xF800)
    GREEN = const(0x07E0)
    BLUE = const(0x001F)
    YELLOW = const(0xFFE0)
    PALERED = const(0xFDB8)     # 浅红色
    PURPLE = const(0x8010)     # 紫色
    ORANGE = const(0x7e0)     # 橙色
    DARKGREEN = const(0xd79c)  # 深绿色
    
    # Rotation constants
    ROTATE_0 = 0
    ROTATE_90 = 1
    ROTATE_180 = 2
    ROTATE_270 = 3

    def __init__(self, spi, cs, dc, rst, bl, width=480, height=320):
        self.ST7796_WIDTH = const(width)
        self.ST7796_HEIGHT = const(height)
        self.ST7796_MADCTL_MY = const(0x80)
        self.ST7796_MADCTL_MX = const(0x40)
        self.ST7796_MADCTL_MV = const(0x20)
        self.ST7796_MADCTL_ML = const(0x10)
        self.ST7796_MADCTL_RGB = const(0x00)
        self.ST7796_MADCTL_BGR = const(0x08)
        self.ST7796_MADCTL_MH = const(0x04)
        
        self._width = width
        self._height = height
        self._rotation = self.ROTATE_0  # Default rotation

        self.spi = spi
        self.dc = machine.Pin(dc, machine.Pin.OUT)
        self.cs = machine.Pin(cs, machine.Pin.OUT)
        self.rst = machine.Pin(rst, machine.Pin.OUT)
        self.backlight = machine.Pin(bl, machine.Pin.OUT)

        self.init_display()
        self.init_display()
    
    @property
    def rotation(self):
        return self._rotation
    
    @rotation.setter
    def rotation(self, rotation):
        self._rotation = rotation % 4  # Ensure rotation is between 0-3
        self._update_rotation()
    
    @property
    def width(self):
        return self._width if self._rotation % 2 == 0 else self._height
    
    @property
    def height(self):
        return self._height if self._rotation % 2 == 0 else self._width
    
    def _update_rotation(self):
        """Update the display rotation based on current rotation setting"""
        if self._rotation == self.ROTATE_0:
            madctl = self.ST7796_MADCTL_MX | self.ST7796_MADCTL_MY | self.ST7796_MADCTL_RGB
        elif self._rotation == self.ROTATE_90:
            madctl = self.ST7796_MADCTL_MY | self.ST7796_MADCTL_MV | self.ST7796_MADCTL_RGB
        elif self._rotation == self.ROTATE_180:
            madctl = self.ST7796_MADCTL_RGB
        elif self._rotation == self.ROTATE_270:
            madctl = self.ST7796_MADCTL_MX | self.ST7796_MADCTL_MV | self.ST7796_MADCTL_RGB
        
        self.write_command(0x36)  # Memory Access Control
        self.write_data(madctl)

    def write_command(self, cmd):
        self.dc.value(0)
        self.cs.value(0)
        self.spi.write(bytearray([cmd]))
        self.cs.value(1)

    def write_data(self, data):
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(bytearray([data]))
        self.cs.value(1)

    def reset(self):
        self.rst.value(0)
        time.sleep_ms(100)
        self.rst.value(1)
        time.sleep_ms(100)

    def init_display(self):
        self.reset()
        self.write_command(0x11)  # Sleep out
        time.sleep_ms(120)
        self.write_command(0x3A)  # Interface Pixel Format
        self.write_data(0x55)  # 16-bit color
        self.write_command(0xB2)  # Gate Control
        self.write_data(0x02)
        self.write_data(0x02)
        self.write_data(0x02)
        self.write_data(0x02)
        self.write_data(0x02)
        self.write_command(0xB7)  # Entry Mode Set
        self.write_data(0x07)
        self.write_command(0xBB)  # Front Porch
        self.write_data(0x28)
        self.write_command(0xC0)  # Porch Setting
        self.write_data(0x28)
        self.write_data(0x0C)
        self.write_command(0xC1)  # Display Function Control
        self.write_data(0xC0)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_command(0xC5)  # Power Control 1
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_command(0xC7)  # Power Control 2
        self.write_data(0x00)
        self._update_rotation()  # Set initial rotation
        self.write_command(0x3A)  # Interface Pixel Format
        self.write_data(0x55)  # 16-bit color
        self.write_command(0x29)  # Display on
        self.backlight.value(1)
        
#     def set_backlight(self, duty):
#         """设置背光亮度，duty 应该在 0（最暗）到 1023（最亮）之间"""
#         self.backlight.duty(duty)
        
    def set_window(self, x0, y0, x1, y1):
        self.write_command(0x2A)  # Column address set
        self.write_data((x0 >> 8) & 0xFF)
        self.write_data(x0 & 0xFF)
        self.write_data((x1 >> 8) & 0xFF)
        self.write_data(x1 & 0xFF)
        self.write_command(0x2B)  # Page address set
        self.write_data((y0 >> 8) & 0xFF)
        self.write_data(y0 & 0xFF)
        self.write_data((y1 >> 8) & 0xFF)
        self.write_data(y1 & 0xFF)
        self.write_command(0x2C)  # Memory write

    def fillScreen(self, x, y, color, width=480, height=320):
        # 考虑旋转角度
        if self.rotation == self.ROTATE_90 or self.rotation == self.ROTATE_270:
            width, height = height, width  # 如果旋转90°或270°，宽高需要交换

        self.set_window(x, y, x + width - 1, y + height - 1)
        self.dc.value(1)
        self.cs.value(0)

        for i in range(height):
            row_buffer = bytearray([color >> 8, color & 0xFF] * width)
            self.spi.write(row_buffer)

        self.cs.value(1)

    def draw_pixel(self, x, y, color):
        self.set_window(x, y, x, y)
        buffer = bytearray([color >> 8, color & 0xFF])
        self.dc.value(1)
        self.cs.value(0)
        self.spi.write(buffer)
        self.cs.value(1)
        
    def draw_char(self, x, y, char, color, bg_color, size=2):
        # 扩展字体数据，包含数字0-9和大小写字母A-Z
        font = {
            # 数字
            '0': [0x3C, 0x66, 0x6E, 0x76, 0x66, 0x66, 0x3C, 0x00],
            '1': [0x18, 0x38, 0x18, 0x18, 0x18, 0x18, 0x3C, 0x00],
            '2': [0x3C, 0x66, 0x06, 0x0C, 0x18, 0x30, 0x7E, 0x00],
            '3': [0x3C, 0x66, 0x06, 0x1C, 0x06, 0x66, 0x3C, 0x00],
            '4': [0x0C, 0x1C, 0x2C, 0x4C, 0x7E, 0x0C, 0x0C, 0x00],
            '5': [0x7E, 0x60, 0x7C, 0x06, 0x06, 0x66, 0x3C, 0x00],
            '6': [0x1C, 0x30, 0x60, 0x7C, 0x66, 0x66, 0x3C, 0x00],
            '7': [0x7E, 0x06, 0x0C, 0x18, 0x18, 0x18, 0x18, 0x00],
            '8': [0x3C, 0x66, 0x66, 0x3C, 0x66, 0x66, 0x3C, 0x00],
            '9': [0x3C, 0x66, 0x66, 0x3E, 0x06, 0x0C, 0x38, 0x00],
            # 大写字母
            'A': [0x18, 0x3C, 0x66, 0x66, 0x7E, 0x66, 0x66, 0x00],
            'B': [0x7C, 0x66, 0x66, 0x7C, 0x66, 0x66, 0x7C, 0x00],
            'C': [0x3C, 0x66, 0x60, 0x60, 0x60, 0x66, 0x3C, 0x00],
            'D': [0x78, 0x6C, 0x66, 0x66, 0x66, 0x6C, 0x78, 0x00],
            'E': [0x7E, 0x60, 0x60, 0x78, 0x60, 0x60, 0x7E, 0x00],
            'F': [0x7E, 0x60, 0x60, 0x78, 0x60, 0x60, 0x60, 0x00],
            'G': [0x3C, 0x66, 0x60, 0x6E, 0x66, 0x66, 0x3C, 0x00],
            'H': [0x66, 0x66, 0x66, 0x7E, 0x66, 0x66, 0x66, 0x00],
            'I': [0x3C, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3C, 0x00],
            'J': [0x1E, 0x0C, 0x0C, 0x0C, 0x0C, 0x6C, 0x38, 0x00],
            'K': [0x66, 0x6C, 0x78, 0x70, 0x78, 0x6C, 0x66, 0x00],
            'L': [0x60, 0x60, 0x60, 0x60, 0x60, 0x60, 0x7E, 0x00],
            'M': [0x63, 0x77, 0x7F, 0x6B, 0x63, 0x63, 0x63, 0x00],
            'N': [0x66, 0x76, 0x7E, 0x7E, 0x6E, 0x66, 0x66, 0x00],
            'O': [0x3C, 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x00],
            'P': [0x7C, 0x66, 0x66, 0x7C, 0x60, 0x60, 0x60, 0x00],
            'Q': [0x3C, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x0E, 0x00],
            'R': [0x7C, 0x66, 0x66, 0x7C, 0x78, 0x6C, 0x66, 0x00],
            'S': [0x3C, 0x66, 0x60, 0x3C, 0x06, 0x66, 0x3C, 0x00],
            'T': [0x7E, 0x18, 0x18, 0x18, 0x18, 0x18, 0x18, 0x00],
            'U': [0x66, 0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x00],
            'V': [0x66, 0x66, 0x66, 0x66, 0x66, 0x3C, 0x18, 0x00],
            'W': [0x63, 0x63, 0x63, 0x6B, 0x7F, 0x77, 0x63, 0x00],
            'X': [0x66, 0x66, 0x3C, 0x18, 0x3C, 0x66, 0x66, 0x00],
            'Y': [0x66, 0x66, 0x66, 0x3C, 0x18, 0x18, 0x18, 0x00],
            'Z': [0x7E, 0x06, 0x0C, 0x18, 0x30, 0x60, 0x7E, 0x00],
            # 小写字母
            'a': [0x00, 0x00, 0x3C, 0x06, 0x3E, 0x66, 0x3E, 0x00],
            'b': [0x60, 0x60, 0x7C, 0x66, 0x66, 0x66, 0x7C, 0x00],
            'c': [0x00, 0x00, 0x3C, 0x66, 0x60, 0x66, 0x3C, 0x00],
            'd': [0x06, 0x06, 0x3E, 0x66, 0x66, 0x66, 0x3E, 0x00],
            'e': [0x00, 0x00, 0x3C, 0x66, 0x7E, 0x60, 0x3C, 0x00],
            'f': [0x1C, 0x30, 0x30, 0x7C, 0x30, 0x30, 0x30, 0x00],
            'g': [0x00, 0x00, 0x3E, 0x66, 0x66, 0x3E, 0x06, 0x3C],
            'h': [0x60, 0x60, 0x7C, 0x66, 0x66, 0x66, 0x66, 0x00],
            'i': [0x18, 0x00, 0x38, 0x18, 0x18, 0x18, 0x3C, 0x00],
            'j': [0x06, 0x00, 0x06, 0x06, 0x06, 0x06, 0x66, 0x3C],
            'k': [0x60, 0x60, 0x66, 0x6C, 0x78, 0x6C, 0x66, 0x00],
            'l': [0x38, 0x18, 0x18, 0x18, 0x18, 0x18, 0x3C, 0x00],
            'm': [0x00, 0x00, 0x66, 0x7F, 0x7F, 0x6B, 0x63, 0x00],
            'n': [0x00, 0x00, 0x7C, 0x66, 0x66, 0x66, 0x66, 0x00],
            'o': [0x00, 0x00, 0x3C, 0x66, 0x66, 0x66, 0x3C, 0x00],
            'p': [0x00, 0x00, 0x7C, 0x66, 0x66, 0x7C, 0x60, 0x60],
            'q': [0x00, 0x00, 0x3E, 0x66, 0x66, 0x3E, 0x06, 0x06],
            'r': [0x00, 0x00, 0x7C, 0x66, 0x60, 0x60, 0x60, 0x00],
            's': [0x00, 0x00, 0x3E, 0x60, 0x3C, 0x06, 0x7C, 0x00],
            't': [0x30, 0x30, 0x7C, 0x30, 0x30, 0x30, 0x1C, 0x00],
            'u': [0x00, 0x00, 0x66, 0x66, 0x66, 0x66, 0x3E, 0x00],
            'v': [0x00, 0x00, 0x66, 0x66, 0x66, 0x3C, 0x18, 0x00],
            'w': [0x00, 0x00, 0x63, 0x6B, 0x7F, 0x3E, 0x36, 0x00],
            'x': [0x00, 0x00, 0x66, 0x3C, 0x18, 0x3C, 0x66, 0x00],
            'y': [0x00, 0x00, 0x66, 0x66, 0x66, 0x3E, 0x06, 0x3C],
            'z': [0x00, 0x00, 0x7E, 0x0C, 0x18, 0x30, 0x7E, 0x00],
            '-': [0x00, 0x00, 0x00, 0x00, 0x7E, 0x00, 0x00, 0x00],
            '<': [0x00, 0x06, 0x0C, 0x18, 0x30, 0x18, 0x0C, 0x06],
            '[': [0x3C, 0x30, 0x30, 0x30, 0x30, 0x30, 0x3C, 0x00],
            ']': [0x3C, 0x0C, 0x0C, 0x0C, 0x0C, 0x0C, 0x3C, 0x00],
            ':': [0x00, 0x18, 0x18, 0x00, 0x00, 0x18, 0x18, 0x00],
            '.': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x18, 0x18],
            '>': [0x00, 0x30, 0x18, 0x0C, 0x06, 0x0C, 0x18, 0x30],
            '*': [0x00, 0x00, 0x18, 0x7E, 0x18, 0x00, 0x00, 0x00],  # 添加 *
            '(': [0x00, 0x0C, 0x18, 0x30, 0x30, 0x30, 0x18, 0x0C],  # 添加 (
            ')': [0x00, 0x30, 0x18, 0x0C, 0x0C, 0x0C, 0x18, 0x30],  # 添加 )
            '/': [0x00, 0x02, 0x04, 0x08, 0x10, 0x20, 0x00, 0x00],  # 添加 /
            # 空格
            ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        }
        
        # 如果字符不在字体中，显示为空格
        char = char.upper() if char not in font else char
        char_data = font.get(char, font[' '])

        # 设置窗口大小
        self.set_window(x, y, x + 8 * size - 1, y + 8 * size - 1)
        self.dc.value(1)
        self.cs.value(0)

        # 创建缓冲区
        buffer = bytearray()

        # 遍历字符数据并生成缓冲区
        for row in char_data:
            for i in range(8):  # 遍历字节的每一位
                pixel_color = color if (row >> (7 - i)) & 0x01 else bg_color
                for _ in range(size):  # 水平方向放大
                    buffer.append(pixel_color >> 8)  # 高位
                    buffer.append(pixel_color & 0xFF)  # 低位
            for _ in range(size - 1):  # 垂直方向放大（复制行）
                buffer.extend(buffer[-16 * size:])  # 复制最后一行

        # 发送缓冲区数据
        self.spi.write(buffer)
        self.cs.value(1)
        
    def draw_text(self, x, y, text, color, bg_color, size=2, rotation=0, spacing=-1):
        self.rotation = rotation
        for i, char in enumerate(text):
            # 计算每个字符的位置，增加字符间距
            self.draw_char(x + i * (8 * size + spacing), y, char, color, bg_color, size)

    def draw_button(self, x, y, width, height, color, text="", text_color=WHITE, text_size=1, rotation=0):
        """绘制一个带可选文本的矩形按钮，支持旋转"""
        # 计算文本宽度和高度
        text_width = len(text) * 8 * text_size
        text_height = 8 * text_size
        
        # 绘制按钮背景 165, 200, 40, 150
        if rotation==1 or rotation==3:
            h = height
            height = width
            width = h
        
        self.fillScreen(x, y, color, height, width)
        
        if rotation==0 or rotation==2:
            h = height
            height = width
            width = h
            
        # 计算文本位置（基于原始坐标和尺寸） 20  100   width 80
        text_x = x + (width - text_width) // 2
        text_y = y + (height - text_height) // 2
        
        # 如果有文本，居中显示
        if text:
            self.draw_text(text_x, text_y, text, text_color, color, size=text_size, rotation=rotation)
            
    def display_image(self, image_data):
        """显示图像数据"""
        self.set_window(0, 0, self.width - 1, self.height - 1)  # 设置整个屏幕窗口
        self.dc.value(1)  # 数据模式
        self.cs.value(0)  # 启动 SPI 通信
        self.spi.write(image_data)  # 发送图像数据
        self.cs.value(1)  # 结束 SPI 通信
        
    def blit_buffer(self, buffer, x, y, width, height ,rotation=0):
        """
        Copy buffer to display at the given location.

        Args:
            buffer (bytes): Data to copy to display
            x (int): Top left corner x coordinate
            y (int): Top left corner y coordinate
            width (int): Width
            height (int): Height
        """
        self.rotation = rotation
        self.set_window(x, y, x + width - 1, y + height - 1)  # Set the window to the specified area
        self.dc.value(1)  # Data mode
        self.cs.value(0)  # Start SPI communication
        self.spi.write(buffer)  # Write the image data from the buffer
        self.cs.value(1)  # End SPI communication
