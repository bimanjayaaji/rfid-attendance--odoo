import csv
import datetime

def date_now():
	today = datetime.datetime.now().strftime("%Y-%m-%d")
	today = str(today)
	return today

def main():
	with open(date_now()+'.csv', 'r') as csvfile:
		csvreader = csv.reader(csvfile)
		for each_row in csvreader:
			print(each_row)
		
if __name__ == '__main__':
	main()
