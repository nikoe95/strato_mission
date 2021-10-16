import smbus
import time

class MS5611:
    def __init__(self):
        self.C1 = 0
        self.C2 = 0
        self.C3 = 0
        self.C4 = 0
        self.C5 = 0
        self.C6 = 0
        self.D1 = 0
        self.D2 = 0
        self.dT = 0
        self.TEMP = 0
        self.OFF = 0
        self.SENS = 0
        self.T2 = 0
        self.OFF2 = 0
        self.SENS2 = 0
        self.pressure = 0
        self.temperature = 0
        self.bus = smbus.SMBus(1)

    def start_connection(self):
        self.bus.write_byte(0x77, 0x1E)
        time.sleep(0.5)


    def read_calibration_data(self):
        data = self.bus.read_i2c_block_data(0x77, 0xA2, 2)
        self.C1 = data[0] * 256 + data[1]
        
        data = self.bus.read_i2c_block_data(0x77, 0xA4, 2)
        self.C2 = data[0] * 256 + data[1]

        data = self.bus.read_i2c_block_data(0x77, 0xA6, 2)
        self.C3 = data[0] * 256 + data[1]

        data = self.bus.read_i2c_block_data(0x77, 0xA8, 2)
        self.C4 = data[0] * 256 + data[1]

        data = self.bus.read_i2c_block_data(0x77, 0xAA, 2)
        self.C5 = data[0] * 256 + data[1]

        data = self.bus.read_i2c_block_data(0x77, 0xAC, 2)
        self.C6 = data[0] * 256 + data[1]
    
    def read_data(self):
        self.bus.write_byte(0x77, 0x48)
        time.sleep(0.1)
        value = self.bus.read_i2c_block_data(0x77, 0x00, 3)
        self.D1 = value[0] * 65535 + value[1] * 256 + value[2]

        self.bus.write_byte(0x77, 0x58)
        time.sleep(0.1)
        value = self.bus.read_i2c_block_data(0x77, 0x00, 3)
        self.D2 = value[0] * 65536 + value[1] * 256 + value[2]

        self.dT = self.D2 - self.C5 * 256
        self.TEMP = 2000 + self.dT * self.C6/8388608
        self.OFF = self.C2 * 65536 + (self.C4 * self.dT)/128
        self.SENS = self.C1 * 32768 + (self.C3 * self.dT)/256
        
        self.data_alignment()
        self.print_data()

    
    def data_alignment(self):
        self.T2 = 0
        self.OFF2 = 0
        self.SENS2 = 0

        if self.TEMP >= 2000 :
            self.T2 = 0
            self.OFF2 = 0
            self.SENS2 = 0
        elif self.TEMP < 2000 :
            self.T2 = (self.dT * self.dT)/2147483648
            self.OFF2 = 5 * ((self.TEMP - 2000)*(self.TEMP-2000))/2
            self.SENS2 = 5 * ((self.TEMP - 2000) * (self.TEMP - 2000)) / 4
            if self.TEMP < -1500 :
                self.OFF2 = self.OFF2 + 7 * ((self.TEMP + 1500) * (self.TEMP + 1500))
                self.SENS2 = self.SENS2 + 11 * ((self.TEMP + 1500) * (self.TEMP + 1500)) / 2

        self.TEMP = self.TEMP - self.T2
        self.OFF = self.OFF - self.OFF2
        self.SENS = self.SENS - self.SENS2


    def print_data(self):
        self.pressure = ((((self.D1 * self.SENS) / 2097152) - self.OFF) / 32768.0) / 100.0
        self.temperature = self.TEMP / 100.0

        print(f'Pressure : {self.pressure} ')
        print(f'Temperature : {self.temperature} ')

