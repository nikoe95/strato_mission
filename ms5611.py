import smbus
import time

#open i2c bus 1
#Addres of MS5611 in OKY3255 is 0x77

bus = smbus.SMBus(1)

#Reset Command 
bus.write_byte(0x77, 0x1E)
time.sleep(0.5)

#Read pressure sensitivity 
data = bus.read_i2c_block_data(0x77, 0xA2, 2)
C1 = data[0] * 256 + data[1]

data = bus.read_i2c_block_data(0x77, 0xA4, 2)
C2 = data[0] * 256 + data[1] 

#Read temperature coefiicient of pressure sensitivity 
data = bus.read_i2c_block_data(0x77, 0xA6, 2)
C3 = data[0] * 256 + data[1]

# Read temperature coefficient of pressure offset
data = bus.read_i2c_block_data(0x77, 0xA8, 2)
C4 = data[0] * 256 + data[1]

# Read reference temperature

data = bus.read_i2c_block_data(0x77, 0xAA, 2)
C5 = data[0] * 256 + data[1]

# Read temperature coefficient of the temperature
data = bus.read_i2c_block_data(0x77, 0xAC, 2)
C6 = data[0] * 256 + data[1]


while True:
#Pressure conversion(OSR = 256) command
    bus.write_byte(0x77, 0x48)
    time.sleep(0.5)
    value = bus.read_i2c_block_data(0x77, 0x00, 3)
    D1 = value[0] * 65535 + value[1] * 256 + value[2]

    bus.write_byte(0x77, 0x58)
    time.sleep(0.5)
    value = bus.read_i2c_block_data(0x77, 0x00, 3)
    D2 = value[0] * 65536 + value[1] * 256 + value[2]


    dT = D2 - C5 * 256
    TEMP = 2000 + dT * C6/8388608
    OFF = C2 * 65536 + (C4 * dT)/128
    SENS = C1 * 32768 + (C3 * dT)/256

#Compensation variables 
    T2 = 0
    OFF2 = 0
    SENS2 = 0 

    if TEMP >= 2000 :
        T2 = 0
        OFF2 = 0
        SENS2 = 0
    elif TEMP < 2000 :
        T2 = (dT * dT)/2147483648
        OFF2 = 5 * ((TEMP - 2000)*(TEMP-2000))/2
        SENS2 = 5 * ((TEMP - 2000) * (TEMP - 2000)) / 4
        if TEMP < -1500 :
            OFF2 = OFF2 + 7 * ((TEMP + 1500) * (TEMP + 1500))
            SENS2 = SENS2 + 11 * ((TEMP + 1500) * (TEMP + 1500)) / 2

    TEMP = TEMP - T2
    OFF = OFF - OFF2
    SENS = SENS - SENS2

    #Compensated values 
    pressure = ((((D1 * SENS) / 2097152) - OFF) / 32768.0) / 100.0
    cTemp = TEMP / 100.0

    print("Pressure : %.2f" %pressure)
    print("Temperature : %.2f" %cTemp)




