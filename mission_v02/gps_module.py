class GpsModule:
    def __init__(self):
        self.time = 0
        self.latitude = 0
        self.longitude = 0
        self.altSeaLevel = 0

    def parse_gps_data(self, data):
        if data[0:6] == "$GPGGA":
            sdata = data.split(",")
            if sdata[2] == '' :
                #print("no satellite data available")
                return
            #print("Obliczanie")
            self.time = sdata[1][0:2] + ":" + sdata[1][2:4] + ":" + sdata[1][4:6]
            self.latitude = self.decode_coordinates(sdata[2], sdata[3])
            self.longitude = self.decode_coordinates(sdata[4], sdata[5])
            self.altSeaLevel = sdata[9] #Antenna altitude above/below mean sea level

            #print(f'Time - {self.time} Coordinates - {self.latitude} {self.longitude} H.A.S {self.altSeaLevel}')

    def decode_coordinates(self, coordinates, direction):
        coord = coordinates.split(".")
        head = coord[0]
        tail = coord[1]
        degrees = head[0:-2]
        minutes = head[-2:]
        return degrees + "°" + minutes + "'" + tail + "''" + "(" + direction + ")"
