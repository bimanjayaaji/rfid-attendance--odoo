import csv
import datetime
import RPi.GPIO as GPIO
from time import sleep, time
from mfrc522 import SimpleMFRC522
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106

serial = i2c(port=1, address=0x3C)
device = sh1106(serial, rotate=0)
reader = SimpleMFRC522()

def time_now():
	now = datetime.datetime.now().strftime("%H:%M:%S")
	now = str(now)
	return now
	
def date_now():
	today = datetime.datetime.now().strftime("%Y-%m-%d")
	today = str(today)
	return today

def reading():
	global id_str,text
	id, text = reader.read()
	id_str = str(id)
	presencing()

def presencing():
	with open(date_now()+'.csv',mode='a') as writing:
		presence_write = csv.writer(writing, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		presence_write.writerow([time_now(),id_str,text])

def display_preview(par1,par2):
	timeout = time() + 4
	while time() < timeout:
		with canvas(device) as draw:
			draw.text((20, 20), par1, fill="white")
			draw.text((20, 40), par2, fill="white")

def display_default():
	with canvas(device) as draw:
		draw.text((30, 40), "Attendance", fill="white")

def main():
	while True:
		display_default()
		reading()
		display_preview(id_str,text)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
        
GPIO.cleanup()
