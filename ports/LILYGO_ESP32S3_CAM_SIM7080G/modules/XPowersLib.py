
AXP2101_SLAVE_ADDRESS = 0x34

XPOWERS_AXP2101_ADC_CHANNEL_CTRL = 0x30
XPOWERS_AXP2101_CHGLED_SET_CTRL = 0x69
XPOWERS_AXP2101_DC_ONOFF_DVM_CTRL = 0x80
XPOWERS_AXP2101_DC_VOL2_CTRL = 0x84
XPOWERS_AXP2101_LDO_ONOFF_CTRL0 = 0x90
XPOWERS_AXP2101_LDO_VOL4_CTRL = 0x96
XPOWERS_AXP2101_LDO_VOL5_CTRL = 0x97

XPOWERS_CHG_LED_OFF = 0
XPOWERS_CHG_LED_BLINK_1HZ = 1
XPOWERS_CHG_LED_BLINK_4HZ = 2
XPOWERS_CHG_LED_ON = 3
XPOWERS_CHG_LED_CTRL_CHG = 4

XPOWERS_AXP2101_BLDO1_VOL_STEPS = 100 
XPOWERS_AXP2101_BLDO1_VOL_MIN = 500   
XPOWERS_AXP2101_BLDO1_VOL_MAX = 3500 


XPOWERS_AXP2101_BLDO2_VOL_STEPS = 100
XPOWERS_AXP2101_BLDO2_VOL_MIN = 500 
XPOWERS_AXP2101_BLDO2_VOL_MAX = 3500


XPOWERS_AXP2101_DCDC3_VOL1_MIN = 500   
XPOWERS_AXP2101_DCDC3_VOL1_MAX = 1200 
XPOWERS_AXP2101_DCDC3_VOL_STEPS1 = 10   

XPOWERS_AXP2101_DCDC3_VOL2_MIN = 1220   
XPOWERS_AXP2101_DCDC3_VOL2_MAX = 1540  
XPOWERS_AXP2101_DCDC3_VOL_STEPS2 = 20   
XPOWERS_AXP2101_DCDC3_VOL_STEPS2_BASE = 71 

XPOWERS_AXP2101_DCDC3_VOL3_MIN = 1550 
XPOWERS_AXP2101_DCDC3_VOL3_MAX = 3400 
XPOWERS_AXP2101_DCDC3_VOL_STEPS3 = 100   
XPOWERS_AXP2101_DCDC3_VOL_STEPS3_BASE = 88  

# Function to simulate PMU functionalities
class XPowersPMU:
    def begin(self, i2c, address, sda, scl):
        self.i2c = i2c
        self.address = address
        try:
            # Read a register (choose an appropriate register to read for confirmation)
            i2c.readfrom_mem(address, 0x00, 1)  # Replace 0x00 with an actual register address
            return True
        except OSError:
            return False
        
    def readRegister(self, reg):
        try:
            return self.i2c.readfrom_mem(self.address, reg, 1)[0]
        except:
            return -1
    
    def write_register(self, reg, val):
        try:
            self.i2c.writeto_mem(self.address, reg, bytes([val]))
            return True
        except:
            return False

    def setChargingLedMode(self, mode):
        if mode in [XPOWERS_CHG_LED_OFF, XPOWERS_CHG_LED_BLINK_1HZ, 
                   XPOWERS_CHG_LED_BLINK_4HZ, XPOWERS_CHG_LED_ON]:
            val = self.readRegister(XPOWERS_AXP2101_CHGLED_SET_CTRL)
            if val == -1:
                return
            val &= 0xC8
            val |= 0x05  
            val |= (mode << 4) 
            self.write_register(XPOWERS_AXP2101_CHGLED_SET_CTRL, val)  
        elif mode == XPOWERS_CHG_LED_CTRL_CHG:
            val = self.readRegister(XPOWERS_AXP2101_CHGLED_SET_CTRL)
            if val == -1:
                return
            val &= 0xF9
            self.write_register(XPOWERS_AXP2101_CHGLED_SET_CTRL, val | 0x01)
            # self.write_register(XPOWERS_AXP2101_CHGLED_SET_CTRL, val | 0x02)

    def disableDC(self, num):
        if num == 1:
            return self.clrRegisterBit(XPOWERS_AXP2101_DC_ONOFF_DVM_CTRL, 0)
        elif num == 2:
            return self.clrRegisterBit(XPOWERS_AXP2101_DC_ONOFF_DVM_CTRL, 1)
        elif num == 3:
            return self.clrRegisterBit(XPOWERS_AXP2101_DC_ONOFF_DVM_CTRL, 2)
        elif num == 4:
            return self.clrRegisterBit(XPOWERS_AXP2101_DC_ONOFF_DVM_CTRL, 3)
        elif num == 5:
            return self.clrRegisterBit(XPOWERS_AXP2101_DC_ONOFF_DVM_CTRL, 4)
        return False
    
    def disableALDO(self, num):
        if num == 1:
            return self.clrRegisterBit(XPOWERS_AXP2101_LDO_ONOFF_CTRL0, 0)
        elif num == 2:
            return self.clrRegisterBit(XPOWERS_AXP2101_LDO_ONOFF_CTRL0, 1)
        elif num == 3:
            return self.clrRegisterBit(XPOWERS_AXP2101_LDO_ONOFF_CTRL0, 2)
        elif num == 4:
            return self.clrRegisterBit(XPOWERS_AXP2101_LDO_ONOFF_CTRL0, 3)
    
    def disableBLDO(self, num):
        if num == 1:
            return self.clrRegisterBit(XPOWERS_AXP2101_LDO_ONOFF_CTRL0, 4)
        elif num == 2:
            return self.clrRegisterBit(XPOWERS_AXP2101_LDO_ONOFF_CTRL0, 5)
    
    def disableCPUSLDO(self):
        return self.clrRegisterBit(XPOWERS_AXP2101_LDO_ONOFF_CTRL0, 6)
    
    def disableDLDO(self, num):
        if num == 1:
            return self.clrRegisterBit(XPOWERS_AXP2101_LDO_ONOFF_CTRL0, 7)
        elif num == 2:
            return self.clrRegisterBit(XPOWERS_AXP2101_LDO_ONOFF_CTRL0, 0)
        
    def clrRegisterBit(self, registers, bit):
        val = self.readRegister(registers)
        if val == -1:
            return False
        # Clear the specified bit
        val &= ~(1 << bit)
        return self.write_register(registers, val)

    def setBLDO1Voltage(self, millivolt):
        if millivolt % XPOWERS_AXP2101_BLDO1_VOL_STEPS != 0:
            print(f"Mistake ! The steps must be {XPOWERS_AXP2101_BLDO1_VOL_STEPS} mV")
            return False
        if millivolt < XPOWERS_AXP2101_BLDO1_VOL_MIN:
            print(f"Mistake ! BLDO1 minimum output voltage is {XPOWERS_AXP2101_BLDO1_VOL_MIN} mV")
            return False
        elif millivolt > XPOWERS_AXP2101_BLDO1_VOL_MAX:
            print(f"Mistake ! BLDO1 maximum output voltage is {XPOWERS_AXP2101_BLDO1_VOL_MAX} mV")
            return False
        val = self.readRegister(XPOWERS_AXP2101_LDO_VOL4_CTRL)
        if val == -1:
            return False
        voltage_step = (millivolt - XPOWERS_AXP2101_BLDO1_VOL_MIN) // XPOWERS_AXP2101_BLDO1_VOL_STEPS
        val &= 0xE0
        val |= voltage_step
        return self.write_register(XPOWERS_AXP2101_LDO_VOL4_CTRL, val)

    def enableBLDO1(self):
        return self.setRegisterBit(XPOWERS_AXP2101_LDO_ONOFF_CTRL0, 4)
    
    def setRegisterBit(self, registers, bit):
        val = self.readRegister(registers)
        if val == -1:
            return False
        val |= (1 << bit)
        return self.write_register(registers, val)
    
    def setDC3Voltage(self, millivolt):
        val = self.readRegister(XPOWERS_AXP2101_DC_VOL2_CTRL)
        if val == -1:
            return False
        val &= 0x80
        if XPOWERS_AXP2101_DCDC3_VOL1_MIN <= millivolt <= XPOWERS_AXP2101_DCDC3_VOL1_MAX:
            if millivolt % XPOWERS_AXP2101_DCDC3_VOL_STEPS1 != 0:
                print(f"Mistake ! The steps must be {XPOWERS_AXP2101_DCDC3_VOL_STEPS1} mV")
                return False
            voltage_step = (millivolt - XPOWERS_AXP2101_DCDC3_VOL1_MIN) // XPOWERS_AXP2101_DCDC3_VOL_STEPS1
            val |= voltage_step
            return self.write_register(XPOWERS_AXP2101_DC_VOL2_CTRL, val)
        elif XPOWERS_AXP2101_DCDC3_VOL2_MIN <= millivolt <= XPOWERS_AXP2101_DCDC3_VOL2_MAX:
            if millivolt % XPOWERS_AXP2101_DCDC3_VOL_STEPS2 != 0:
                print(f"Mistake ! The steps must be {XPOWERS_AXP2101_DCDC3_VOL_STEPS2} mV")
                return False
            voltage_step = (millivolt - XPOWERS_AXP2101_DCDC3_VOL2_MIN) // XPOWERS_AXP2101_DCDC3_VOL_STEPS2
            val |= (voltage_step + XPOWERS_AXP2101_DCDC3_VOL_STEPS2_BASE)
            return self.write_register(XPOWERS_AXP2101_DC_VOL2_CTRL, val)
        elif XPOWERS_AXP2101_DCDC3_VOL3_MIN <= millivolt <= XPOWERS_AXP2101_DCDC3_VOL3_MAX:
            if millivolt % XPOWERS_AXP2101_DCDC3_VOL_STEPS3 != 0:
                print(f"Mistake ! The steps must be {XPOWERS_AXP2101_DCDC3_VOL_STEPS3} mV")
                return False
            voltage_step = (millivolt - XPOWERS_AXP2101_DCDC3_VOL3_MIN) // XPOWERS_AXP2101_DCDC3_VOL_STEPS3
            val |= (voltage_step + XPOWERS_AXP2101_DCDC3_VOL_STEPS3_BASE)
            return self.write_register(XPOWERS_AXP2101_DC_VOL2_CTRL, val)
        print(f"Mistake ! DC3 voltage {millivolt} mV is out of range")
        return False

    def enableDC3(self):
        return self.setRegisterBit(XPOWERS_AXP2101_DC_ONOFF_DVM_CTRL, 2)

    def setBLDO2Voltage(self, millivolt):
        if millivolt % XPOWERS_AXP2101_BLDO2_VOL_STEPS != 0:
            print(f"Mistake ! The steps must be {XPOWERS_AXP2101_BLDO2_VOL_STEPS} mV")
            return False
        if millivolt < XPOWERS_AXP2101_BLDO2_VOL_MIN:
            print(f"Mistake ! BLDO2 minimum output voltage is {XPOWERS_AXP2101_BLDO2_VOL_MIN} mV")
            return False
        elif millivolt > XPOWERS_AXP2101_BLDO2_VOL_MAX:
            print(f"Mistake ! BLDO2 maximum output voltage is {XPOWERS_AXP2101_BLDO2_VOL_MAX} mV")
            return False
        val = self.readRegister(XPOWERS_AXP2101_LDO_VOL5_CTRL)
        if val == -1:
            return False
        val &= 0xE0
        voltage_step = (millivolt - XPOWERS_AXP2101_BLDO2_VOL_MIN) // XPOWERS_AXP2101_BLDO2_VOL_STEPS
        val |= voltage_step
        return self.write_register(XPOWERS_AXP2101_LDO_VOL5_CTRL, val)

    def enableBLDO2(self):
        return self.setRegisterBit(XPOWERS_AXP2101_LDO_ONOFF_CTRL0, 5)

    def disableTSPinMeasure(self):
        return self.clrRegisterBit(XPOWERS_AXP2101_ADC_CHANNEL_CTRL, 1)
