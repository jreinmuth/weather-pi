#!/usr/bin/python
import RPi.GPIO as GPIO
import datetime
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import enum 
  
# creating enumerations using class 
class Wind_from(enum.Enum): 
    #Wind directions
	north = 7
	north_east = 4
	east = 0
	south_east = 1
	south = 2
	south_west = 6
	west = 9
	north_west = 8
	#undefined
	five = 5
	three = 3


# MCP config
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
mcp_chl_winddir = 0

#GPIO config (GPIO 23 und 24 mit Pullup Widerstand)
rain_gpio = 24
wind_gpio = 23
GPIO.setmode(GPIO.BCM)

GPIO.setup(rain_gpio, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(wind_gpio, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Counter consts
Counter_10_Rain = 0
Counter_60_Rain = 0
Counter_360_Rain = 0
Counter_1440_Rain = 0
Counter_Wind = 0
tic_equals_kmh = 2.4
tic_equals_mm = 0.2794
sample_time = 30

# Callback-Funktion
def Interrupt_wind(channel):
  global Counter_Wind
  Counter_Wind = Counter_Wind + 1

# Callback-Funktion
def Interrupt_rain(channel):
  global Counter_10_Rain
  global Counter_60_Rain
  global Counter_360_Rain
  global Counter_1440_Rain
  Counter_10_Rain = Counter_10_Rain + 1
  Counter_60_Rain = Counter_60_Rain + 1
  Counter_360_Rain = Counter_360_Rain +1
  Counter_1440_Rain = Counter_1440_Rain +1

# Interrupt-Event hinzufuegen, steigende Flanke
GPIO.add_event_detect(rain_gpio, GPIO.RISING, callback = Interrupt_rain, bouncetime = 250)  
GPIO.add_event_detect(wind_gpio, GPIO.RISING, callback = Interrupt_wind, bouncetime = 250)  

# Endlosschleife, bis Strg-C gedrueckt wird
try:
  start_time_wind = time.time()
  start_time_rain_10 = time.time()
  start_time_rain_60 = time.time()
  start_time_rain_360 = time.time()
  start_time_rain_1440 = time.time()
  with open('data.txt','a') as f:
    while True:	
		now = time.time()
		sensor = mcp.read_adc(mcp_chl_winddir)
		winddir = sensor // 100
		windspeed = (tic_equals_kmh * Counter_Wind / sample_time)
		f.write('%s with %s km/h at %s\n' %(Wind_from(winddir), round(windspeed), datetime.datetime.now()))
		f.write('Counter Wind: %s \n' %Counter_Wind)
		f.write('Sensor value: %s \n' %sensor)
		# Print amount of rain for last 10 mins
		if now > start_time_rain_10 + 600:
			amount_rain = (Counter_10_Rain * tic_equals_mm)
			f.write('Amount of rain %s in last 10 min recorded at %s\n' %(amount_rain, datetime.datetime.now()))
			Counter_10_Rain = 0
			start_time_rain_10 = time.time()
		# Print amount of rain for last 60 mins
		if now > start_time_rain_60 + 3600:
			amount_rain = (Counter_60_Rain * tic_equals_mm)
			f.write('Amount of rain %s in last 60 min recorded at %s\n' %(amount_rain, datetime.datetime.now()))
			Counter_60_Rain = 0
			start_time_rain_60 = time.time()
		# Print amount of rain for last 6h
		if now > start_time_rain_360 + 21600:
			amount_rain = (Counter_360_Rain * tic_equals_mm)
			f.write('Amount of rain %s in last 6h recorded at %s\n' %(amount_rain, datetime.datetime.now()))
			Counter_360_Rain = 0
			start_time_rain_360 = time.time()
		# Print amount of rain for last 24h
		if now > start_time_rain_1440 + 86400:
			amount_rain = (Counter_1440_Rain * tic_equals_mm)
			f.write('Amount of rain %s in last 24h recorded at %s\n' %(amount_rain, datetime.datetime.time()))
			Counter_1440_Rain = 0
			start_time_rain_1440 = time.now()
		f.flush()
		Counter_Wind = 0 
		time.sleep(sample_time)
except KeyboardInterrupt:
  GPIO.cleanup()
  print "\nBye"


