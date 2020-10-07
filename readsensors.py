import smbus
import Adafruit_MCP3008
import Adafruit_GPIO.SPI as SPI
import time
import sys
import Adafruit_DHT

#config for sensor that reads air temp and humitidy
sensor_temp = Adafruit_DHT.DHT22
sensor_temp_GPIO = 4 

#config sensor that reads soil moisture
SPI_PORT = 0
SPI_DEVICE = 0
mcp3008_channel = 7
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

#define ranges - need calibration for different soil types
dry = 650
flooding = 225
got_water_today = 375
almost_dry = 550
still_sufficient_water = 470

#config sensor that reads soil moisture
I2C_DEVICE = 0x23  # Default device I2C address
bus = smbus.SMBus(1)  

# Define some constants from the datasheet solar sensor
MODE_HIGH_RES = 0x10  # Start measurement at 1lx resolution

#helper function
def convertToNumber(data):
  # Simple function to convert 2 bytes of data
  result = (data[1] + (256 * data[0])) / 1.2
  return (result)


#read data from sensors
humidity, temperature = Adafruit_DHT.read_retry(sensor_temp, sensor_temp_GPIO)
soil_moisture = mcp.read_adc(mcp3008_channel)
lux = convertToNumber(bus.read_i2c_block_data(I2C_DEVICE, MODE_HIGH_RES))

#get current time
now = time.strftime("%c")

#printout values to stdout
print now,",",'{0:0.1f}'.format(temperature),",",'{0:0.1f}'.format(humidity),",",'{0:0.0f}'.format(lux),",",soil_moisture
