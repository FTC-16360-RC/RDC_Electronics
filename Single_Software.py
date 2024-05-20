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

sounds_to_play = [
    #[SOUND_PATH, time, played]
]

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

SENSOR_SCORING = True



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
    print(f"loading {sound_file}")
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()
    print("PLAYSOUND")


def log_data(message = ""):
    state["message"] = message
    log.append(copy.deepcopy(state))


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
    global SENSOR_SCORING

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


def handle_sounds():
    global sounds_to_play

    for sound in sounds_to_play:
        #if played
        if sound[2]:
            continue

        if state["time_ns"] >= sound[1]:
            print(f"playing sound {sound[0]}")
            play_sound(sound[0])
            sound[2] = True
        

def play_sound_at_time(sound, time_ns):
    global sounds_to_play

    #if(time_ns < state["time_ns"]):
        #return
    sounds_to_play.append([sound, time_ns, False])


if __name__ == "__main__":

    load_settings()

    pygame.mixer.quit()
    pygame.mixer.init()

    #set sound timings
    play_sound_at_time(SOUND_START_PATH, 0)
    play_sound_at_time(SOUND_ENDGAME_PATH, MATCH_DURATION - ENDGAME_DURATION)
    play_sound_at_time(SOUND_END_PATH, MATCH_DURATION)

    play_sound_at_time(SOUND_COUNTDOWN_PATH, -1 * COUNTDOWN_INTERVAL)
    play_sound_at_time(SOUND_COUNTDOWN_PATH, -2 * COUNTDOWN_INTERVAL)
    play_sound_at_time(SOUND_COUNTDOWN_PATH, -3 * COUNTDOWN_INTERVAL)

    play_sound_at_time(SOUND_COUNTDOWN_PATH, -1 * COUNTDOWN_INTERVAL + MATCH_DURATION)
    play_sound_at_time(SOUND_COUNTDOWN_PATH, -2 * COUNTDOWN_INTERVAL + MATCH_DURATION)
    play_sound_at_time(SOUND_COUNTDOWN_PATH, -3 * COUNTDOWN_INTERVAL + MATCH_DURATION)

    #initialize window
    window = Window(state)
    window.change_state("match about to start")

    #time variables
    time_zero_ns = time.time_ns() + HOLD_DURATION
    last_displayed_timestamp = 0

    #init ball finders
    ball_finder_blue_high = BallFinder("29")  #one sensor test
    ball_finder_blue_mid = BallFinder("91")
    ball_finder_blue_push = BallFinder("92")

    ball_finder_orange_high = BallFinder("93")
    ball_finder_orange_mid = BallFinder("94")
    ball_finder_orange_push = BallFinder("95")

    ser = "NONE"
    #init serial
    if(SENSOR_SCORING):
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
        print("Serial Open")

    while True:

        #update window
        window.update()
        window.update_time(time_zero_ns)
        window.update_state(state)

        #upate time
        state["time"] = round((time.time_ns() - time_zero_ns) / 1000000000, 4)
        state["time_ns"] = time.time_ns() - time_zero_ns

        #update sounds
        handle_sounds()

        #match start trigger
        if time.time_ns() >= time_zero_ns and state["period"] == "holding":
            print("Game Started")
            window.change_state("match running")
            #log_data("game started")
            state["period"] = "regulation"

        #endgame trigger
        if time.time_ns() - time_zero_ns >= (MATCH_DURATION - ENDGAME_DURATION) and state["period"] == "regulation":  
            print("ENDGAME!!!!")
            window.change_state("endgame")
            #log_data("start of endgame")
            state["period"] = "endgame"
        
        #game end trigger
        if time.time_ns() - time_zero_ns >= MATCH_DURATION and not state["period"] == "finished":
            print("Game Over")
            window.change_state("end")
            #log_data("finished")
            state["period"] = "finished"
            end_match()

            #end loop
            while True:
                window.update()

        
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