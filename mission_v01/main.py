from MS5611 import MS5611
from mpu6050 import mpu6050
import time
from datetime import datetime

#Create MS5611 module
ms5611_sensor = MS5611()

#MS5611 calibration
ms5611_sensor.start_connection()
ms5611_sensor.read_calibration_data()

#create MPU6050 module
mpu6050_sensor = mpu6050(0x68)

#MPU6050 calibration
mpu6050_sensor.set_accel_range(mpu6050_sensor.ACCEL_RANGE_2G)
mpu6050_sensor.set_gyro_range(mpu6050_sensor.GYRO_RANGE_250DEG)


while True:

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("\nCurrent Time =", current_time)

    ms5611_sensor.read_data()
    accel_data = mpu6050_sensor.get_accel_data(True)
    gyro_data = mpu6050_sensor.get_gyro_data()

    print("Acc X - " + str(accel_data['x']))
    print("Acc Y - " + str(accel_data['y']))
    print("Acc Z - " + str(accel_data['z']))

    print("Gyro X - " + str(gyro_data['x']))
    print("Gyro Y - " + str(gyro_data['y']))
    print("Gyro Z - " + str(gyro_data['z']))

    time.sleep(1)

