import csv
from datetime import datetime,date,time,timedelta

time_format_str = '%H:%M:%S'
date_format_str = '%Y-%m-%d'
now_format_str = '%Y-%m-%d %H:%M:%S'
name1 = 'Abigail Peterson'
name2 = 'Anita Oliver'
code_str1 = '041405513376'
code_str2 = '041078536769'

def time_now():
	now = datetime.now().strftime(time_format_str)
	now = str(now)
	return now
	
def date_now():
	today = datetime.now().strftime(date_format_str)
	today = str(today)
	return today
	
def main():	
	with open('./attendances/'+date_now()+'.csv',mode='r') as csvfile:
		csvreader = csv.reader(csvfile)
		index = -1
		all_line_rev = list(reversed(list(csvreader)))
		for row in all_line_rev:
			index += 1
			if row[1] == code_str1:
				break
		
		all_line_rev[index][3] = 'MLEBU'
		all_line = list(reversed(all_line_rev))
		
	with open('./attendances/'+date_now()+'.csv',mode='w') as csvfile:
		presence_write = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		for rows in all_line:
			presence_write.writerow(rows)

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass
		
# with open('./attendances/'+date_input+'.csv',mode='a') as writing:
		# presence_write = csv.writer(writing, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		# presence_write.writerow([time_input,id,employee_full,status])
		
		
		
		
