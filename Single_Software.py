import time
import datetime
import serial
import keyboard
import copy
import json
import pygame
import tkinter as tk
import threading


log = []

state = {"balls" : 
            {"29" : 0, 
             "91" : 0, 
             "92" : 0, 
             "93" : 0, 
             "94" : 0, 
             "95" : 0},
        "time" : 0,             #time in s
        "time_ns" : 0,
        "period" : "holding",   #holding, regulation, endgame, finished
        "message" : ""
             }

events = [
    #[Event Type, time, executed, args...] general
    #["SERIAL_MESSAGE", time, executed, Serial Message] serial
    #["PLAY_SOUND", time, executed, SOUND_PATH] sounds
]

ser = "SERIAL HERE"
window = "WINDOW HERE"

time_zero_ns = 0  #before hold duration

SERIAL_PORT = "COM6"
SERIAL_BAUDRATE = 9600

HOLD_DURATION = 10
MATCH_DURATION = 120
ENDGAME_DURATION = 30
COUNTDOWN_INTERVAL = 1

SOUND_END_PATH = ""
SOUND_START_PATH = ""
SOUND_COUNTDOWN_PATH = ""
SOUND_ENDGAME_PATH = ""

BALL_DROP_1 = 0
BALL_DROP_2 = 0
BALL_DROP_3 = 0

SENSOR_SCORING = True
ESP32_ATTACHED = True


class Window:
    def __init__(self, state):
        self.root = tk.Tk() 

        #centering windows chatgpt magic
        # Set window size and center it on the screen
        self.window_width = 400
        self.window_height = 300
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        self.x = (self.screen_width - self.window_width) // 2
        self.y = (self.screen_height - self.window_height) // 2
        #self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")

        # Create a frame to contain all labels
        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, pady=10, sticky="nsew")

        # Set weights for rows and columns to make them expandable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.frame.grid_columnconfigure((0, 1, 2), weight=1)

        #setting up labels
        self.balls_orange_top = tk.Label(self.frame, text=state["balls"]["29"])
        self.balls_orange_mid = tk.Label(self.frame, text=state["balls"]["91"])
        self.balls_orange_push = tk.Label(self.frame, text=state["balls"]["92"])
        self.balls_blue_top = tk.Label(self.frame, text=state["balls"]["93"])
        self.balls_blue_mid = tk.Label(self.frame, text=state["balls"]["94"])
        self.balls_blue_push = tk.Label(self.frame, text=state["balls"]["95"])

        self.time_label = tk.Label(self.frame, text="time")
        self.state_label = tk.Label(self.frame, text="state")

        self.balls_orange_top.grid(row=2, column=0, padx=10, pady=10)
        self.balls_orange_mid.grid(row=3, column=0, padx=10, pady=10)
        self.balls_orange_push.grid(row=4, column=0, padx=10, pady=10)
        self.balls_blue_top.grid(row=2, column=2, padx=10, pady=10)
        self.balls_blue_mid.grid(row=3, column=2, padx=10, pady=10)
        self.balls_blue_push.grid(row=4, column=2, padx=10, pady=10)

        self.time_label.grid(row=0, column=1, padx=10, pady=10)
        self.state_label.grid(row=1, column=0, padx=10, pady=10)


        self.root.resizable(True, True)
        self.update()
    

    def change_state(self, new_state):
        self.state_label.config(text = new_state)
        self.root.update()

    def update_state(self, state):
        self.balls_orange_top.config(text=state["balls"]["29"])
        self.balls_orange_mid.config(text=state["balls"]["91"])
        self.balls_orange_push.config(text=state["balls"]["92"])
        self.balls_blue_top.config(text=state["balls"]["93"])
        self.balls_blue_mid.config(text=state["balls"]["94"])
        self.balls_blue_push.config(text=state["balls"]["95"])
        self.root.update()

    def update_time(self, time_zero_ns):
        minus_zero_char = ''
        
        t_decimal = int(time.time()*10) - int(time.time()) * 10
        t_second = int((time.time_ns() - time_zero_ns) / 1000000000)

        negative = False

        if(time.time_ns() < time_zero_ns):     #before start
            t_decimal = 9 - t_decimal
            negative = True
            if(t_second == 0):
                minus_zero_char = '-'

        

        if t_second < 0:
            t_decimal = 9 - t_decimal
        
        if t_second >= 40:
            t_second = 40
            t_decimal = 0


        t = f"{minus_zero_char}{t_second}.{t_decimal} / {MATCH_DURATION / 1000000000}"
        self.time_label.config(text = t)
        self.root.update()

            
    def update(self):
        self.root.update_idletasks()
        self.root.update()


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


#helpers
def play_sound(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()


def log_data(message = ""):
    state["message"] = message
    log.append(copy.deepcopy(state))


def send_serial_command(command):
    global ser

    print(f"Writing serial command: {command}")
    log_data(f"serial command {command}")
    ser.write(command.encode('utf-8'))


#one time match related stuff
def calculate_points():
    points = { "orange" : 0, "blue" : 0 }
    
    points["orange"] = int(state["balls"]["29"]) * 14
    points["orange"] += int(state["balls"]["91"]) * 7
    points["orange"] += int(state["balls"]["92"]) * 5

    points["blue"] = int(state["balls"]["93"]) * 14
    points["blue"] += int(state["balls"]["94"]) * 7
    points["blue"] += int(state["balls"]["95"]) * 5

    return points


def start_regulation():
    print("Game Started")
    window.change_state("match running")
    #log_data("game started")
    state["period"] = "regulation"


def start_endgame():
    print("ENDGAME!!!!")
    window.change_state("endgame")
    #log_data("start of endgame")
    state["period"] = "endgame"


def end_match():
    window.change_state("end")
    state["period"] = "finished"

    print("END!!!")
    
    points = calculate_points()
    log.append({"end points: " : points})

    print(log)
    f = open("Match log " + str(datetime.datetime.now()).replace(":","_").replace(".","_") + ".json", "x") 
    f.write(json.dumps(log))
    f.close()

    print("written log to file")
    print("press ctr + c to exit...")
    
    #end loop
    while True:
        window.update()


def wait_for_start(window):
    print("Press <space> to run match")
    print("--waiting--")    
    while not keyboard.is_pressed("space"):
        window.update()
    window.change_state("Match about to start")

#...
def read_serial(ser):

    if ser.in_waiting > 0:
        data = ser.readline().decode('latin1').strip()
        return data
    else:
        return "XXXX"


def load_settings():
    global SERIAL_PORT, SERIAL_BAUDRATE, MATCH_DURATION, ENDGAME_DURATION
    global COUNTDOWN_INTERVAL, MATCH_DURATION, HOLD_DURATION
    global SOUND_START_PATH, SOUND_END_PATH, SOUND_COUNTDOWN_PATH, SOUND_ENDGAME_PATH
    global SENSOR_SCORING, ESP32_ATTACHED
    global BALL_DROP_1, BALL_DROP_2, BALL_DROP_3

    f = open("settings.json", "r")
    settings = json.load(f)

    SERIAL_PORT = settings["serial COM port"]
    SERIAL_BAUDRATE = settings["serial baud rate"]

    COUNTDOWN_INTERVAL = settings["countdown interval"] * 1000000000
    MATCH_DURATION = settings["match duration"] * 1000000000
    ENDGAME_DURATION = settings["endgame duration"] * 1000000000
    HOLD_DURATION = settings["hold duration"] * 1000000000
    
    SOUND_START_PATH = "./Sounds/" + settings["start sound file name"]
    SOUND_END_PATH = "./Sounds/" + settings["end sound file name"]
    SOUND_COUNTDOWN_PATH = "./Sounds/" + settings["countdown sound file name"]
    SOUND_ENDGAME_PATH = "./Sounds/" + settings["endgame sound file name"]

    SENSOR_SCORING = settings["sensor scoring enabled"]
    ESP32_ATTACHED = settings["eps32 attached"]

    BALL_DROP_1 = settings["first ball drop"] * 1000000000
    BALL_DROP_1 = settings["second ball drop"] * 1000000000
    BALL_DROP_1 = settings["third ball drop"] * 1000000000



def handle_serial_data(data, ball_finder):
    if not SENSOR_SCORING:
        return
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


def handle_scheduled_events():
    global events

    for event in events:
        #if executed
        if event[2]:
            continue

        #check if we don't have to execute event yet
        if state["time_ns"] < event[1]:
            continue
        
        if event[0] == "PLAY_SOUND":
            play_sound(event[3])
            event[2] = True
            continue
        
        if event[0] == "SERIAL_MESSAGE":
            send_serial_command(event[3])
            event[2] = True
            continue
        
        if event[0] == "START_REGULATION":
            start_regulation()
            event[2] = True
            continue
        
        if event[0] == "START_ENDGAME":
            start_endgame()
            event[2] = True
            continue

        if event[0] == "END_MATCH":
            end_match()
            event[2] = True
            continue


def schedule_event(event):
    global events

    events.append(event)


if __name__ == "__main__":

    #settings
    load_settings()
    if not SENSOR_SCORING:
        print("\n!!!SENSORS NOT ACTIVE!!!")

    #sound mixer
    pygame.mixer.quit()
    pygame.mixer.init()

    #----Schedule Events-----
    #set sound timings
    schedule_event(["PLAY_SOUND", 0, False, SOUND_START_PATH])
    schedule_event(["PLAY_SOUND", MATCH_DURATION - ENDGAME_DURATION, False, SOUND_ENDGAME_PATH])
    schedule_event(["PLAY_SOUND", MATCH_DURATION, False, SOUND_END_PATH])

    schedule_event(["PLAY_SOUND", -1 * COUNTDOWN_INTERVAL, False, SOUND_COUNTDOWN_PATH])
    schedule_event(["PLAY_SOUND", -2 * COUNTDOWN_INTERVAL, False, SOUND_COUNTDOWN_PATH])
    schedule_event(["PLAY_SOUND", -3 * COUNTDOWN_INTERVAL, False, SOUND_COUNTDOWN_PATH])

    schedule_event(["PLAY_SOUND", -1 * COUNTDOWN_INTERVAL + MATCH_DURATION, False, SOUND_COUNTDOWN_PATH])
    schedule_event(["PLAY_SOUND", -2 * COUNTDOWN_INTERVAL + MATCH_DURATION, False, SOUND_COUNTDOWN_PATH])
    schedule_event(["PLAY_SOUND", -3 * COUNTDOWN_INTERVAL + MATCH_DURATION, False, SOUND_COUNTDOWN_PATH])

    #schedule match events
    schedule_event(["START_REGULATION", 0, False]) 
    schedule_event(["START_ENDGAME", MATCH_DURATION - ENDGAME_DURATION, False]) 
    schedule_event(["END_MATCH", MATCH_DURATION, False]) 

    #set Ball Tower Servo serial timings
    schedule_event(["SERIAL_MESSAGE", BALL_DROP_1, False, "BLU_LOW_OPEN"])
    schedule_event(["SERIAL_MESSAGE", BALL_DROP_1, False, "RED_LOW_OPEN"])

    schedule_event(["SERIAL_MESSAGE", BALL_DROP_2, False, "BLU_MID_OPEN"])
    schedule_event(["SERIAL_MESSAGE", BALL_DROP_2, False, "RED_MID_OPEN"])

    schedule_event(["SERIAL_MESSAGE", BALL_DROP_3, False, "BLU_TOP_OPEN"])
    schedule_event(["SERIAL_MESSAGE", BALL_DROP_3, False, "RED_TOP_OPEN"])
    #---------

    #initialize window
    window = Window(state)
    window.change_state("Waiting for thumbs up")

    #init ball finders
    ball_finder_blue_high = BallFinder("29")  #one sensor test
    ball_finder_blue_mid = BallFinder("91")
    ball_finder_blue_push = BallFinder("92")

    ball_finder_orange_high = BallFinder("93")
    ball_finder_orange_mid = BallFinder("94")
    ball_finder_orange_push = BallFinder("95")

    #init serial
    if(ESP32_ATTACHED):
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
        print("Serial Open")

    wait_for_start(window)

    #time variables
    time_zero_ns = time.time_ns() + HOLD_DURATION
    last_displayed_timestamp = 0

    while True:

        #update window
        window.update()
        window.update_time(time_zero_ns)
        window.update_state(state)

        #upate time
        state["time"] = round((time.time_ns() - time_zero_ns) / 1000000000, 4)
        state["time_ns"] = time.time_ns() - time_zero_ns

        #update scheduled events
        handle_scheduled_events()
        
        #read balls and log stuff
        if((state["period"] == "endgame" or state["period"] == "regulation") and SENSOR_SCORING):
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
            t_ns = state["time_ns"]
            print(f"time match software: {t} - time ns: {t_ns}")