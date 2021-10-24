import serial
import time
import picamera
from gps_module import GpsModule
from timeit import default_timer as timer
import RPi.GPIO as GPIO
import sys
from median import calc_median
import bme280
import subprocess
from gpiozero import CPUTemperature


#Configuration
port = "/dev/serial0"
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)

#Okreslenie po jakim czasie i na jakies wysokosci ma zostac otwarty stick
layout_stick_time = 9000
layout_stick_altitude = 25000
layoutInitiated = False
layoutInitDuration = 0

#Initialization
ser = serial.Serial(port, baudrate = 9600, timeout = 1)
gps_parser = GpsModule()
start_time = timer()
altList = []
averAlt = 0
cpu_temp = CPUTemperature()

#important variables
isStickOpen = False
stickOpen_timeup = False
stress_done_flag = True
bme_temp = 0
bme_pressure = 0
bme_humidity = 0
timer_var = 0
gpioDown = False
gsDown = False


# create file with logs
lcl_time = time.localtime()
lcl_time_now = time.strftime("%Y%m%d_%H%M%S", lcl_time)
logs_path = "/home/pi/logs_directory/" + lcl_time_now + ".txt"
layout_path = "/home/pi/logs_directory/shs_layout_logs/" + lcl_time_now + ".txt"

#camera
camera_detected = subprocess.run(["vcgencmd", "get_camera"], universal_newlines=True,  capture_output=True)
cameraOK = camera_detected.stdout.find("detected=1") > 0
print(cameraOK)
recordingOn = False
recordingStartTime = 0
lastCaptureTime = 0
captureInside = True
captureDeployed = False
if cameraOK:
    logs_file = open(logs_path, "a")
    logs_file.write(time.strftime("%H:%M:%S ") + camera_detected.stdout)
    logs_file.close()
    camera = picamera.PiCamera(resolution=(2592, 1944), framerate=30)
    #camera = picamera.PiCamera(resolution=(1920, 1020), framerate=30)
    camera.start_preview()
    camera.annotate_background = picamera.Color('black')
    camera.annotate_text = time.strftime("%H:%M:%S") + " Camera init photo "
    camera.capture('capture/init_'+time.strftime("%H%M%S")+'.jpg')
    caputerInside = True

while True:
    try:
        while True:
            data = ser.readline()
            time.sleep(0.1)
            gps_parser.parse_gps_data(data.decode())
            dec_str = data.decode()
            if dec_str[0:6] == "$GPGGA":
                timer_var = 0
                break
            timer_var = timer_var + 1
            if timer_var > 20:
                timer_var = 0
                break
    except:
        pass

    try:
        bme_temp, bme_pressure, bme_humidity = bme280.readBME280All()
    except:
        pass

    #TEST ALTITUDE 
    gps_parser.altSeaLevel = gps_parser.altSeaLevel + 50
    print("Sea Level: \r\n")
    print(gps_parser.altSeaLevel)

    #Wysokosc
    altList.append(float(gps_parser.altSeaLevel))
    if len(altList) > 3:
        averAlt = calc_median(altList)
        altList.clear()
 
    #Odliczanie czasu przez system
    end = timer()
    duration = int(end - start_time)

    if cameraOK:
        camera.annotate_text = time.strftime("%H:%M:%S")

    print(duration)

    #Robienie zdjec przed otwarciem SHS:
    if cameraOK and captureInside:
        if timer() - lastCaptureTime > 45:  # co 15 min
            lastCaptureTime = timer()
            camera.capture('capture/deployed_'+time.strftime("%H%M%S")+'.jpg')

    #Otwarcie SHS - nagrywanie 
    if ((duration > layout_stick_time) or (averAlt > layout_stick_altitude)) and isStickOpen == False:
        layoutInitiated = True
        stickOpenTimerStart = timer()
        if cameraOK:
            captureInside = False
            camera.resolution = (1920, 1080)
            camera.start_recording('capture/stickLayout'+time.strftime("%H%M%S")+'.h264')
            recordingOn = True
            recordingStartTime = timer()
            isStickOpen = True

    if layoutInitiated == True:
        layoutInitDuration = layoutInitDuration + 1
        
    #Otwarcie SHS-layout
    if layoutInitiated == True and layoutInitDuration > 5 and gpioDown == False and gsDown == False: #DODAC ZWIEKSZANIE TEJ ZMIENNEJ
        GPIO.output(12, GPIO.HIGH)
        isStickOpen = True
#        stickOpenTimerStart = timer()
        with open(layout_path, 'a') as layout_log_file:
            layout_log_file.write(f'SHS open at time : {gps_parser.time} - temperature : {bme_temp} - altitude : {gps_parser.altSeaLevel} \r\n')
        print("[TESTS DEBUG] - SHS open")
        print("[TESTS DEBUG] State of pin:")
        print(GPIO.input(12))
        gsDown = True
  
    if isStickOpen == True and stickOpen_timeup == False:
        stickOpenTimerStop = timer()
        if ((stickOpenTimerStop - stickOpenTimerStart) > 20):
            GPIO.output(12, GPIO.LOW)
            if cameraOK:
                camera.stop_recording()
                camera.resolution = (2592, 1944)  
                captureDeployed = True
                camera.capture('capture/deployed_'+time.strftime("%H%M%S")+'.jpg')
            stickOpen_timeup = True
            with open(layout_path, "a") as layout_log_file:
                layout_log_file.write(f'GPIO(12) Off at time : {gps_parser.time} - temperature : {bme_temp} - altitude : {gps_parser.altSeaLevel} \r\n')
            print("[TESTS DEBUG] - Wylaczono GPIO")
            gpioDown = True
    
    if averAlt > 28000 and stress_done_flag == False:
        stress_done_flag = True
        try:
            output = subprocess.run(['python3', 'stress.py'], capture_output=True)
            with open(log_stress.txt, 'a') as f_stress:
                f_stress.write(output)
        except:
            pass


    #Robienie zdjec po otwarciu SHS:
    if cameraOK and captureDeployed:
        if timer() - lastCaptureTime > 60:  # co 1 min
            lastCaptureTime = timer()
            camera.capture('capture/deployed_'+time.strftime("%H%M%S")+'.jpg')

    saveLogsTime = time.localtime()
    saveLogsTime_now = time.strftime("%H:%M:%S")
    #Zapis danych do pliku 

    with open(logs_path, "a") as logs_file:
        logs_file.write(f'{saveLogsTime_now } - temperature: {bme_temp} - cpu_temperature: {cpu_temp.temperature} - pressure: {bme_pressure} - humidity: {bme_humidity} - altitude: {gps_parser.altSeaLevel} - Coordinates : {gps_parser.latitude}  {gps_parser.longitude} \r\n')
    time.sleep(0.1)

#Clear GPIO
GPIO.cleanup()
