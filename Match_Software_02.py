from flask import Flask, request
import requests
import time
import serial
import keyboard

balls = {"29" : 0}

class BallFinder:
    
    ticks_since_local_maximum = 0
    local_maximum = 0
    sensor_id = 0
    last_x = 0

    def __init__(self, id):
        self.sensor_id = id
    
    def new_datapoint(self, x):
        if x > 200:
            pass
        if x >= self.local_maximum:
            self.local_maximum = x
        else:
            self.ticks_since_local_maximum = self.ticks_since_local_maximum + 1
            self.last_x = x
    
    def check_for_ball(self):
        if self.ticks_since_local_maximum >= 20:
            self.local_maximum = self.last_x
            self.ticks_since_local_maximum = 0
            return True

    

def handle_serial_data(data, ball_finder):
    if "Distance at sensor" == data[0:18]:
        address = data[19:21]
        distance = data[23:]

        ball_finder.new_datapoint(int(distance))
        if ball_finder.check_for_ball():
            balls[address] = balls[address] + 1
        print(f"num of balls: {balls[address]}")
        #print(f"sensor address: {address} - distance:  \'{distance}\'")
    else:
        pass

def read_serial(ser):

    if ser.in_waiting > 0:
        data = ser.readline().decode('latin1').strip()
        return data
    else:
        return "XXXX"


if __name__ == "__main__":
    ball_finder = BallFinder(29)
    #try:
    ser = serial.Serial('COM6', 9600)
    print("Serial Open")
    while True:
        data = read_serial(ser)
        handle_serial_data(data, ball_finder)
    #except:
    #    print("RIP")