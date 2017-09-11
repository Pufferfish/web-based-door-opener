"""Handles the I/O for the raspberry pi"""
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

def open_door():
    """Sets pins to open door"""
    print 'Door opening!'
    GPIO.setup(3, GPIO.OUT)
    GPIO.output(3, GPIO.LOW)

def close_door():
    """Sets pints to close door"""
    print 'Door closing!'
    GPIO.setup(3, GPIO.OUT)
    GPIO.output(3, GPIO.HIGH)
