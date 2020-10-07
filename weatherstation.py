#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008

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
start_at = time.time()
timeslot_10_in_secs = 60*10
timeslot_60_in sec = 60*60
Counter_10_Rain = 0
Counter_60_Rain = 0
Counter_60_Wind = 0
tic_equals_kmh = 2.4
tic_equals_mm = 1.6

# Callback-Funktion
def Interrupt_wind(channel):
  global Counter_60_Wind
  now = time.time()
  if now > start_at + timeslot_60_in_secs:
      print "Counter reset for wind, value was ", Counter_60_Wind * tic_equals_kmh
      Counter_60_Wind = 0
  Counter_60_Wind = Counter_60_Wind + 1
  print "Windspeed (km/h) " + str(Counter_Wind * tic_equals_kmh)

# Callback-Funktion
def Interrupt_rain(channel):
  global Counter_10_Rain Counter_60_Rain
  now = time.time()
  if now > start_at + timeslot_10_in_secs:
      print "10 min Counter reset for rain, value was ", Counter_10_Wind * tic_equals_mm
      Counter_10_Wind = 0
  if now > start_at + timeslot_60_in_secs:
      print "60 min Counter reset for rain, value was ", Counter_60_Wind * tic_equals_mm
      Counter_60_Wind = 0
  Counter_10_Rain = Counter_10_Rain + 1
  Counter_60_Rain = Counter_60_Rain + 1
  print "Rain (mm/10min) " + str(Counter_10_Rain * tic_equals_mm)
  print "Rain (mm/h) " + str(Counter_60_Rain * tic_equals_mm)

# Interrupt-Event hinzufuegen, steigende Flanke
GPIO.add_event_detect(rain_gpio, GPIO.RISING, callback = Interrupt_rain, bouncetime = 250)  
GPIO.add_event_detect(wind_gpio, GPIO.RISING, callback = Interrupt_wind, bouncetime = 250)  

# Endlosschleife, bis Strg-C gedrueckt wird
try:
  while True:
    winddir = mcp.read_adc(mcp_chl_winddir)
    print('Direction of wind' , winddir)
    # Pause for half a second.
    time.sleep(0.5)
except KeyboardInterrupt:
  GPIO.cleanup()
  print "\nBye"
