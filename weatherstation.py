#PiJuice weatherstation
#Nick Pestell 2015

import spidev
import time
import os
import serial
import sys
import Adafruit_DHT

# set delay
#delay = 5
delay = 86400

#setup for humidity sensor
sensor = 22
pin = 4

# open SPI bus
spi = spidev.SpiDev()
spi.open(0,0)

# read humidity sensor
def ReadHumidity(places):
	humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
	humidity = round(humidity,places)
	return humidity

# read on SPI port on specified channel
def ReadChannel(channel):
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) +adc[2]
	return data

# convert serial data to voltage reading
def ConvertVolts(data,places):
	volts = (data * 3.3)/float(1023)
#	volts = round(volts,places)
	return volts

# convert voltage to a percentage
def ConvertPercent(VoltReading,places,x):
	if x==1:
		Percentage = ((3.3-VoltReading)/3.3)*100
	elif x==2:
		Percentage = (VoltReading/3.3)*100
	Percentage=round(Percentage,places)
	return Percentage 

# convert temperature voltage to C
def ConvertTemp(TempVolts,places):
	Temp = (TempVolts/0.01)
	Temp = round(Temp,places)
	return Temp		

# send results SMS to specified mobile number
def SendMessage(LightReading,GasReading,TempReading,HumidityReading):
	SMS = "Light = " + str(float(LightReading)) + "%, Gas = " + str(float(GasReading)) + "%, Temp = " + str(float(TempReading)) + "C, Humidity = " + str(float(HumidityReading)) + "%"
	port.write("AT\r")
	response=port.readlines(None)
	print (response)
	port.write("AT+CMGF=1\r")
	response=port.readlines(None)
	print (response)
	port.write('AT+CMGS="+44**********"\r') #put your tellephone number in here 
	response=port.readlines(None)
	print (response)
	port.write(str(SMS)+"\r")
	port.write(chr(26))
	response=port.readlines(None)

#set sensor channels on MCP3008
light_channel = 0
gas_channel   = 1
temp_channel  = 2

# modem setup
print "Initialising Modem..."
port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=3.0)
port.write("AT\r")
response = port.readlines(None)
print (response)

while True:
#take humidity reading
	humidity_percentage = ReadHumidity(2)

#take light reading and convert to a percentage
	light_level      = ReadChannel(light_channel)
	light_volts      = ConvertVolts(light_level,2)
	light_percentage = ConvertPercent(light_volts,2)
	light_percentage = ConvertPercent(light_volts,2,2)

#take gas reading and convert to a percentage
	gas_level      = ReadChannel(gas_channel)
	gas_volts      = ConvertVolts(gas_level,2)
	gas_percentage = ConvertPercent(gas_volts,2)	
	gas_percentage = ConvertPercent(gas_volts,2,1)	

#take temperature reading convert to C
	temp_level  = ReadChannel(temp_channel)
	temp_volts  = ConvertVolts(temp_level,2)
	temp_C      = ConvertTemp(temp_volts,2)

# send results to phone in SMS
	SendMessage(light_percentage,gas_percentage,temp_C,humidity_percentage)

	print "______________________________"
	print("Humidity: {}%". format(humidity_percentage))  
	print("Light level: {}%". format(light_percentage))
	print("Gas  : {}%". format(gas_percentage))
	print("Temperature : {}C". format(temp_C))

	time.sleep(delay)



