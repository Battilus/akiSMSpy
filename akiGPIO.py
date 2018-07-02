# coding: utf8
import time
from pyA20.gpio import gpio, port


def setup_gpio():
	#initialize the gpio module
	gpio.init()

	#setup the port (same as raspberry pi's gpio.setup() function)
	gpio.setcfg(gp_led, gpio.OUTPUT)
	gpio.setcfg(boot_pin, gpio.OUTPUT)
	gpio.setcfg(smsError, gpio.OUTPUT)
	gpio.setcfg(statusLed, gpio.OUTPUT)
	gpio.setcfg(network_OK, gpio.OUTPUT)
	gpio.setcfg(Button0, gpio.INPUT)
	gpio.setcfg(Button1, gpio.INPUT)

	"""Enable pullup resistor"""
	gpio.pullup(Button0, gpio.PULLUP)
	gpio.pullup(Button1, gpio.PULLUP)

	gpio.output(gp_led, gpio.LOW)
	gpio.output(boot_pin, gpio.HIGH)
	gpio.output(smsError, gpio.LOW)
	gpio.output(statusLed, gpio.HIGH)
	gpio.output(network_OK, gpio.LOW)

def boot_L():
	gpio.output(boot_pin, gpio.LOW)
#****************
def boot_H():
	gpio.output(boot_pin, gpio.HIGH)
#****************
def smsErrorLed_L():
	gpio.output(smsError, gpio.LOW)
#****************
def smsErrorLed_H():
	gpio.output(smsError, gpio.HIGH)
#****************
def statusLed_L():
	gpio.output(statusLed, gpio.LOW)
#****************
def statusLed_H():
	gpio.output(statusLed, gpio.HIGH)
#****************
def networkOKled_L():
	gpio.output(network_OK, gpio.LOW)
#****************
def networkOKled_H():
	gpio.output(network_OK, gpio.HIGH)
#****************
def modOFF():
	boot_H()
#****************
def modON():
	boot_L()
#****************

#Variables
gp_led = port.PA10
boot_pin = port.PA19
smsError = port.PA8
statusLed = port.PA7
network_OK = port.PA3
Button0 = port.PA1
Button1 = port.PA0

#init
setup_gpio()