import time
import datetime
import serial
import keyboard
import copy
import json
import pygame
import tkinter as tk
import threading
import screeninfo
import Scorer

log = []

state = {"balls" : 
            {"blu_top" : 0, 
             "blu_mid" : 0, 
             "blu_low" : 0, 
             "red_top" : 0, 
             "red_mid" : 0, 
             "red_low" : 0},   
        "penalty points" : 
            {"blu" : 0,
             "red" : 0},
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

MANUAL_SCORING = False
PRESENTATION_MODE = False
PRESENTATION_SCREEN_ID = 1

CONSOLE_TIME = True

updating_state_gui = False
updating_time_gui = False

scorer = ''


class Window:
    def __init__(self, state):
        self.root = tk.Tk() 

        # Create a frame to contain all labels
        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, pady=10, sticky="nsew")

        # Set weights for rows and columns to make them expandable
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.frame.grid_columnconfigure((0, 1, 2), weight=1)

        #setting up labels
        self.balls_red_top = tk.Label(self.frame, text=state["balls"]["red_top"])
        self.balls_red_mid = tk.Label(self.frame, text=state["balls"]["red_mid"])
        self.balls_red_low = tk.Label(self.frame, text=state["balls"]["red_low"])
        self.balls_blu_top = tk.Label(self.frame, text=state["balls"]["blu_top"])
        self.balls_blu_mid = tk.Label(self.frame, text=state["balls"]["blu_mid"])
        self.balls_blu_low = tk.Label(self.frame, text=state["balls"]["blu_low"])
        self.penalties_blu = tk.Label(self.frame, text=state["penalty points"]["blu"])
        self.penalties_red = tk.Label(self.frame, text=state["penalty points"]["red"])

        self.time_label = tk.Label(self.frame, text="time")
        self.state_label = tk.Label(self.frame, text="state")

        self.balls_red_top.grid(row=2, column=2, padx=10, pady=10)
        self.balls_red_mid.grid(row=3, column=2, padx=10, pady=10)
        self.balls_red_low.grid(row=4, column=2, padx=10, pady=10)
        self.balls_blu_top.grid(row=2, column=0, padx=10, pady=10)
        self.balls_blu_mid.grid(row=3, column=0, padx=10, pady=10)
        self.balls_blu_low.grid(row=4, column=0, padx=10, pady=10)
        self.penalties_blu.grid(row=6, column=0, padx=10, pady=10)
        self.penalties_red.grid(row=6, column=2, padx=10, pady=10)

        self.time_label.grid(row=0, column=1, padx=10, pady=10)
        self.state_label.grid(row=1, column=0, padx=10, pady=10)


        self.root.resizable(True, True)
        self.update()

        #fullscreen_on_second_monitor
        monitors = screeninfo.get_monitors()
        if len(monitors) > 1 and PRESENTATION_MODE:
            print("running on PRESENTATION SCREEN")
            second_monitor = monitors[PRESENTATION_SCREEN_ID]
        
            #self.root.overrideredirect(True)
            self.root.geometry(f"{second_monitor.width}x{second_monitor.height}+{second_monitor.x}+{second_monitor.y}")
            self.root.attributes('-fullscreen', True)
        else:
            print("runnig on MAIN SCREEN")
            #centering windows chatgpt magic
            # Set window size and center it on the screen
            monitor = monitors[0]
            self.window_width = 400
            self.window_height = 300
            self.x = (monitor.width - self.window_width) // 2
            self.y = (monitor.height - self.window_height) // 2
            self.root.geometry(f"{self.window_width}x{self.window_height}+{self.x}+{self.y}")

        
    

    def change_state(self, new_state):
        self.state_label.config(text = new_state)
        self.root.update()

    def update_state(self, state):
        self.balls_red_top.config(text=state["balls"]["red_top"])
        self.balls_red_mid.config(text=state["balls"]["red_mid"])
        self.balls_red_low.config(text=state["balls"]["red_low"])
        self.balls_blu_top.config(text=state["balls"]["blu_top"])
        self.balls_blu_mid.config(text=state["balls"]["blu_mid"])
        self.balls_blu_low.config(text=state["balls"]["blu_low"])
        self.penalties_blu.config(text=state["penalty points"]["blu"])
        self.penalties_red.config(text=state["penalty points"]["red"])
        self.root.update()

    def override_time(self, t):
        self.time_label.config(text = t)
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
        global updating_state_gui
        global updating_time_gui
        global state

        if updating_state_gui:
            self.update_state(state)
        if updating_time_gui:
            self.update_time(time_zero_ns)

        self.root.update_idletasks()
        self.root.update()


class BallFinder:
    
    ticks_since_local_maximum = 0
    local_maximum = 0
    sensor_id = ""
    position = ""
    last_x = 0

    def __init__(self, id, pos):
        self.sensor_id = id
        self.position = pos
    
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

    if not ESP32_ATTACHED:
        print(f"esp not connected. Command: {command}")
        return
    print(f"Writing serial command: {command}")
    log_data(f"serial command {command}")
    ser.write(command.encode('utf-8'))


#one time match related stuff
def calculate_points():
    points = { "orange" : 0, "blue" : 0 }
    
    points["orange"] = int(state["balls"]["red_top"]) * 14
    points["orange"] += int(state["balls"]["red_mid"]) * 7
    points["orange"] += int(state["balls"]["red_low"]) * 5

    points["blue"] = int(state["balls"]["blu_top"]) * 14
    points["blue"] += int(state["balls"]["blu_mid"]) * 7
    points["blue"] += int(state["balls"]["blu_low"]) * 5

    points["blue"] -= int(state["penalty points"]["blu"])
    points["orange"] -= int(state["penalty points"]["red"])

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


def run_manual_scoring():
    global state

    new_entry = scorer.pop_top()
    if new_entry == "empty":
        return

    category = new_entry["category"]
    position = new_entry["position"]
    change = int(new_entry["change"])
    state[category][position] = state[category][position] + change

    temp = state[category][position]
    print(f"now we have {temp} at \"{category}\" : {position} with change {change}")


def end_match():
    global updating_time_gui

    updating_time_gui = False

    window.change_state("end")
    window.override_time(f"{MATCH_DURATION/1e9} / {MATCH_DURATION/1e9}")
    state["period"] = "finished"

    print("END!!!")
    print("press <ENTER> to confirm points")

    scorer.clear()
    while not keyboard.is_pressed('enter'):
        run_manual_scoring()
        window.update()
    
    points = calculate_points()
    log.append({"end points: " : points})

    print(log)
    f = open("Match log " + str(datetime.datetime.now()).replace(":","_").replace(".","_") + ".json", "x") 
    f.write(json.dumps(log))
    f.close()

    print("written log to file")
    print("ctrl + c doesn't work, figure it out :)")
    
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
    global MANUAL_SCORING, PRESENTATION_MODE, PRESENTATION_SCREEN_ID, CONSOLE_TIME

    f = open("settings.json", "r")
    settings = json.load(f)

    SERIAL_PORT = settings["serial COM port"]
    SERIAL_BAUDRATE = settings["serial baud rate"]

    COUNTDOWN_INTERVAL = settings["countdown interval"] * 1e9
    MATCH_DURATION = settings["match duration"] * 1e9
    ENDGAME_DURATION = settings["endgame duration"] * 1e9
    HOLD_DURATION = settings["hold duration"] * 1e9
    
    SOUND_START_PATH = "./Sounds/" + settings["start sound file name"]
    SOUND_END_PATH = "./Sounds/" + settings["end sound file name"]
    SOUND_COUNTDOWN_PATH = "./Sounds/" + settings["countdown sound file name"]
    SOUND_ENDGAME_PATH = "./Sounds/" + settings["endgame sound file name"]

    SENSOR_SCORING = settings["sensor scoring enabled"]
    ESP32_ATTACHED = settings["eps32 attached"]

    BALL_DROP_1 = settings["first ball drop"] * 1e9
    BALL_DROP_2 = settings["second ball drop"] * 1e9
    BALL_DROP_3 = settings["third ball drop"] * 1e9

    MANUAL_SCORING = settings["manual scoring"]
    PRESENTATION_MODE = settings["activate full screen mode"]
    PRESENTATION_SCREEN_ID = settings["secondary screen ID"]
    CONSOLE_TIME = settings["time display in console"]

    f.close()


def handle_serial_data(data, ball_finder):
    if not SENSOR_SCORING:
        return
    state_changed = False

    if "Distance at sensor" == data[0:18]:
        i2c_address = data[19:21]
        distance = data[23:]

        if i2c_address != ball_finder.sensor_id:
            return

        position = ball_finder.position
        ball_finder.new_datapoint(int(distance))
        if ball_finder.check_for_ball():
            state["balls"][position] = state["balls"][position] + 1
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

    print(events)

    #initialize socrer
    scorer = Scorer.Scorer()

    #initialize window
    window = Window(state)
    window.change_state("Waiting for thumbs up")

    #init ball finders
    ball_finder_blu_top = BallFinder("29", "blu_top")  #one sensor test
    ball_finder_blu_mid = BallFinder("91", "blu_mid")
    ball_finder_blu_low = BallFinder("92", "blu_low")

    ball_finder_red_top = BallFinder("93", "red_top")
    ball_finder_red_mid = BallFinder("94", "red_mid")
    ball_finder_red_low = BallFinder("95", "red_low")

    #init serial
    if(ESP32_ATTACHED):
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
        print("Serial Open")

    wait_for_start(window)

    #time variables
    time_zero_ns = time.time_ns() + HOLD_DURATION
    last_displayed_timestamp = 0

    #global updating_state_gui
    #global updating_time_gui
    updating_time_gui = True
    updating_state_gui = True

    while True:

        #update window
        window.update()

        #upate time
        state["time"] = round((time.time_ns() - time_zero_ns) / 1000000000, 4)
        state["time_ns"] = time.time_ns() - time_zero_ns

        #manual scoring
        if MANUAL_SCORING:
            run_manual_scoring()

        #update scheduled events
        handle_scheduled_events()
        
        #read balls and log stuff
        if((state["period"] == "endgame" or state["period"] == "regulation") and SENSOR_SCORING):
            data = read_serial(ser)

            a = handle_serial_data(data, ball_finder_blu_top)
            b = handle_serial_data(data, ball_finder_blu_mid)
            c = handle_serial_data(data, ball_finder_blu_low)
            
            d = handle_serial_data(data, ball_finder_red_top)
            e = handle_serial_data(data, ball_finder_red_mid)
            f = handle_serial_data(data, ball_finder_red_low)

        #decisec display
        if time.time_ns() >= last_displayed_timestamp + 250000000 and CONSOLE_TIME:   
            last_displayed_timestamp = time.time_ns()
            t = state["time"]
            t_ns = state["time_ns"]
            print(f"time match software: {t} - time ns: {t_ns}")