# coding: utf8
import time, datetime
import serial
import akiGPIO as io


#Serial init
def get_serial():
	"""Serial init ttyS1 COM2"""
	seri = serial.Serial("/dev/ttyS1", baudrate=115200, timeout=1)
	seri.flush()
	return seri

def command(in_comm):
	ser.write(in_comm +' \r\n')
	time.sleep(0.1)

def readmod():
	return ser.read(ser.inWaiting())

def setGSM():	#Set GSM mode...
	command('AT+CMGF=1')	#Send TEXT mode
	command('AT+CSCS="GSM"')
	buff = readmod()
	if 'ERROR' in buff: return -1
	else: return 1

def setPDU():	#Set PDU mode...
	command('AT+CMGF=0')	#Send PDU mode
	buff = readmod()
	if 'ERROR' in buff: return -1
	else: return 1

def modPwrOFF():	#Modem power OFF...
	io.statusLed_H()
	io.modOFF()
	time.sleep(0.5)
	command('AT+CPWROFF')

	time.sleep(5)

def sendSMS(num, txt):	#Просто шлет смс
	ser.write('AT+CMGS="'+ num + '"' +' \r\n')
	time.sleep(1)
	ser.write(txt + chr(26))	#end symbol 1A ascii(26)

def sendSMScheck(num, txt):	#Отсылает смс и проверяет статус отправки
	ser.write('AT+CMGS="'+ num + '"' +' \r\n')
	time.sleep(1)
	ser.write(txt + chr(26))	#end symbol 1A ascii(26)
	interation = 0
	while True:
		buff = readmod()
		if '+CMGS:' in buff:
			x = sfindn('+',buff)
			if buff != None: return buff[x:x+8]
			else: return 'EMPTY'
		elif 'ERROR' in buff:	#Если смс не отправилось, то возвращаем ERROR
			return 'ERROR'	
		
		interation += 1	#Если отет не пришел, то читаем снова
		
		if interation >= 30:	#Если буффер молчит в течении 30 запросов (интервал 1 сек.), то возвращаем ошибку
			return 'EMPTY'
		else:
			time.sleep(0.5)

def sfindn(x_in, str_in):	#Ищет символ и возвращает номер ячейки массива, в которой хранится нужный нам символ(x_in)
	k_x = len(x_in) #длина искомого
	k_s = len(str_in)	#длина массива в котором ищем
	for i in range(k_s):
		k = i + k_x
		if x_in == str_in[i:k]: return i	#Возвращаем номер ячейки массива, в котором нашли искомый символ
		if i >= k_s: return -1	#None

def getDatetime():	#Запросить дату и время из системы
	rtc_m = datetime.datetime.now()	#Создаем класс для даты и времени
	return (str(rtc_m.year)+'-'+str(rtc_m.month)+'-'+str(rtc_m.day)+' '
			+str(rtc_m.hour)+':'+str(rtc_m.minute)+':'+str(rtc_m.second))

def sysGetDatetimeToMod():	#Запросить дату и время из системы и записать его в модем
	rtc_m = datetime.datetime.now()	#Создаем класс для даты и времени
	gmt = 3 #Часовой пояс (GMT+03)
	command('AT+CCLK="'+str(rtc_m.year-2000)+'/'+str(rtc_m.month)+'/'+str(rtc_m.day)+','
			+str(rtc_m.hour)+'::'+str(rtc_m.minute)+':'+str(rtc_m.second)+'+0'+str(gmt)+'"')

def modSTART_m590(sleep=3):	#Strat modem (for M590)
	modPwrOFF()	#предварительно выключаем для гарантированного старта
	io.modON()	#Modem ON
	time.sleep(sleep) #sleep 3sec.

	check = 0
	while True:
		io.statusLed_H()	#Led BLUE ON
		time.sleep(0.5)
		buff = readmod()
		if '+PBREADY' in buff:
			io.statusLed_L()	#Led BLUE OFF
			return 1
		else: check += 1
		if check == 60:	#Starting error!
			io.statusLed_H()	#Led BLUE ON
			return -1
		io.statusLed_L()	#Led BLUE OFF
		time.sleep(0.5)

def modSTART_D800(sleep=3):	#Strat modem (for D800)
	modPwrOFF()
	io.modON()	#Modem ON
	time.sleep(sleep)	#sleep 3sec.

	check = 0
	while True:
		io.statusLed_H()	#Led BLUE ON
		time.sleep(0.5)
		command('AT')
		buff = readmod()
		if 'OK' in buff:
			io.statusLed_L()	#Led BLUE OFF
			return 1
		else: check += 1
		if check == 10:	#Starting error!!
			io.statusLed_H()	#Led BLUE ON
			return -1
		io.statusLed_L()	#Led BLUE OFF
		time.sleep(0.5)

def mod_init():	#Modem init...
	command('ATE0')	#ECHO OFF
	buff = readmod()	#Clear buff
	command('AT')
	buff = readmod()
	if 'OK' in buff:
		x = setGSM()
		if x == 1: return 1	#OK
		else: return -1	#ERROR
	else: return -1	#ERROR

def setNet():	#Ждем регистрации в сети. если в течении 60 сек. не зарегестрировался то ошибка
	#Waiting registration in GSM...
	tmp = 0	#60 раз читаем буфер раз в сек. и при успешном ответе выходим. если за 60 попыток не было, то ERROR
	while True:
		io.statusLed_H()	#Led BLUE ON
		time.sleep(0.5)
		command('AT+CREG?')	#Without print
		buff = readmod()
		if '+CREG: 0,1' in buff:
			command('AT+CSQ')
			buff = readmod()
			io.statusLed_L()	#Led BLUE OFF
			return 1
		else:
			tmp += 1
			io.statusLed_L()	#Led BLUE OFF
			time.sleep(0.5)
		if tmp == 60:
			io.statusLed_H()	#Led BLUE ON
			return -1	#GSM connection ERROR!

def modREBOOT():	#Modem reboot...
	tmpx = modSTART_m590(30)	#pwr off/on
	if tmpx == 1:	#if reboot ok: init
		sysGetDatetimeToMod()
		buff = readmod()	#CLEAR BUFFER
		tmp = mod_init()
		if tmp == -1: return -1
		else:
			tmp = setNet()
			if tmp == -1: return -1
			else: return 1	#if ALL is OK
	else: return -1

def modSTARTUP():	#Только для старта при начальном пуске
	#Modem reboot...
	tmpx = modSTART_m590()	#pwr off/on
	if tmpx==1:	#if reboot ok: init
		sysGetDatetimeToMod()
		buff = readmod()	#CLEAR BUFFER
		tmp = mod_init()
		if tmp == -1: return -1
		else:
			tmp = setNet()
			if tmp == -1: return -1
			else: return 1	#if ALL is OK
	else: return -1

def getTimeFromModem():
	buff = command('AT+CCLK?')
	buff = readmod()
	time_x = sfindn('+',buff)
	if time_x!=None: time = str(buff[time_x+8:time_x+25])
	else: time=" "
	return time

def getTimeFromModem_str():
	buff = command('AT+CCLK?')
	buff = readmod()
	time_x = sfindn('+',buff)
	if time_x!=None: time = (str(buff[time_x+8:time_x+10])+'.'+str(buff[time_x+11:time_x+13])+'.'+str(buff[time_x+14:time_x+16])+'('+str(buff[time_x+17:time_x+19])+'_'+str(buff[time_x+20:time_x+22])+'_'+str(buff[time_x+23:time_x+25])+')') #buff[time_x+8:time_x+25]
	else: time=" "
	return time

def sendSMS_fl_last(flag, num, txt, err):	#Отправляет смс, проверяет статус отправки и моргает светодиодом
	if flag==1:
		print("Send SMS: ",txt)
		buff = sendSMScheck(num, txt)
		if '+CMGS' in buff:
			io.smsErrorLed_L()
			return 0, 0
		else:
			io.smsErrorLed_H()
			return 1, err+1
	else: return 0, err

def sendSMS_fl(flag, num, txt, err):	#Отправляет смс, проверяет статус отправки и моргает светодиодом
	if flag==1:
		for iNum in num:
			print("Send SMS: ",iNum,txt)
			buff = sendSMScheck(iNum, txt)
			if '+CMGS' in buff:
				io.smsErrorLed_L()
				flag = 0
				err = 0
			else:
				io.smsErrorLed_H()
				flag = 1
				err += 1
	return flag, err

def checkSignal():
	command('AT+CSQ')	#Если зарегестрированв сети, то запрашиваем уровень сигнала
	buff = readmod()
	x = sfindn('+',buff)	#Фильтруем лишний мусор, что бы вывести результат в консоль
	if x!=None: #Защищаемся от вывода ошибки, если буфер внезапно оказался пуст		
		dec = (float(buff[x+6])) * 10
		if buff[x+7]!=',':	#Защита от 8,99
			ed = (float(buff[x+7]))
			fDec = (float(buff[x+9])) / 10
		else:
			ed = 0
			fDec = (float(buff[x+8])) / 10

		result = (dec + ed + fDec)
		
		if result >= 7.0 and result < 90.0: io.networkOKled_H() 
		else: io.networkOKled_L()
	else: io.networkOKled_L()

def checkModem():	# 1 - ОК	2 - reboot	-1 - bad check
	buff = readmod()	#Clear buffer
	buff = ""

	io.statusLed_H()

	command('AT')
	command('AT+CREG?')
	buff = readmod()

	if 'OK' in buff:
		if '+CREG: 0,1' in buff:
			checkSignal()
			io.statusLed_L()
			return 1	# ALL OK
		else:
			io.statusLed_H()
			return -1
	else:
		io.statusLed_H()
		return -1

	if '+PBREADY' in buff:	return 2	#Если вдруг модем перезапустился, то ребутаем и инициализируемся снова


#init
ser = get_serial()
		