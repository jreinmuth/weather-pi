#!/usr/bin/python
import RPi.GPIO as GPIO
from datetime import datetime, timedelta as delta
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import enum 
import math
import Adafruit_DHT

#config for sensor that reads air temp and humitidy
sensor_temp = Adafruit_DHT.DHT22
sensor_temp_GPIO = 26 

  
# creating enumerations using class 
class Wind_from(enum.Enum): 
    #Wind directions
	north = 0
	north_east = 1
	east = 2
	south_east = 6
	south = 9
	south_west = 8
	west = 7
	north_west = 4
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
#every 5 sec 
sample_time = 5
def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)

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
start_time_wind = datetime.now()
start_time_rain_10 = datetime.now()
start_time_rain_60 = datetime.now()
start_time_rain_360 = datetime.now()
start_time_rain_1440 = datetime.now()

GPIO.add_event_detect(rain_gpio, GPIO.RISING, callback = Interrupt_rain,bouncetime = 500)  
GPIO.add_event_detect(wind_gpio, GPIO.RISING, callback = Interrupt_wind)  

with open('debug.log','a') as dbg:
	# Endlosschleife, bis Strg-C gedrueckt wird
	try:
		with open('wind.txt','a') as f:
			while True:	
				dbg.write('%s : Counter Rain (10,60,360,1440) %s , %s , %s , %s\n' %( datetime.now(), Counter_10_Rain, Counter_60_Rain, Counter_360_Rain, Counter_1440_Rain))
				dbg.write('%s : Counter Wind  %s \n' %( datetime.now(), Counter_Wind))
				dbg.flush()
				now = datetime.now()
				humidity, temperature = Adafruit_DHT.read_retry(sensor_temp, sensor_temp_GPIO)
				dbg.write('%s : Air temp %s \n' %( datetime.now(), temperature))
				dbg.write('%s : Air humidity %s \n' %( datetime.now(), humidity))
				dbg.flush()
				sensor = mcp.read_adc(mcp_chl_winddir)
				winddir = sensor // 100
				dbg.write('%s : Wind direction %s \n' %( datetime.now(), winddir))
				sec_since_lasttime_wind = (now - start_time_wind).total_seconds()
				dbg.write('%s : Secs Wind  %s \n' %( datetime.now(), sec_since_lasttime_wind))
				windspeed = (tic_equals_kmh * Counter_Wind / sec_since_lasttime_wind)
				sec_since_lasttime_wind = datetime.now()
				Counter_Wind = 0 
				start_time_wind = datetime.now()
				f.write('%s with %s km/h at %s\n' %(Wind_from(winddir),normal_round(windspeed), datetime.now()))
				# Print amount of rain for last 10 mins
				if now > start_time_rain_10 + delta(seconds=600):
					amount_rain_10 = (Counter_10_Rain * tic_equals_mm)
					with open('rain_10_mins.txt','a') as rain_10:
						rain_10.write('Amount of rain %s in last 10 min recorded at %s\n' %(normal_round(amount_rain_10), datetime.now()))
					Counter_10_Rain = 0
					start_time_rain_10 = datetime.now()
					with open('air.txt','a') as air:
						air.write('Air (Temp., Humi.): %s , %s at %s\n' %(normal_round(temperature),normal_round(humidity), datetime.now()))
				# Print amount of rain for last 60 mins
				if now > (start_time_rain_60 + delta(seconds=3600)):
					amount_rain_60 = (Counter_60_Rain * tic_equals_mm)
					with open('rain_60_mins.txt','a') as rain_60:
						rain_60.write('Amount of rain %s in last 60 min recorded at %s\n' %(normal_round(amount_rain_60), datetime.now()))
					Counter_60_Rain = 0
					start_time_rain_60 = datetime.now()
				# Print amount of rain for last 6h
				if now > (start_time_rain_360 + delta(seconds=21600)):
					amount_rain_360 = (Counter_360_Rain * tic_equals_mm)
					with open('rain_6_h.txt','a') as rain_360:
						rain_360.write('Amount of rain %s in last 6h recorded at %s\n' %(normal_round(amount_rain_360), datetime.now()))
					Counter_360_Rain = 0
					start_time_rain_360 = datetime.now()
				# Print amount of rain for last 24h
				if now > (start_time_rain_1440 + delta(seconds=86400)):
					amount_rain_1440 = (Counter_1440_Rain * tic_equals_mm)
					with open('rain_24_h.txt','a') as rain_1440:
						rain_1440.write('Amount of rain %s in last 24h recorded at %s\n' %(normal_round(amount_rain_1440), datetime.now()))
					Counter_1440_Rain = 0
					start_time_rain_1440 = datetime.now()
				f.flush()
				time.sleep(sample_time)
	except KeyboardInterrupt:
		GPIO.cleanup()
		print ("\nBye")
