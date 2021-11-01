#!/usr/bin/env python3

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

def main():
	while True:
		text = input('New data:')    
		print("Now place your tag to write")
		reader.write(text)
		print("Written")

if __name__ == "__main__":
	try:
		main()
	except:
		pass

GPIO.cleanup()
