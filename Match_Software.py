from flask import Flask, request
import requests
import time
import serial
import keyboard

ser = serial.Serial()
#app = Flask(__name__)

#does not work if another program has serial monitor open
def init_serial():

    ser.baudrate = 6900
    ser.port = 'COM6'
    
    try:
        ser.open()
        return True
    except:
        return False


def read_serial_line():

    if not ser.is_open:
        print("serial not open")
        return

    try:
        if ser.in_waiting > 0:
            print(f"reading {ser.baudrate} and {ser.port}")
            data = ser.readline().decode('latin1').strip()
            return data
    except:
        return "x"

# Function to trigger webhook to Script B
def trigger_webhook(data):
    webhook_url = 'http://localhost:5001/webhook_match_to_display'  # URL of Script B's endpoint
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 200:
            print('Webhook successfully triggered')
        else:
            print('Failed to trigger webhook')    
    except:       
        print('Failed to trigger webhook')


def _init():
    global serial_running

    trigger_webhook("init")
    init_serial()
    print("Serial Open: " + str(ser.is_open))


def _loop():
    global ser

    if ser.is_open:
        print(read_serial_line())

    if keyboard.is_pressed('q'):
        trigger_webhook("woop")
    

if __name__ == '__main__':
    _init()
    while True:
        try:
            _loop()
        except KeyboardInterrupt:
            print("\nSerial reading stopped.")
            
