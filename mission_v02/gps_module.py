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
                print("no satellite data available")
                return
            time = sdata[1][0:2] + ":" + sdata[1][2:4] + ":" + sdata[1][4:6]
            latitude = self.decode_coordinates(sdata[2], sdata[3])
            longitude = self.decode_coordinates(sdata[4], sdata[5])
            altSeaLevel = sdata[9] #Antenna altitude above/below mean sea level

            print(f'Time - {time} Coordinates - {latitude} {longitude} H.A.S {altSeaLevel}')

    def decode_coordinates(self, coordinates, direction):
        coord = coordinates.split(".")
        head = coord[0]
        tail = coord[1]
        degrees = head[0:-2]
        minutes = head[-2:]
        return degrees + "°" + minutes + "'" + tail + "''" + "(" + direction + ")"
