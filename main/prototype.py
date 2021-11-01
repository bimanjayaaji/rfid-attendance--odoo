import os
import csv
import RPi.GPIO as GPIO
from PIL import Image
from pathlib import Path
from time import time as timer
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

time_format_str = '%H:%M:%S'
date_format_str = '%Y-%m-%d'
now_format_str = '%Y-%m-%d %H:%M:%S'
add_time = 7
state = ['IN','OUT']

img_path = str(Path(__file__).resolve().parent.joinpath('images', \
														'aba_logo_adobespark.png'))

'''------------------------------------------------------------------------------'''

def time_now():
	now = datetime.now().strftime(time_format_str)
	now = str(now)
	return now
	
def date_now():
	today = datetime.now().strftime(date_format_str)
	today = str(today)
	return today

def append_presence():
	if status == state[0]:
		with open('./attendances/'+date_input+'.csv',mode='a') as writing:
			presence_write = csv.writer(writing, delimiter=',', quotechar='"', 		\
										quoting=csv.QUOTE_MINIMAL)
			presence_write.writerow([id,employee_full,time_input,'',''])
	else:
		with open('./attendances/'+date_input+'.csv',mode='r') as csvfile:
			csvreader = csv.reader(csvfile)
			index = -1
			all_line_rev = list(reversed(list(csvreader)))
			for row in all_line_rev:
				index += 1
				if row[0] == id:
					break
		
			all_line_rev[index][3] = time_input
			all_line_rev[index][4] = work_h
			
			all_line = list(reversed(all_line_rev))
		
		with open('./attendances/'+date_input+'.csv',mode='w') as csvfile:
			presence_write = csv.writer(csvfile, delimiter=',', quotechar='"', 		\
										quoting=csv.QUOTE_MINIMAL)
			for rows in all_line:
				presence_write.writerow(rows)
	display_preview()
			
def append_new():
	with open('./attendances/'+date_input+'.csv',mode='a') as writing:
		presence_write = csv.writer(writing, delimiter=',', quotechar='"', 			\
									quoting=csv.QUOTE_MINIMAL)
		presence_write.writerow(['ID','Name','Check-in','Check-out','Work-hour'])
		if status == state[0]:
			presence_write.writerow([id,employee_full,time_input,'',''])
		else:
			presence_write.writerow([id,employee_full,'',time_input,wh])
	display_preview()

def identify():
	global status, time_input, date_input
	if check_out == False:
		status = state[0]
		time_input = check_in_time
		date_input = check_in_date
	else:
		status = state[1]
		time_input = check_out_time
		date_input = check_out_date
	return status

def presencing():
	odoo_regist()
	identify()
	if os.path.isfile('./attendances/'+date_input+'.csv') == False:
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
	global employee, employee_full, work_h, check_in, check_out,	\
			check_in_date, check_in_time, 	\
			check_out_date, check_out_time
	if res != {'warning': "No employee corresponding to Badge ID '"+id+".'"}:
		employee_full = res['action']['attendance']['employee_id'][1]
		if len(employee_full) >= 2:
			employee = employee_full.split()[0]
		check_in = res['action']['attendance']['check_in']
		check_out = res['action']['attendance']['check_out']
		if check_in != False:
			check_in_date,check_in_time = datetime_generator(check_in)
		if check_out != False:
			check_out_date,check_out_time = datetime_generator(check_out)	
			work_h = wh_generator(check_in_date,check_in_time,check_out_date,		\
									check_out_time)
	else:
		display_db_error()
		main()

def datetime_generator(check):
	check = datetime.strptime(check,now_format_str)
	check = datetime.combine(check.date(),check.time())+timedelta(hours=add_time)
	check_date = check.strftime(date_format_str)
	check_time = check.strftime(time_format_str)
	return check_date,check_time

def wh_generator(start_date,start_time,stop_date,stop_time):
	td = datetime.strptime(start_date,date_format_str)
	tt = datetime.strptime(start_time,time_format_str)
	pd = datetime.strptime(stop_date,date_format_str)
	pt = datetime.strptime(stop_time,time_format_str)
	datetime1 = datetime.combine(td.date(),tt.time())
	datetime2 = datetime.combine(pd.date(),pt.time())
	time_elapsed = datetime2 - datetime1
	return time_elapsed
	
'''------------------------------------------------------------------------------'''

def logo_format():
	global backgroundsss
	logo = Image.open(img_path).convert("RGBA")
	fff = logo.resize((40,40), Image.ANTIALIAS) \
            .transform(device.size, Image.AFFINE, (1,0,0,0,1,0), Image.BILINEAR) \
            .convert(device.mode)
	backgroundsss = Image.new("RGBA", device.size, "black")
	backgroundsss = backgroundsss.resize((128,64), Image.ANTIALIAS) \
            .transform(device.size, Image.AFFINE, (1,0,0,0,1,0), Image.BILINEAR) \
            .convert(device.mode)
	backgroundsss.paste(fff, (83,6))

def display_default():
	with canvas(device,backgroundsss) as draw:
		draw.rectangle(device.bounding_box, outline="white", fill=None)
		draw.text((10, 10), date_now(), fill="white")
		draw.text((10, 25), time_now()[0:5], fill="white")
		draw.text((10, 45), "ABA ROBOTICS", fill="white")

def display_preview():
	if status == state[0]:
		space = ' : '
	if status == state[1]:
		space = ': '
	timeout = timer() + 3
	while timer() < timeout:
		with canvas(device) as draw:
			draw.rectangle(device.bounding_box, outline="white", fill="black")
			draw.text((8, 10), 'ID : '+employee, fill="white")
			draw.text((8, 25), status+space+time_input, fill="white")
			draw.text((90, 40), status, fill="white")

def display_db_error():
	timeout = timer() + 3
	while timer() < timeout:
		with canvas(device) as draw:
			draw.rectangle(device.bounding_box, outline="white", fill="black")
			draw.text((8, 18), "Database Not Found", fill="white")
			draw.text((16, 38), "Retry / Check ID", fill="white")

def display_odoo_refused():
	with canvas(device) as draw:
		draw.rectangle(device.bounding_box, outline="white", fill="black")
		draw.text((8, 18), "Connection Refused", fill="white")
		draw.text((24, 38), "Check Server", fill="white")	

'''------------------------------------------------------------------------------'''

def check_server():
	while not Odoo.setUserID():
		display_odoo_refused()

def main():
	logo_format()
	while True:
		check_server()
		display_default()
		reading()

'''------------------------------------------------------------------------------'''

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass
GPIO.cleanup()
