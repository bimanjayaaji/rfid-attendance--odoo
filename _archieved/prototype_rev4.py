import os
import csv
import RPi.GPIO as GPIO
from time import time as timer
from enum import Enum
from mfrc522 import SimpleMFRC522
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from lib import OdooXMLrpc, Utils
from datetime import datetime,date,time,timedelta

serial = i2c(port=1, address=0x3C)
device = sh1106(serial, rotate=0)
reader = SimpleMFRC522()

Utils.getSettingsFromDeviceCustomization()
Odoo = OdooXMLrpc.OdooXMLrpc()
serverProxy = Odoo.getServerProxy("/xmlrpc/object")

ph_date =''
time_format_str = '%H:%M:%S'
date_format_str = '%Y-%m-%d'
now_format_str = '%Y-%m-%d %H:%M:%S'
add_time = 7

def time_now():
	now = datetime.now().strftime(time_format_str)
	now = str(now)
	return now
	
def date_now():
	today = datetime.now().strftime(date_format_str)
	today = str(today)
	return today

def append_presence():
	if identify(employee) == 'INVALID':
		display_invalid()
	else:
		if id_check != 0:
			with open('./attendances/'+date_now()+'.csv',mode='a') as writing:
				presence_write = csv.writer(writing, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
				presence_write.writerow([time_now(),id,employee,status])
			display_preview(code_str,id,status)
			
def append_new():
	if id_check != 0:
		with open('./attendances/'+date_now()+'.csv',mode='a') as writing:
			presence_write = csv.writer(writing, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			presence_write.writerow(['time','id','name','in/out'])
			presence_write.writerow([time_now(),id,employee,'IN'])
		display_preview(code_str,id,'IN')

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
	odoo_regist()
	if os.path.isfile('./attendances/'+date_now()+'.csv') == False:
		append_new()
	else:
		append_presence()

def reading():
	global code_str,id
	code, id = reader.read_no_block()
	if code != None:
		code_str = str(code)
		id = id.replace(" ","")
		presencing()

'''------------------------------------------------------------------------------'''

def odoo_regist():
	global res
	res = serverProxy.execute_kw(
					Utils.settings["odooParameters"]["db"][0],
                    Odoo.uid,
                    Utils.settings["odooParameters"]["user_password"][0],
                    "hr.employee",
                    "attendance_scan",
                    [id]
                )
	odoo_reply()

def odoo_reply():
	global employee, check_in, check_out, id_check
	if res != {'warning': "No employee corresponding to Badge ID '"+id+".'"}:
		id_check = 1
		employee = res['action']['attendance']['employee_id'][1].split()[0]
		check_in = res['action']['attendance']['check_in']
		check_out = res['action']['attendance']['check_out']
		if check_in != False:
			check_in_date,check_in_time = datetime_generator(check_in)
		if check_out != False:
			check_out_date,check_out_time = datetime_generator(check_out)
	else:
		id_check = 0
		employee = ''
		display_db_error()

def datetime_generator(check):
	check = datetime.strptime(check,now_format_str)
	check = datetime.combine(check.date(),check.time())+timedelta(hours=add_time)
	check_date = check.strftime(date_format_str)
	check_time = check.strftime(time_format_str)
	#print(check_date,check_time)
	return check_date,check_time

'''------------------------------------------------------------------------------'''

def display_default():
	with canvas(device) as draw:
		draw.rectangle(device.bounding_box, outline="white", fill="black")
		draw.text((10, 10), date_now(), fill="white")
		draw.text((10, 25), time_now(), fill="white")
		draw.text((12, 45), "Work Life Balance", fill="white")

def display_preview(par1,par2,status):
	if status == 'IN':
		space = ' : '
	if status == 'OUT':
		space = ': '
	check_time = time_now()
	timeout = timer() + 3
	while timer() < timeout:
		with canvas(device) as draw:
			draw.rectangle(device.bounding_box, outline="white", fill="black")
			draw.text((8, 10), 'ID : '+employee, fill="white")
			draw.text((8, 25), str(status)+space+check_time, fill="white")
			draw.text((90, 40), status, fill="white")

def display_invalid():
	timeout = timer() + 3
	while timer() < timeout:
		with canvas(device) as draw:
			draw.rectangle(device.bounding_box, outline="white", fill="black")
			draw.text((8, 18), "Already Checked Out", fill="white")
			draw.text((16, 38), "Have a Nice Day!", fill="white")

def display_db_error():
	timeout = timer() + 3
	while timer() < timeout:
		with canvas(device) as draw:
			draw.rectangle(device.bounding_box, outline="white", fill="black")
			draw.text((8, 18), "Database Not Found", fill="white")
			draw.text((16, 38), "Retry / Check ID", fill="white")

'''------------------------------------------------------------------------------'''

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
