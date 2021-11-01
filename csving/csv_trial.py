import os
import csv
import datetime
import RPi.GPIO as GPIO
from enum import Enum
from time import sleep, time
from mfrc522 import SimpleMFRC522
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

serial = i2c(port=1, address=0x3C)
device = sh1106(serial, rotate=0)
reader = SimpleMFRC522()
old_date = ''

def time_now():
	now = datetime.datetime.now().strftime("%H:%M:%S")
	now = str(now)
	return now
	
def date_now():
	today = datetime.datetime.now().strftime("%Y-%m-%d")
	today = str(today)
	return today

def append_presence():
	if identify(text) == 'invalid':
		display_invalid()
	else:
		with open(date_now()+'.csv',mode='a') as writing:
			presence_write = csv.writer(writing, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			presence_write.writerow([time_now(),id_str,text,status])
		display_preview(id_str,text)
			
def append_new():
	with open(date_now()+'.csv',mode='a') as writing:
		presence_write = csv.writer(writing, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		presence_write.writerow(['time','id','name','in/out'])
		presence_write.writerow([time_now(),id_str,text,'in'])
	display_preview(id_str,text)

def identify(name):
	global status, status_bottom
	with open(date_now()+'.csv',mode='r') as csvfile:
		csvreader = csv.reader(csvfile)
		for row in reversed(list(csvreader)):
			if row[2] == name:
				status_bottom = row[3]
				break
			else:
				status_bottom = 'empty'
	if status_bottom == 'in':
		status = 'out'
	elif status_bottom == 'out':
		status = 'invalid'
	else:
		status = 'in'
	return status

def reading():
	global id_str,text
	id, text = reader.read()
	id_str = str(id)
	presencing()

def presencing():
	if date_now() != old_date:
		if os.path.isfile('./'+date_now()+'.csv') == False:
			append_new()
		else:
			append_presence()
	else:
		append_presence()

def display_preview(par1,par2):
	timeout = time() + 4
	while time() < timeout:
		with canvas(device) as draw:
			draw.text((20, 20), par1, fill="white")
			draw.text((20, 40), par2, fill="white")

def display_default():
	with canvas(device) as draw:
		draw.text((30, 40), "Attendance", fill="white")

def display_invalid():
	timeout = time() + 3
	while time() < timeout:
		with canvas(device) as draw:
			draw.text((30, 40), "GO HOME!", fill="white")

def main():
	global old_date
	while True:
		display_default()
		reading()
		
		old_date = date_now()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
        
GPIO.cleanup()
