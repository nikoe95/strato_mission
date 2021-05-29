from MS5611 import MS5611

ms5611_sensor = MS5611()
ms5611_sensor.start_connection()
ms5611_sensor.read_calibration_data()

while True:
    ms5611_sensor.read_data()
