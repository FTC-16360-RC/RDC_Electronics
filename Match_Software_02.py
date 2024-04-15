from flask import Flask, request
import requests
import time
import datetime
import serial
import keyboard
import copy
import json

log = []

state = {"balls" : 
            {"29" : 0, 
             "91" : 0, 
             "92" : 0, 
             "93" : 0, 
             "94" : 0, 
             "95" : 0},
        "time" : 0,         #time in ms
             }

time_zero = 0

serial_port = "COM6"
serial_baudrate = 9600
display_software_ip = "127.0.0.1"
webhook_port = "5001"

class BallFinder:
    
    ticks_since_local_maximum = 0
    local_maximum = 0
    sensor_id = ""
    last_x = 0

    def __init__(self, id):
        self.sensor_id = id
    
    def new_datapoint(self, x):
        if x > 200:
            return
        if x > self.local_maximum:
            self.local_maximum = x
        if x < self.local_maximum - 10:
            self.ticks_since_local_maximum = self.ticks_since_local_maximum + 1
            self.last_x = x
    
    def check_for_ball(self):
        if self.ticks_since_local_maximum >= 15:
            self.local_maximum = self.last_x
            self.ticks_since_local_maximum = 0
            return True

# Function to trigger webhook to Script B
def trigger_webhook(data):
    webhook_url = f"http://{display_software_ip}:{str(webhook_port)}/webhook_match_to_display"  # URL of Script B's endpoint
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code == 200:
            print('Webhook successfully triggered')
        else:
            print('Failed to trigger webhook')    
    except:       
        print('Failed to trigger webhookDDDD')



def handle_serial_data(data, ball_finder):
    
    state_changed = False

    if "Distance at sensor" == data[0:18]:
        address = data[19:21]
        distance = data[23:]

        if address != ball_finder.sensor_id:
            return

        ball_finder.new_datapoint(int(distance))
        if ball_finder.check_for_ball():
            state["balls"][address] = state["balls"][address] + 1
            log.append(copy.deepcopy(state))
            state_changed = True
            print("-sensed ball!")
        

        temp = state["balls"][address]

        return state_changed
    else:
        return False

def read_serial(ser):

    if ser.in_waiting > 0:
        data = ser.readline().decode('latin1').strip()
        return data
    else:
        return "XXXX"

def load_settings():
    global serial_port, serial_baudrate, display_software_ip, webhook_port

    f = open("settings.json", "r")
    settings = json.load(f)

    serial_port = settings["serial COM port"]
    serial_baudrate = settings["serial baud rate"]
    display_software_ip = settings["display software ip"]
    webhook_port = settings["webhook port"]
    


def calculate_points():
    points = { "orange" : 0, "blue" : 0 }
    
    points["orange"] = int(state["balls"]["29"]) * 14
    points["orange"] += int(state["balls"]["91"]) * 7
    points["orange"] += int(state["balls"]["92"]) * 5

    points["blue"] = int(state["balls"]["93"]) * 14
    points["blue"] += int(state["balls"]["94"]) * 7
    points["blue"] += int(state["balls"]["95"]) * 5

    return points


def start_match():
    global time_zero

    start_time = int(time.time() + 9)            #start time delay
    start_packet = {"init" : start_time}
    trigger_webhook(start_packet)
    print(f"start time:{start_time}")

    while(time.time() < start_time):
        trash = read_serial(ser)                #put shit in trash

    time_zero = time.time() * 1000


def end_match():
    print("END!!!")
    
    points = calculate_points()
    log.append({"end points: " : points})
    end_packet = {"end" : points}
    trigger_webhook(end_packet)

    print(log)
    f = open("Match log " + str(datetime.datetime.now()).replace(":","_").replace(".","_") + ".json", "x") 
    f.write(json.dumps(log))
    f.close()

    print("written log to file")
    print("press ctr + c to exit...")
    
    while True:
        pass



if __name__ == "__main__":
    last_second = 0
    endgame = False

    load_settings()

    ser = serial.Serial(serial_port, serial_baudrate)
    print("Serial Open")

    start_match()

    ball_finder_blue_high = BallFinder("29")  #one sensor test
    ball_finder_blue_mid = BallFinder("91")
    ball_finder_blue_push = BallFinder("92")

    ball_finder_orange_high = BallFinder("93")
    ball_finder_orange_mid = BallFinder("94")
    ball_finder_orange_push = BallFinder("95")

    while True:
        state["time"] = int(time.time() * 1000 - time_zero)                #upate time

        data = read_serial(ser)

        a = handle_serial_data(data, ball_finder_blue_high)
        b = handle_serial_data(data, ball_finder_blue_mid)
        c = handle_serial_data(data, ball_finder_blue_push)
        
        d = handle_serial_data(data, ball_finder_orange_high)
        e = handle_serial_data(data, ball_finder_orange_mid)
        f = handle_serial_data(data, ball_finder_orange_push)

        if a or b or c or d or e or f:
            trigger_webhook(state)
        
        if int(time.time()) != last_second:    #decisec anzeige
            last_second = int(time.time())
            print(f"time match software: {int(time.time() - time_zero/1000)}")

        if time.time() - time_zero/1000 >= 30 and not endgame:
            print("ENDGAME!!!!")
            endgame = True

        if time.time() - time_zero/1000 >= 40:
            end_match()
            