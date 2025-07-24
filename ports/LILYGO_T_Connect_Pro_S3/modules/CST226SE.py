from machine import Pin, I2C
import time

class CST226SE:    
    # Register addresses for the touch sensor
    RD_DEVICE_X1POSH = 0x01  
    RD_DEVICE_X1POSL = 0x03  
    RD_DEVICE_Y1POSH = 0x02  
    RD_DEVICE_Y1POSL = 0x03  
    RD_DEVICE_X2POSH = 0x08  
    RD_DEVICE_X2POSL = 0x0A  
    RD_DEVICE_Y2POSH = 0x09  
    RD_DEVICE_Y2POSL = 0x0A  
    RD_DEVICE_X3POSH = 0x0D  
    RD_DEVICE_X3POSL = 0x0F  
    RD_DEVICE_Y3POSH = 0x0E  
    RD_DEVICE_Y3POSL = 0x0F  
    RD_DEVICE_X4POSH = 0x12  
    RD_DEVICE_X4POSL = 0x14  
    RD_DEVICE_Y4POSH = 0x13  
    RD_DEVICE_Y4POSL = 0x14  
    RD_DEVICE_X5POSH = 0x17  
    RD_DEVICE_X5POSL = 0x19  
    RD_DEVICE_Y5POSH = 0x18  
    RD_DEVICE_Y5POSL = 0x19  
    RD_DEVICE_TOUCH1_PRESSURE_VALUE = 0x04  
    RD_DEVICE_TOUCH2_PRESSURE_VALUE = 0x07  
    RD_DEVICE_TOUCH3_PRESSURE_VALUE = 0x0C  
    RD_DEVICE_TOUCH4_PRESSURE_VALUE = 0x11  
    RD_DEVICE_TOUCH5_PRESSURE_VALUE = 0x16  

    def __init__(self, sda_pin, scl_pin, rst_pin, int_pin, device_address=0x5A):
        # Define I2C configuration
        self.i2c = I2C(1, scl=Pin(scl_pin), sda=Pin(sda_pin), freq=400000)
        self.touch_rst_pin = Pin(rst_pin, Pin.OUT)
        self.touch_int_pin = Pin(int_pin, Pin.IN)
        self.device_address = device_address
        self.touch_interrupt_flag = False

        # Set up interrupt pin
        self.touch_int_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.touch_interrupt_handler)

        # Reset the touch sensor
        self.reset_touch_sensor()

    def touch_interrupt_handler(self, pin):
        self.touch_interrupt_flag = True

    def reset_touch_sensor(self):
        self.touch_rst_pin.off()
        time.sleep_ms(100)
        self.touch_rst_pin.on()

    def read_register(self, reg):
        return self.i2c.readfrom_mem(self.device_address, reg, 1)[0]

    def begin_touch_sensor(self):
        time.sleep(1)
        try:
            self.device_id = self.read_register(0x06)  # Example device ID register
#             print(f"ID: {device_id:#X}")
            return True
        except OSError as e:
            print(f"CST226SE initialization fail: {e}")
            return False

    def read_touch_data(self):
        finger_number = self.read_register(0x05)
        touches = []
        pressures = []

        for i in range(1, finger_number + 1):
            try:
                # Obtain the register addresses for the given finger number
                x_high_addr = getattr(self, f'RD_DEVICE_X{i}POSH')
                x_low_addr = getattr(self, f'RD_DEVICE_X{i}POSL')
                y_high_addr = getattr(self, f'RD_DEVICE_Y{i}POSH')
                y_low_addr = getattr(self, f'RD_DEVICE_Y{i}POSL')
            except AttributeError:
                continue

            # Read the original data
            x_high = self.read_register(x_high_addr)
            x_low = self.read_register(x_low_addr)
            y_high = self.read_register(y_high_addr)
            y_low = self.read_register(y_low_addr)

            # Analyze the X and Y coordinates (12 bits)
            x = ((x_high & 0xFF) << 4) | ((x_low & 0xF0) >> 4)
            y = ((y_high & 0xFF) << 4) | (y_low & 0x0F)

            # Read the pressure value
            try:
                pressure_addr = getattr(self, f'RD_DEVICE_TOUCH{i}_PRESSURE_VALUE')
                pressure = self.read_register(pressure_addr)
            except AttributeError:
                continue

            touches.append((x, y))
            pressures.append(pressure)

        return finger_number, touches, pressures

    def is_touch_detected(self):
        return self.touch_interrupt_flag

    def clear_touch_interrupt_flag(self):
        self.touch_interrupt_flag = False


