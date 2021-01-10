#!/usr/bin/python
import os, sys, sqlite3
from datetime import datetime
import time
import enum 
import math

import RPi.GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import Adafruit_DHT

#config for sensor that reads air temp and humitidy
sensor_temp = Adafruit_DHT.DHT22
sensor_temp_GPIO = 26 

# MCP config - used for windmeter
SPI_PORT   = 0
SPI_DEVICE = 0
mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
mcp_chl_winddir = 0

#GPIO config (GPIO 23 + 24 with pullup resistor)
rain_gpio = 24
wind_gpio = 23
GPIO.setmode(GPIO.BCM)

GPIO.setup(rain_gpio, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(wind_gpio, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Initialize variables and constants
DEBUG = True
SAMPLE_TIME = 60
PATH_TO_DB = "/var/db/weather.db"
TIC_EQUALS_KMH = 2.4
TIC_EQUALS_MM = 0.2794

# creating enumeration for wind directions using class 
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


def createDB():
    connection = sqlite3.connect(PATH_TO_DB)
    cursor = connection.cursor()
    # Create table for WEATHER DATA
    sql = "CREATE TABLE WEATHER( "\
            "recorded_datetime STRING,"\
            "temperature_degree_celsius FLOAT,"\
            "humitidy_in_percent FLOAT,"\
            "wind_direction STRING,"\
            "wind_speed_in_kmh FLOAT,"\
            "rain_last_min_in_mm FLOAT)" 

    cursor.execute(sql)
    connection.close()

# Callback-Funktion for tic counter windspeed sensor
def Interrupt_wind(channel):
  global Counter_Wind
  Counter_Wind = Counter_Wind + 1

# Callback-Funktion for tic counter rain sensor
def Interrupt_rain(channel):
  global Counter_Rain
  Counter_Rain = Counter_Rain + 1


# 1. Check if DB existis
if not os.path.exists(PATH_TO_DB):
    createDB()
    time.sleep(30)

# 2. Read sensors every minute and write to db
try:
    GPIO.add_event_detect(rain_gpio, GPIO.RISING, callback = Interrupt_rain,bouncetime = 500)
    GPIO.add_event_detect(wind_gpio, GPIO.RISING, callback = Interrupt_wind)  

    connection = sqlite3.connect(PATH_TO_DB)
    cursor = connection.cursor()

    while True:	
        now = datetime.now()
        Counter_Wind = 0
        Counter_Rain = 0
        # Count the tics for 60 sec
        time.sleep(SAMPLE_TIME)

        humidity, temperature = Adafruit_DHT.read_retry(sensor_temp, sensor_temp_GPIO)

        windsensor = mcp.read_adc(mcp_chl_winddir)
		# check only for main directions - div by 100, to group data
        winddir = windsensor // 100
        winddir_text = Wind_from(winddir).name
        windspeed = (TIC_EQUALS_KMH * Counter_Wind / SAMPLE_TIME) 

        amount_rain = (Counter_Rain * TIC_EQUALS_MM)

        if (DEBUG): 
            print(humidity,temperature,winddir_text,windspeed,amount_rain)
        
        sql = """INSERT INTO WEATHER(
            recorded_datetime,
            temperature_degree_celsius,
            humitidy_in_percent,
            wind_direction,
            wind_speed_in_kmh,
            rain_last_min_in_mm) 
            VALUES (?, ?, ?, ?, ?, ?);"""

        data = (now,temperature,humidity,winddir_text,windspeed,amount_rain)

        cursor.execute(sql,data)
        connection.commit()
        
except KeyboardInterrupt:
    connection.close()
    GPIO.remove_event_detect(wind_gpio)
    GPIO.remove_event_detect(rain_gpio)
    GPIO.cleanup()
    print ("\nBye")
