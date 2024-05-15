import time
import datetime
import serial
import keyboard
import copy
import json
import pygame


log = []

state = {"balls" : 
            {"29" : 0, 
             "91" : 0, 
             "92" : 0, 
             "93" : 0, 
             "94" : 0, 
             "95" : 0},
        "time" : 0,             #time in s
        "period" : "holding",   #holding, regulation, endgame, finished
        "message" : ""
             }

time_zero_ns = 0  #before hold duration

SERIAL_PORT = "COM6"
SERIAL_BAUDRATE = 9600
HOLD_DURATION = 10
MATCH_DURATION = 120
ENDGAME_DURATION = 30

SOUND_END_PATH = ""
SOUND_START_PATH = ""
SOUND_COUNTDOWN_PATH = ""
SOUND_ENDGAME_PATH = ""


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


def play_sound(sound_file):
    pygame.mixer.init()
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()


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
            log_data("ball")
            state_changed = True
            print("-sensed ball!")

        return state_changed
    else:
        return False


def calculate_points():
    points = { "orange" : 0, "blue" : 0 }
    
    points["orange"] = int(state["balls"]["29"]) * 14
    points["orange"] += int(state["balls"]["91"]) * 7
    points["orange"] += int(state["balls"]["92"]) * 5

    points["blue"] = int(state["balls"]["93"]) * 14
    points["blue"] += int(state["balls"]["94"]) * 7
    points["blue"] += int(state["balls"]["95"]) * 5

    return points


def log_data(message = ""):
    state["message"] = message
    log.append(copy.deepcopy(state))


def read_serial(ser):

    if ser.in_waiting > 0:
        data = ser.readline().decode('latin1').strip()
        return data
    else:
        return "XXXX"


def end_match():
    print("END!!!")
    
    points = calculate_points()
    log.append({"end points: " : points})

    print(log)
    f = open("Match log " + str(datetime.datetime.now()).replace(":","_").replace(".","_") + ".json", "x") 
    f.write(json.dumps(log))
    f.close()

    print("written log to file")
    print("press ctr + c to exit...")
    
    while True:
        pass


def load_settings():
    global SERIAL_PORT, SERIAL_BAUDRATE, MATCH_DURATION, ENDGAME_DURATION, MATCH_DURATION, HOLD_DURATION, SOUND_START_PATH, SOUND_END_PATH, SOUND_COUNTDOWN_PATH, SOUND_ENDGAME_PATH

    f = open("settings.json", "r")
    settings = json.load(f)

    SERIAL_PORT = settings["serial COM port"]
    SERIAL_BAUDRATE = settings["serial baud rate"]

    MATCH_DURATION = settings["match duration"] * 1000000000
    ENDGAME_DURATION = settings["endgame duration"] * 1000000000
    HOLD_DURATION = settings["hold duration"] * 1000000000
    
    SOUND_START_PATH = "./Sounds/" + settings["start sound file name"]
    SOUND_END_PATH = "./Sounds/" + settings["end sound file name"]
    SOUND_COUNTDOWN_PATH = "./Sounds/" + settings["countdown sound file name"]
    SOUND_ENDGAME_PATH = "./Sounds/" + settings["endgame sound file name"]


if __name__ == "__main__":

    load_settings()

    pygame.mixer.init()

    time_zero_ns = time.time_ns() + HOLD_DURATION
    last_displayed_timestamp = 0
    countdown_played = False

    print(f"starting at {time_zero_ns}")

    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
    print("Serial Open")

    ball_finder_blue_high = BallFinder("29")  #one sensor test
    ball_finder_blue_mid = BallFinder("91")
    ball_finder_blue_push = BallFinder("92")

    ball_finder_orange_high = BallFinder("93")
    ball_finder_orange_mid = BallFinder("94")
    ball_finder_orange_push = BallFinder("95")

    while True:

        state["time"] = round((time.time_ns() - time_zero_ns) / 1000000000, 4)            #upate time

        #match start trigger
        if time.time_ns() >= time_zero_ns and state["period"] == "holding":
            print("Game Started")
            #log_data("game started")
            state["period"] = "regulation"
            play_sound(SOUND_START_PATH)

        #endgame trigger
        if time.time_ns() - time_zero_ns >= (MATCH_DURATION - ENDGAME_DURATION) and state["period"] == "regulation":  
            print("ENDGAME!!!!")
            #log_data("start of endgame")
            state["period"] = "endgame"
            play_sound(SOUND_ENDGAME_PATH)
        
        #game end trigger
        if time.time_ns() - time_zero_ns >= MATCH_DURATION and not state["period"] == "finished":
            print("Game Over")
            #log_data("finished")
            state["period"] = "finished"
            play_sound(SOUND_END_PATH)
            end_match()
        
        #read balls and log stuff
        if(state["period"] == "endgame" or state["period"] == "regulation"):
            data = read_serial(ser)

            a = handle_serial_data(data, ball_finder_blue_high)
            b = handle_serial_data(data, ball_finder_blue_mid)
            c = handle_serial_data(data, ball_finder_blue_push)
            
            d = handle_serial_data(data, ball_finder_orange_high)
            e = handle_serial_data(data, ball_finder_orange_mid)
            f = handle_serial_data(data, ball_finder_orange_push)

        #decisec display
        if time.time_ns() >= last_displayed_timestamp + 250000000:    
            last_displayed_timestamp = time.time_ns()
            t = state["time"]
            print(f"time match software: {t} - timestamp: {time.time_ns()}")

        #countdowns
        if state["period"] == "holding":
            if state["time"] >= -3 and state["time"] < -2.5 and not countdown_played:
                countdown_played = True
                play_sound(SOUND_COUNTDOWN_PATH)
            if state["time"] > -2.5 and state["time"] < -2 and countdown_played:
                countdown_played = False

            if state["time"] >= -2 and state["time"] < -1.5 and not countdown_played:
                countdown_played = True
                play_sound(SOUND_COUNTDOWN_PATH)
            if state["time"] > -1.5 and state["time"] < -1 and countdown_played:
                countdown_played = False

            if state["time"] >= -1 and state["time"] < -0.5 and not countdown_played:
                countdown_played = True
                play_sound(SOUND_COUNTDOWN_PATH)
            if state["time"] > -0.5 and state["time"] < 0 and countdown_played:
                countdown_played = False

        if state["period"] == "endgame":
            if state["time"] >= MATCH_DURATION - 3 and state["time"] < MATCH_DURATION - 2.5 and not countdown_played:
                countdown_played = True
                play_sound(SOUND_COUNTDOWN_PATH)
            if state["time"] > MATCH_DURATION - 2.5 and state["time"] < MATCH_DURATION - 2 and countdown_played:
                countdown_played = False

            if state["time"] >= MATCH_DURATION - 2 and state["time"] < MATCH_DURATION - 1.5 and not countdown_played:
                countdown_played = True
                play_sound(SOUND_COUNTDOWN_PATH)
            if state["time"] > MATCH_DURATION - 1.5 and state["time"] < MATCH_DURATION - 1 and countdown_played:
                countdown_played = False

            if state["time"] >= MATCH_DURATION - 1 and state["time"] < MATCH_DURATION - 0.5 and not countdown_played:
                countdown_played = True
                play_sound(SOUND_COUNTDOWN_PATH)
            if state["time"] > MATCH_DURATION - 0.5 and state["time"] < MATCH_DURATION - 0 and countdown_played:
                countdown_played = False
