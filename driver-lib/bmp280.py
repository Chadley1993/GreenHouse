import smbus
import time
# Get I2C bus
bus = smbus.SMBus(1)
# BMP280 address, 0x76(118)
# Read data back from 0x88(136), 24 bytes


def get_temperature():
	b1 = bus.read_i2c_block_data(0x76, 0x88, 24)
	# Convert the data
	# Temp coefficents
	dig_T1 = b1[1] * 256 + b1[0]
	dig_T2 = b1[3] * 256 + b1[2]
	if dig_T2 > 32767:
		dig_T2 -= 65536
	dig_T3 = b1[5] * 256 + b1[4]
	if dig_T3 > 32767:
		dig_T3 -= 65536

	bus.write_byte_data(0x76, 0xF4, 0x27)
	# BMP280 address, 0x76(118)
	# Select Configuration register, 0xF5(245)
	# 0xA0(00) Stand_by time = 1000 ms
	bus.write_byte_data(0x76, 0xF5, 0xA0)
	time.sleep(0.5)
	# BMP280 address, 0x76(118)
	# Read data back from 0xF7(247), 8 bytes
	# Pressure MSB, Pressure LSB, Pressure xLSB, Temperature MSB, Temperature LSB
	# Temperature xLSB, Humidity MSB, Humidity LSB
	data = bus.read_i2c_block_data(0x76, 0xF7, 8)
	# Convert pressure and temperature data to 19-bits
	adc_p = ((data[0] * 65536) + (data[1] * 256) + (data[2] & 0xF0)) / 16
	adc_t = ((data[3] * 65536) + (data[4] * 256) + (data[5] & 0xF0)) / 16
	# Temperature offset calculations
	var1 = ((adc_t) / 16384.0 - (dig_T1) / 1024.0) * (dig_T2)
	var2 = (((adc_t) / 131072.0 - (dig_T1) / 8192.0) * ((adc_t)/131072.0 - (dig_T1)/8192.0)) * (dig_T3)
	t_fine = (var1 + var2)
	cTemp = (var1 + var2) / 5120.0
	return cTemp
