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
from lib import OdooXMLrpc, Utils

serial = i2c(port=1, address=0x3C)
device = sh1106(serial, rotate=0)
reader = SimpleMFRC522()
ph_date =''

Utils.getSettingsFromDeviceCustomization()
Odoo = OdooXMLrpc.OdooXMLrpc()
serverProxy = Odoo.getServerProxy("/xmlrpc/object")

def time_now():
	now = datetime.datetime.now().strftime("%H:%M:%S")
	now = str(now)
	return now
	
def date_now():
	today = datetime.datetime.now().strftime("%Y-%m-%d")
	today = str(today)
	return today

def append_presence():
	odoo_regist()
	if identify(employee) == 'INVALID':
		display_invalid()
	else:
		if id_check != 0:
			with open('./attendances/'+date_now()+'.csv',mode='a') as writing:
				presence_write = csv.writer(writing, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				presence_write.writerow([time_now(),text,employee,status])
			display_preview(id_str,text,status)
			
def append_new():
	odoo_regist()
	if id_check != 0:
		with open('./attendances/'+date_now()+'.csv',mode='a') as writing:
			presence_write = csv.writer(writing, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			presence_write.writerow(['time','id','name','in/out'])
			presence_write.writerow([time_now(),text,employee,'IN'])
		display_preview(id_str,text,'IN')

def identify(name):
	global status, status_bottom
	with open('./attendances/'+date_now()+'.csv',mode='r') as csvfile:
		csvreader = csv.reader(csvfile)
		for row in reversed(list(csvreader)):
			if row[2] == name:
				status_bottom = row[3]
				break
			else:
				status_bottom = 'EMPTY'
	if status_bottom == 'IN':
		status = 'OUT'
	elif status_bottom == 'OUT':
		status = 'INVALID'
	else:
		status = 'IN'
	return status

def presencing():
	if (date_now() != old_date) or (date_now() != ph_date):
		if os.path.isfile('./attendances/'+date_now()+'.csv') == False:
			append_new()
		else:
			append_presence()
	else:
		append_presence()

def reading():
	global id_str,text
	id, text = reader.read_no_block()
	if id != None:
		id_str = str(id)
		text = text.replace(" ","")
		presencing()

def display_preview(par1,par2,status):
	if status == 'IN':
		space = ' : '
	if status == 'OUT':
		space = ': '
	check_time = time_now()
	timeout = time() + 3
	while time() < timeout:
		with canvas(device) as draw:
			draw.rectangle(device.bounding_box, outline="white", fill="black")
			draw.text((8, 10), 'ID : '+employee, fill="white")
			draw.text((8, 25), str(status)+space+check_time, fill="white")
			draw.text((90, 40), status, fill="white")

def display_default():
	with canvas(device) as draw:
		draw.rectangle(device.bounding_box, outline="white", fill="black")
		draw.text((10, 10), date_now(), fill="white")
		draw.text((10, 25), time_now(), fill="white")
		draw.text((12, 45), "Work Life Balance", fill="white")

def display_invalid():
	timeout = time() + 3
	while time() < timeout:
		with canvas(device) as draw:
			draw.rectangle(device.bounding_box, outline="white", fill="black")
			draw.text((8, 18), "Already Checked Out", fill="white")
			draw.text((16, 38), "Have a Nice Day!", fill="white")

def display_db_error():
	timeout = time() + 3
	while time() < timeout:
		with canvas(device) as draw:
			draw.rectangle(device.bounding_box, outline="white", fill="black")
			draw.text((8, 18), "Database Not Found", fill="white")
			draw.text((16, 38), "Retry / Check ID", fill="white")

def odoo_regist():
	global res
	res = serverProxy.execute_kw(
					Utils.settings["odooParameters"]["db"][0],
                    Odoo.uid,
                    Utils.settings["odooParameters"]["user_password"][0],
                    "hr.employee",
                    "attendance_scan",
                    [text]
                )
	odoo_reply()

def odoo_reply():
	global employee, check_in, check_out, id_check
	if res != {'warning': "No employee corresponding to Badge ID '"+text+".'"}:
		id_check = 1
		employee = res['action']['attendance']['employee_id'][1].split()[0]
		#check_in = res['action']['attendance']['check_in'].split()[1]
		#check_out = res['action']['attendance']['check_out'].split()[1]
	else:
		id_check = 0
		employee = ''
		display_db_error()
	
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
