#!/usr/bin/env python3

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

def main():
	while True:
		id, text = reader.read()
		print(id)
		print(text)

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass
		
GPIO.cleanup()

