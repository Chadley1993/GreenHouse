import time
import datetime

from drivers import bmp280


def calculate_sleeptime(curr_time, freq):
    return (freq - curr_time % freq) * 60


def main():
    freq = 20
    boot_time = time.ctime()
    t0_minutes = int(boot_time[14:16]) + int(boot_time[17:19]) / 60
    init_sleep = calculate_sleeptime(t0_minutes, freq)
    time.sleep(init_sleep)

    while True:
        cTemp = bmp280.get_temperature()
        timestamp = time.ctime()
        f = open('/home/pi', 'a+')
        f.write(timestamp + ',' + "{:.1f}\n".format(cTemp))
        f.close()
        curr_time = time.ctime()
        t_minutes = int(curr_time[14:16]) + int(curr_time[17:19]) / 60
        target_sleep = calculate_sleeptime(t_minutes, freq)
        time.sleep(target_sleep)


if __name__ == '__main__':
    main()
