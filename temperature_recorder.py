import time
import bmp280

while True:
    cTemp = bmp280.get_temperature()
    timestamp = time.ctime()
    f = open('/home/pi/temperature.db', 'a')
    f.write(timestamp + ',' + "{:.1f}\n".format(cTemp))
    f.close()
    time.sleep(60 * 12)
