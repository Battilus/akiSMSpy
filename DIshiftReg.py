# coding: utf8
from pyA20.gpio import gpio
from pyA20.gpio import port
import time

def set_gpio():
	#initialize the gpio module
	gpio.init()

	#setup the port (same as raspberry pi's gpio.setup() function)
	gpio.setcfg(CLKpin, gpio.OUTPUT)
	gpio.setcfg(LATCHpin, gpio.OUTPUT)
	gpio.setcfg(DATApin, gpio.INPUT)

	"""Enable pullup resistor"""
	#gpio.pullup(button, gpio.PULLUP)
	#gpio.pullup(button_0, gpio.PULLDOWN)

	gpio.output(CLKpin, gpio.LOW)
	gpio.output(LATCHpin, gpio.LOW)
	
#****************
def CLK_L():
	gpio.output(CLKpin, gpio.LOW)
#****************
def CLK_H():
	gpio.output(CLKpin, gpio.HIGH)
#****************
def LATCH_L():
	gpio.output(LATCHpin, gpio.LOW)
#****************
def LATCH_H():
	gpio.output(LATCHpin, gpio.HIGH)
#****************
def DATAread():
	return gpio.input(DATApin) 
#****************

def readDataFromPort(in_DI, in_BIT):
	LATCH_L()
	time.sleep(0.0003)	#300ms
	LATCH_H()

	for i in range(in_BIT-1,-1,-1):
		in_DI[i]=DATAread()
		CLK_L()
		time.sleep(0.0001)	#100ms
		CLK_H()

	return in_DI

#****************
#Variables
DATApin = port.PC0	#19
CLKpin = port.PC1	#21
LATCHpin = port.PC2	#23
#init
set_gpio()

