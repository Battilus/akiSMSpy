# coding: utf8
import time, datetime
import threading
import DIshiftReg as mDI
from akiMODEM import *

class ThreadDI(threading.Thread):

	def __init__(self, bits, t_delay, t_filter, DIflags):
		threading.Thread.__init__(self)
		self.bits = bits	#количество используемых входов (8 или 16) (может будет и больше, если решим добавить в будущем модули)
		self.DI = [0] * bits	#актуальное состояние входов 
		self.invers = [0] * bits	#режим работы входов (обычниый или инвертирован)
		self._DIxt = [0] * bits	#количество успешных опросов (раз в t_delay) входа (для фильтрации дребезга)
		self._last = [0] * bits	#предидущее состояние входа
		self.chEN = [0] * bits	#разрешение на изменение флага отправки смс (для блокировки ненужных входов и избежания отпраки ложных смс)
		self.timeS = [''] * bits	#актуальное время на момент срабатывания входа (для отправки по смс)
		self.DIresult = DIflags	#флаги для отправки СМС (отфильтрованное состояние входа (возвращается в 0 после успешной отправки СМС))
		self.cycle = t_delay #интервалы опроса входов
		self.tDIdelay = t_filter #sec время для фильтрации входа
		self.k__cycle = 0	#количество циклов в течении которых на входе должно быть True
		self.time_k = self.cycle * 1000
		self.th_start = True	#запускает while в потоке

	def run(self):
		print("Thread Run!")
		self._k_cycle()
		while self.th_start:
			self.DI = mDI.readDataFromPort(self.DI, self.bits)
			for i in range(self.bits):
				if ((self.DI[i] == 1 and self.invers[i] == 0) or (self.DI[i] == 0 and self.invers[i] == 1)) and self.DIresult[i] == 0 and self._last[i] == 0 and self.chEN[i] == 1: 
					self._DIxt[i] += 1
					# print("{}: {}".format(i, self._DIxt[i]))
				elif (self.DI[i] == 0 and self.invers[i] == 0) or (self.DI[i] == 1 and self.invers[i] == 1): 
					self._last[i] = 0
					self._DIxt[i] = 0
				
				if self._DIxt[i] >= self.k__cycle and self.chEN[i] == 1 and self._last[i] == 0:	#если на входе реально есть сигнал(т.е. на входе непрерывно висит сигнал в течении заданного времени), то:
					self.timeS[i] = getDatetime()	#записываем актуальное время срабатывания входа
					self.DIresult[i] = 1	#пишем флаг для отправки смс					
					self._DIxt[i] = 0	#обновляем счетчик фильтрации входа
					self._last[i] = 1	#фиксим состояние как предидущее, пока на входе не пропадет сигнал
	
			time.sleep(self.cycle)
		print("Thread Stoped")

	def tstop(self):
		self.th_start = False
		print("Kill!")

	def _k_cycle(self):
		self.k__cycle = round(((self.tDIdelay * self.time_k) * self.cycle) - 1)

	def _invers(self, in_DIres, in_invers):
		if in_DIres==1:
			if in_invers==1: in_DIres = 0
			else: in_DIres = 1
		else:
			if in_invers==1: in_DIres = 1
			else: in_DIres = 0
		return in_DIres


def main():

	#Variables
	error = 0	#Флаг для ребута модема (если больше трех)

	#sms flags	(Флаги для отправки смс)
	_fs_start = 1	#Для отправки после успешного старта и инициализации
	_fs_reboot = 0	#Для отправки после успешного ребута
	_fs_alive = 0	#Для отправки смс о том что все в работе

	#log GLOBAL
	_fl_reboots = 0	#Количество ребутов
	_fl_errors = 0	#Количество ошибок
	_fl_sms_error = 0	#Количество неудачных попыток отправки СМС
	_fl_time = getDatetime()	#Актуальное время

	reboot_smsf_err = 0	#Флаг для ребута при неуспешной отправки sms (ребут если >= 3)
	tmpCheck = 0
	tic = 0	#Учет итераций в рантайме
	
	check_ints = 0	#Общее количество чеков для отправки лога	(УБРАТЬ НАХРЕН!!!)
	goodCheck = 0	#Количество успешных чеков для отправки лога (УБРАТЬ НАХРЕН!!!)
	inter = 0	#считаем итерации для Alive (ПЕРЕДЕЛАТЬ НА НОРМ ТАЙМЕР СУТОК)

	#ПОУБИРАТЬ ПОТОМ НАХРЕН!!! и обращаться напрямую к t1.DIresult и t1.timeS
	global BIT
	global _fs_DI
	timeS = [''] * BIT
	print("Main Run!")
	while True:

		t1.chEN = sendEN
		t1.invers = DIinvers
		_fs_DI = t1.DIresult
		timeS = t1.timeS

		if _fs_start or _fs_alive or _fs_reboot: _fl_time = getDatetime()

		#Системные SMS сообщения
		_fs_start, reboot_smsf_err = sendSMS_fl((_fs_start and smsStartup_EN==1), smsNumbers, "Modem: STARTUP!"+'\n'+str(_fl_time), reboot_smsf_err)
 		_fs_reboot, reboot_smsf_err = sendSMS_fl((_fs_reboot and smsReboot_EN==1), smsNumbers, "Modem REBOOTED! ("+str(check_ints)+', '+str(goodCheck)+')'+'\n'+str(_fl_time)+'\n'+"Reboots: "+str(_fl_reboots), reboot_smsf_err)
		_fs_alive, reboot_smsf_err = sendSMS_fl((_fs_alive and smsAlive_EN==1), smsNumbers, "I'm alive!!!("+str(check_ints)+', '+str(goodCheck)+')'+'\n'+str(_fl_time), reboot_smsf_err)

		#SMS сообщения со входов DI
		for i in range(4):	#При полной сборке всех 16-ти входов заменить 4 на BIT (иначе будет слать кучу ненужных смс на этапе разработки)
			_fs_DI[i], reboot_smsf_err = sendSMS_fl(_fs_DI[i], smsNumbers, smstxtDI[i]+'\n'+str(timeS[i]), reboot_smsf_err)

		if reboot_smsf_err!=0 and reboot_smsf_err!=None: _fl_sms_error += reboot_smsf_err

 		buff = readmod()	#READ BUFFER

 		if ('+PBREADY' in buff) or tmpCheck==2:	#Если вдруг модем перезапустился, то ребутаем и инициализируемся снова
 			io.statusLed_H()
 			error=3

		#==========================
		if tic>=49:	#RUNTIME 5 sec.
			tic=0
			tmpCheck = checkModem()
			
			check_ints += 1
			if tmpCheck == 1:	#Check OK
				goodCheck += 1

			if tmpCheck == -1:	#Check ERROR
				error+=1
				for i in range(3):	#Быстро мигаем светодиодом 3 раза
					io.statusLed_L()
					time.sleep(0.1)
					io.statusLed_H()
					time.sleep(0.1)
				_fl_errors+=1#################

		if reboot_smsf_err>=3:	#Если три раза сообщение не отправилось, то ребутаем модем
			reboot_smsf_err=0	#Сбрасываем флаг что бы повторно не ребутать, и пробуем опять три раза смснуть
			error=3	#Когда этот флаг >= 3, то ребутаем

		while error>=3:	#Данная секция отвечает за ребут
			error=0
			_fl_reboots+=1#######################
			tmp = modREBOOT()
			if tmp == -1: error=3	#если неудачно, то ребутаем до усрачки
			else:
				error=0
				_fs_reboot=1
				break
			time.sleep(1)

		time.sleep(0.1)
		tic+=1


try:
	#Variables and init
	BIT = 8	#Количество входов
	_fs_DI = [0] * BIT	#Флаги факта активного состояния входов (для отправки смс)
	smstxtDI = [""] * BIT
	#*********************

	#Внешние переменные (для сервера)
	sendEN = [0] * BIT	#флаг блокировки изменеия флагов отправки смс сообщений
	DIinvers = [0] * BIT	#делает инверсной работу входов
	t_filterDI = 3 #время фильтрации дребезга контактов
	_fs_alive = 0
	smsAlive_EN = 0
	smsReboot_EN = 1
	smsStartup_EN = 0
	smsNumbers = ["+79184778396"]	#Справочник номеров телефонов

	#Текст смс привязанный к входам (индекс к индексу)
	txtDI = ["DI0 some text...",
			"DI1 some text...(invers)",
			"DI2 some text...",
			"DI3 some text..."]
	#*********************
	for i in range(len(txtDI)):	#Подстраховка на случай если не все поля сообщений заполнены
		smstxtDI.insert(i, txtDI[i])
		sendEN[i] = 1	#УБРАТЬ ПРИ ПОДКЛЮЧЕНИИ К СЕРВАКУ111111111111111111

	DIinvers[1] = 1
	
	#Active threads
	# try:
	t1 = ThreadDI(BIT, 0.1, t_filterDI, _fs_DI)
	t1.start()
	# finally:
	# 	t1.tstop()
	# 	t1.join()
	# 	startPow = 1
	# 	modPwrOFF()
	#*********************

	startPow = 0
	while startPow!=1:	startPow = modSTARTUP()	#Включаем модем

	if startPow == 1:	#это костыль1111 переделать1111
		if __name__ == '__main__':
			main()

except KeyboardInterrupt:
	print('\n'+"Handle close")

finally:
	t1.tstop()
	t1.join()
	modPwrOFF()
	
"""
	1: Переделать 1 и 0 на true и false
	2: Убери срач1
"""
