import serial
import time
from gps_module import GpsModule

port = "/dev/serial0"

def parseGPS(data):
    if data[0:6] == "$GPGGA":
        sdata = data.split(",")
        if sdata[2] == '' :
            print("no satellite data available")
            return
        print("---Parsing GPGAA---")
        time = sdata[1][0:2] + ":" + sdata[1][2:4] + ":" + sdata[1][4:6]
        #lat = decode(sdata[3]) #latitude
        latitude = decode_coordinates(sdata[2], sdata[3])
        longitude = decode_coordinates(sdata[4], sdata[5])
        altSeaLevel = sdata[9] #Antenna altitude above/below mean sea level

        print(f'Time - {time} Coordinates - {latitude} {longitude} H.A.S {altSeaLevel}')

def decode_coordinates(coordinates, direction):
    coord = coordinates.split(".")
    head = coord[0]
    tail = coord[1]
    degrees = head[0:-2]
    minutes = head[-2:]
    return degrees + "°" + minutes + "'" + tail + "''" + "(" + direction + ")"

print("Receiving GPS data")
set = serial.Serial(port, baudrate = 9600, timeout = 1)
while True:
    #data = set.readline()
    data = "$GPGGA,134658.00,5106.9792,N,11402.3003,W,2,09,1.0,1048.47,M,-16.27,M,08,AAAA*60"
    #print(data)
    #parseGPS(data)
    gps_parser = GpsModule()
    gps_parser.parse_gps_data(data)
    time.sleep(0.5)
