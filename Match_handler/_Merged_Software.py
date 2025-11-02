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

#sk
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from  PIL import Image, ImageTk
import os
import Settings
import TeamDisplay


match_settings = None
blue_score = None
red_score = None
redcolor = '#ff9028'
bluecolor = '#08cdf9'
scaling_unit_height = 1
scaling_unit_width = 1
scaling_unit = 1
groundcolor = '#574f4e'
transparent_grey = '#808080'
greencolor = '#038024'
#sk


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
SOUND_BALLDROP_PATH = ""
SOUND_CONFIRM_PATH = ""

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
    print(f"Writing Serial Command: {command}")
    ser.write((command + '\n').encode('utf-8'))
    log_data(f"serial command {command}")

    time.sleep(3)


def init_events():
     #----Schedule Events-----
        #set sound timings
        schedule_event(["PLAY_SOUND", MATCH_DURATION + 1e9, False, SOUND_START_PATH])
        schedule_event(["PLAY_SOUND", ENDGAME_DURATION, False, SOUND_ENDGAME_PATH])
        schedule_event(["PLAY_SOUND", 0 + 1e9, False, SOUND_END_PATH])

        schedule_event(["PLAY_SOUND", 1 * COUNTDOWN_INTERVAL + MATCH_DURATION + 1e9, False, SOUND_COUNTDOWN_PATH])
        schedule_event(["PLAY_SOUND", 2 * COUNTDOWN_INTERVAL + MATCH_DURATION + 1e9, False, SOUND_COUNTDOWN_PATH])
        schedule_event(["PLAY_SOUND", 3 * COUNTDOWN_INTERVAL + MATCH_DURATION + 1e9, False, SOUND_COUNTDOWN_PATH])

        schedule_event(["PLAY_SOUND", 1 * COUNTDOWN_INTERVAL + 1e9, False, SOUND_COUNTDOWN_PATH])
        schedule_event(["PLAY_SOUND", 2 * COUNTDOWN_INTERVAL + 1e9, False, SOUND_COUNTDOWN_PATH])
        schedule_event(["PLAY_SOUND", 3 * COUNTDOWN_INTERVAL + 1e9, False, SOUND_COUNTDOWN_PATH])

        #schedule match events
        schedule_event(["START_REGULATION", MATCH_DURATION + 1e9, False]) 
        schedule_event(["START_ENDGAME", ENDGAME_DURATION, False]) 
        schedule_event(["END_MATCH", 0 + 1e9, False]) 

        #set Ball Tower Servo serial timings
        schedule_event(["SERIAL_MESSAGE", BALL_DROP_1, False, "BLU_LOW_OPEN"])
        #schedule_event(["PLAY_SOUND", BALL_DROP_1 + 1.5e9, False, SOUND_BALLDROP_PATH])
        #schedule_event(["SERIAL_MESSAGE", BALL_DROP_1, False, "RED_LOW_OPEN"])

        schedule_event(["SERIAL_MESSAGE", BALL_DROP_2, False, "BLU_MID_OPEN"])
        #schedule_event(["PLAY_SOUND", BALL_DROP_2 + 1.5e9 , False, SOUND_BALLDROP_PATH])
        #schedule_event(["SERIAL_MESSAGE", BALL_DROP_2, False, "RED_MID_OPEN"])

        schedule_event(["SERIAL_MESSAGE", BALL_DROP_3, False, "BLU_TOP_OPEN"])
        #schedule_event(["PLAY_SOUND", BALL_DROP_3 + 1.5e9, False, SOUND_BALLDROP_PATH])
        #schedule_event(["SERIAL_MESSAGE", BALL_DROP_3, False, "RED_TOP_OPEN"])

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


#...
def read_serial(ser):
    if ser.in_waiting > 0:
        data = ser.readline().decode('latin1').strip()
        #if "Distance at sensor" != data[0:18]:
        #    send_serial_command(data)
        #    return "XXX"
        return data
    else:
        return "XXXX"


def load_settings():
    global SERIAL_PORT, SERIAL_BAUDRATE, MATCH_DURATION, ENDGAME_DURATION
    global COUNTDOWN_INTERVAL, MATCH_DURATION, HOLD_DURATION
    global SOUND_START_PATH, SOUND_END_PATH, SOUND_COUNTDOWN_PATH, SOUND_ENDGAME_PATH, SOUND_BALLDROP_PATH, SOUND_CONFIRM_PATH
    global SENSOR_SCORING, ESP32_ATTACHED
    global BALL_DROP_1, BALL_DROP_2, BALL_DROP_3
    global MANUAL_SCORING, PRESENTATION_MODE, PRESENTATION_SCREEN_ID, CONSOLE_TIME

    f = open("_settings.json", "r")
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
    SOUND_BALLDROP_PATH = "./Sounds/" + settings["balldrop sound file name"]
    SOUND_CONFIRM_PATH = "./Sounds/" + settings["confirm sound file name"]

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


def increase_score(position):
    print("pos: ", position)
    global blue_score, red_score
    if (position == "blu_top"):
        score = blue_score.highgoal.get() + 1
        blue_score.highgoal.set(score)
    if (position == "blu_mid"):
        score = blue_score.midgoal.get() + 1
        blue_score.midgoal.set(score)
    if (position == "blu_low"):
        score = blue_score.lowgoal.get() + 1
        blue_score.lowgoal.set(score)
    
    if (position == "red_top"):
        score = red_score.highgoal.get() + 1
        red_score.highgoal.set(score)
    if (position == "red_mid"):
        score = red_score.midgoal.get() + 1
        red_score.midgoal.set(score)
    if (position == "red_low"):
        score = red_score.lowgoal.get() + 1
        red_score.lowgoal.set(score)


def handle_serial_data(data, ball_finder):
    #print("handeling data: ", data)
    if not SENSOR_SCORING:
        return
    state_changed = False

    if "Distance at sensor" == data[0:18]:
        i2c_address = data[19:21]
        distance = data[23:]

        if i2c_address != ball_finder.sensor_id:
            return

        position = ball_finder.position
        ball_finder.new_datapoint(round(float(distance)))
        if ball_finder.check_for_ball():
            state["balls"][position] = state["balls"][position] + 1
            log_data("ball")
            state_changed = True
            increase_score(position)
            print("-sensed ball!")

        return state_changed
    else:
        return False


def handle_scheduled_events():
    global events
    global match_settings
    global state

    for event in events:
        #if executed
        if event[2]:
            continue

        #check if we don't have to execute event yet
        if state["time_ns"] > event[1]:
            continue
        
        if event[0] == "PLAY_SOUND":
            play_sound(event[3])
            event[2] = True
            print("SOUND")
            continue
        
        if event[0] == "SERIAL_MESSAGE":
            serial_thread = threading.Thread(target=send_serial_command, args=(event[3],))
            serial_thread.start()
            #send_serial_command(event[3])
            event[2] = True
            continue
        
        if event[0] == "START_REGULATION":
            print("were regulationg")
            state["period"] = "regulation"
            event[2] = True
            continue
        
        if event[0] == "START_ENDGAME":
            print("were gaming")
            state["period"] = "endgame"
            event[2] = True
            continue

        if event[0] == "END_MATCH":
            #end_match()
            event[2] = True
            continue


def schedule_event(event):
    global events

    events.append(event)


class Controller(ctk.CTk):

    def __init__(self):
        global ser
        global ball_finder_blu_top, ball_finder_blu_mid, ball_finder_blu_low
        global ball_finder_red_top, ball_finder_red_mid, ball_finder_red_low



        super().__init__()
        self.title("RDC Match Display")
        self.geometry("800x600")

        #load settings
        load_settings()

        #load events 
        init_events()

        #init ball finders
        ball_finder_blu_top = BallFinder("25", "blu_top")  #one sensor test
        ball_finder_blu_mid = BallFinder("33", "blu_mid")
        ball_finder_blu_low = BallFinder("32", "blu_low")

        ball_finder_red_top = BallFinder("22", "red_top")
        ball_finder_red_mid = BallFinder("14", "red_mid")
        ball_finder_red_low = BallFinder("26", "red_low")

        #init serial
        if(ESP32_ATTACHED):
            ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)
            print("Serial Open")

        #init sound mixer
        pygame.mixer.quit()
        pygame.mixer.init()


        #settings conflict !!!!!  resolve
        global match_settings, blue_score, red_score
        match_settings = Settings.MatchSettings()
        blue_score = Settings.TeamScores()
        red_score = Settings.TeamScores()

        #define a grid
        self.columnconfigure(0, weight = 2, uniform = 'b')
        self.columnconfigure(1, weight = 2, uniform = 'b')

        self.rowconfigure(0, weight = 75)
        self.rowconfigure(1, weight = 25)
        self.rowconfigure(2, weight = 25,)

        #define the frames
        self.Settings = SettingsDisplay(self)
        self.Settings.grid(row = 0, column = 0, columnspan = 2, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        #define all the buttons to control match
        self.Button_frame = ctk.CTkFrame(self, fg_color = groundcolor)
        self.Button_frame.grid(row = 1, column = 0, columnspan = 2, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        self.InitDisplay = ctk.CTkButton(self.Button_frame, text = "Init Display", fg_color = '#870065', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, command = self.start_display)
        self.InitDisplay.pack(expand = True, fill = 'both', side = 'left', padx = 10 * scaling_unit, pady = 10 * scaling_unit)

        self.StartMatch = ctk.CTkButton(self.Button_frame, text = "Start Match", fg_color = 'green', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, command = self.start_match)
        self.StartMatch.pack(expand = True, fill = 'both', side = 'left', padx = 10 * scaling_unit, pady = 10 * scaling_unit)

        self.ConfirmScore = ctk.CTkButton(self.Button_frame, text = "Confirm Score", fg_color = 'blue', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, command = self.toggle_confirm)
        self.showed_confirm = False
        self.ConfirmScore.pack(expand = True, fill = 'both', side = 'left', padx = 10 * scaling_unit, pady = 10 * scaling_unit)

        self.ResetScore = ctk.CTkButton(self.Button_frame, text = "Reset Match", fg_color = 'red', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, command = self.reset_match)
        self.ResetScore.pack(expand = True, fill = 'both', side = 'left', padx = 10 * scaling_unit, pady = 10 * scaling_unit)

        #load two frames for both teams' scores
        self.Scoring_blue = Scoring(self, bluecolor, blue_score)
        self.Scoring_blue.grid(row = 2, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        self.Scoring_red = Scoring(self, redcolor, red_score)
        self.Scoring_red.grid(row = 2, column = 1, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

    #start the display for the teams
    def start_display(self):
        global match_settings, blue_score, red_score
        print("Display Started")
        self.team_display = TeamDisplay.Display(self, match_settings, blue_score, red_score)
        self.team_display.mainloop()

        print("start_display called")
        
    def reset_match(self):
        global match_settings, blue_score, red_score

        init_events()
        blue_score.reset_team_score()
        red_score.reset_team_score()
        match_settings.reset_matchstate()
        match_settings.show_confirm.set(value = False)

        print("reset_match called")
    
    def toggle_confirm(self):
        global match_settings

        if(self.showed_confirm == False):
            play_sound(SOUND_CONFIRM_PATH)
            match_settings.show_confirm.set(value = True)
            self.showed_confirm = True
            match_settings.match_stopped.set(value = False)

            points = calculate_points()
            log.append({"blue end points: " : blue_score.total_score})
            log.append({"red end points: " : red_score.total_score})

            print(log)
            f = open("Match log " + str(datetime.datetime.now()).replace(":","_").replace(".","_") + ".json", "x") 
            f.write(json.dumps(log))
            f.close()

            print("written log to file")

        else:
            match_settings.show_confirm.set(value = False)
            match_settings.match_stopped.set(value = True)
            self.showed_confirm = False
        
        print("toggle_confirm called")

    ''' EDIT HERE FOR SERVO ACTION!!!!------------------------------------------------------------------------------------------------'''
    def update_matchtimer(self):
        global match_settings
        global state

        current_time = match_settings.current_time.get()
        state["time_ns"] = current_time * 1e9
        
        new_status = False

        #update refill timer
        if current_time > match_settings.firstball_drop:
            match_settings.refill_time.set(int(current_time - match_settings.firstball_drop))
            match_settings.event_trigger.set("waiting_firstdrop")
        elif current_time > match_settings.secondball_drop:
            match_settings.refill_time.set(int(current_time - match_settings.secondball_drop))
            match_settings.event_trigger.set("waiting_seconddrop")
        elif current_time > match_settings.thirdball_drop:
            match_settings.refill_time.set(int(current_time - match_settings.thirdball_drop))
            match_settings.event_trigger.set("waiting_thirddrop")
        elif current_time > match_settings.endgame_duration:
            match_settings.refill_time.set(int(current_time - match_settings.endgame_duration))
            match_settings.event_trigger.set("waiting_endgame")
        elif current_time < match_settings.endgame_duration:
            match_settings.refill_time.set(-1)
            match_settings.event_trigger.set(value ="endgame")
        else:
            print("undefined match_state ____________________________________")
            
        #advance the matchtimer
        if current_time > 0 and match_settings.match_stopped.get() != True:
            match_settings.current_time.set(match_settings.total_matchtime - (time.time() - match_settings.start_time)) #SPEED HERE
            self.after(10, self.update_matchtimer) #initiate the next instance
        else:
            print("Match Ended------------------------------------")
            match_settings.match_stopped.set(value = True)
            pass 
        
        #print(state["time_ns"] / 1e9 )
        #print(match_settings.event_trigger.get())

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

    
    #start the match after the entire setup is done
    def start_match(self):
        global match_settings, blue_score, red_score

        print("start_match called")

        match_settings.match_stopped.set(False)
        blue_score.reset_team_score()
        red_score.reset_team_score()
        match_settings.show_confirm.set(False)
        match_settings.start_time = time.time()

        self.update_matchtimer()
    '''define functions that act on certain timed events, like ball drop and add functions in update_matchtimer function'''


class SettingsDisplay(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.add_teamnames()

    def add_teamnames(self):
        
        global match_settings 
        #teamnames
        team1_1_entry = ctk.CTkEntry(self, placeholder_text = "Blue 1 ", textvariable= match_settings.teamblue_1_name, fg_color = bluecolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)
        team1_2_entry = ctk.CTkEntry(self, placeholder_text = "Blue 2 ", textvariable= match_settings.teamblue_2_name, fg_color = bluecolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)
        team2_1_entry = ctk.CTkEntry(self, placeholder_text = "Red 1 ", textvariable= match_settings.teamred_1_name, fg_color = redcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)
        team2_2_entry = ctk.CTkEntry(self, placeholder_text = "Red 2 ",textvariable= match_settings.teamred_2_name, fg_color = redcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)

        team1_1_entry.pack(side = 'top', fill = tk.BOTH, expand = True, padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        team1_2_entry.pack(side = 'top', fill = tk.BOTH, expand = True, padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        team2_1_entry.pack(side = 'top', fill = tk.BOTH, expand = True, padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        team2_2_entry.pack(side = 'top', fill = tk.BOTH, expand = True, padx = 5 * scaling_unit, pady = 5 * scaling_unit)


class Scoring(ctk.CTkFrame):
    def __init__(self, master, color, team):
        super().__init__(master, fg_color = color)
        self.color = color

        self.columnconfigure(0, weight = 1, uniform = 'a')
        self.columnconfigure(1, weight = 1, uniform = 'a')

        self.rowconfigure(0, weight = 1, uniform = 'b')
        self.rowconfigure(1, weight = 1, uniform = 'b')

        self.Frame_goals = ctk.CTkFrame(self, fg_color = 'gray')
        self.Frame_goals.pack(side= 'left', fill = tk.BOTH, expand = False, padx = 10 * scaling_unit, pady = 10 * scaling_unit)

        self.Frame_goals_team = ctk.CTkFrame(self, fg_color = 'palegreen')
        self.Frame_goals_team.pack(side= 'left', fill = tk.BOTH, expand = False, padx = 10 * scaling_unit, pady = 10 * scaling_unit)

        self.Frame_other = ctk.CTkFrame(self, fg_color = 'grey')
        self.Frame_other.pack(side = 'left', fill = tk.BOTH, expand = False, padx = 10 * scaling_unit, pady = 10 * scaling_unit)

        #actually create the interfaces
        self.create_goals(team)
        self.create_other(team)

    def create_goals(self, team):

        #define grid
        self.columnconfigure(0, weight = 1, uniform = 'a')
        self.columnconfigure(1, weight = 1, uniform = 'a')
        self.columnconfigure(2, weight = 1, uniform = 'a')

        self.rowconfigure(0, weight = 1, uniform = 'b')
        self.rowconfigure(1, weight = 1, uniform = 'b')
        self.rowconfigure(2, weight = 1, uniform = 'b')
        self.rowconfigure(3, weight = 1, uniform = 'b')

        
        #define points labels
        self.highgoal_label = ctk.CTkLabel(self.Frame_goals, textvariable = team.highgoal, fg_color = groundcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)
        self.midgoal_label = ctk.CTkLabel(self.Frame_goals, textvariable = team.midgoal, fg_color = groundcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)
        self.lowgoal_label = ctk.CTkLabel(self.Frame_goals, textvariable = team.lowgoal, fg_color = groundcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)

        self.highgoal_label.grid(row = 1, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.midgoal_label.grid(row = 2, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.lowgoal_label.grid(row = 3, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        #define plus_buttons
        self.highgoal_button_p = ctk.CTkButton(self.Frame_goals, text = "+", fg_color = 'green', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.increment_score(team.highgoal))
        self.midgoal_button_p = ctk.CTkButton(self.Frame_goals, text = "+", fg_color = 'green', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.increment_score(team.midgoal))
        self.lowgoal_button_p = ctk.CTkButton(self.Frame_goals, text = "+", fg_color = 'green', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.increment_score(team.lowgoal))

        self.highgoal_button_p.grid(row = 1, column = 1, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.midgoal_button_p.grid(row = 2, column = 1, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.lowgoal_button_p.grid(row = 3, column = 1, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        #define_minus_buttons   
        self.highgoal_button_m = ctk.CTkButton(self.Frame_goals, text = "-", fg_color = 'red', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.decrement_score(team.highgoal))
        self.midgoal_button_m = ctk.CTkButton(self.Frame_goals, text = "-", fg_color = 'red', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.decrement_score(team.midgoal))
        self.lowgoal_button_m = ctk.CTkButton(self.Frame_goals, text = "-", fg_color = 'red', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.decrement_score(team.lowgoal))

        self.highgoal_button_m.grid(row = 1, column = 2, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.midgoal_button_m.grid(row = 2, column = 2, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.lowgoal_button_m.grid(row = 3, column = 2, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        self.total_name_label = ctk.CTkLabel(self.Frame_goals, text = "Total:", fg_color = 'grey', font = ('Helvetica', 10 * scaling_unit, 'bold'), corner_radius = 15)
        self.total_name_label.grid(row = 4, column = 0, columnspan = 1, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        self.total_score_label = ctk.CTkLabel(self.Frame_goals, textvariable = team.total_score, fg_color = self.color, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)    
        self.total_score_label.grid(row = 4, column = 1, columnspan = 2, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)


        #hacked in
        #
        #pt labels
        self.highgoal_label_team = ctk.CTkLabel(self.Frame_goals_team, textvariable = team.highgoal_team, fg_color = groundcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)
        self.midgoal_label_team = ctk.CTkLabel(self.Frame_goals_team, textvariable = team.midgoal_team, fg_color = groundcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)
        self.lowgoal_label_team = ctk.CTkLabel(self.Frame_goals_team, textvariable = team.lowgoal_team, fg_color = groundcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)

        self.highgoal_label_team.grid(row = 1, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.midgoal_label_team.grid(row = 2, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.lowgoal_label_team.grid(row = 3, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        #define plus_buttons
        self.highgoal_button_p_team = ctk.CTkButton(self.Frame_goals_team, text = "+", fg_color = 'green', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.increment_score(team.highgoal_team))
        self.midgoal_button_p_team = ctk.CTkButton(self.Frame_goals_team, text = "+", fg_color = 'green', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.increment_score(team.midgoal_team))
        self.lowgoal_button_p_team = ctk.CTkButton(self.Frame_goals_team, text = "+", fg_color = 'green', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.increment_score(team.lowgoal_team))

        self.highgoal_button_p_team.grid(row = 1, column = 1, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.midgoal_button_p_team.grid(row = 2, column = 1, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.lowgoal_button_p_team.grid(row = 3, column = 1, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        #define_minus_buttons   
        self.highgoal_button_m_team = ctk.CTkButton(self.Frame_goals_team, text = "-", fg_color = 'red', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.decrement_score(team.highgoal_team))
        self.midgoal_button_m_team = ctk.CTkButton(self.Frame_goals_team, text = "-", fg_color = 'red', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.decrement_score(team.midgoal_team))
        self.lowgoal_button_m_team = ctk.CTkButton(self.Frame_goals_team, text = "-", fg_color = 'red', font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.decrement_score(team.lowgoal_team))

        self.highgoal_button_m_team.grid(row = 1, column = 2, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.midgoal_button_m_team.grid(row = 2, column = 2, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.lowgoal_button_m_team.grid(row = 3, column = 2, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        self.team_label = ctk.CTkLabel(self.Frame_goals_team, text = "Team", fg_color = 'grey', font = ('Helvetica', 10 * scaling_unit, 'bold'), corner_radius = 15)
        self.team_label.grid(row = 4, column = 0, columnspan = 1, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        #
        #




    #create all the other opportunities for points inclduing parking and penalty
    def create_other(self, team):

        #define grid
        self.columnconfigure(0, weight = 10, uniform = 'a')
        self.columnconfigure(1, weight = 1, uniform = 'a')
        self.columnconfigure(2, weight = 1, uniform = 'a')

        self.rowconfigure(0, weight = 1, uniform = 'b')
        self.rowconfigure(1, weight = 1, uniform = 'b')
        self.rowconfigure(2, weight = 2, uniform = 'b')
        self.rowconfigure(3, weight = 2, uniform = 'b')

        #define dropdown menu with 3 states of climbing and a label for robot 1
        self.climbing_label_1 = ctk.CTkLabel(self.Frame_other, text = "Robot 1", fg_color = groundcolor, font = ('Helvetica', 10 * scaling_unit,), corner_radius = 0)
        self.climbing_label_1.grid(row = 1, column = 0, columnspan = 1, sticky = 'nsew', padx = 0 * scaling_unit, pady = 5 * scaling_unit)

        
        self.climbing_dropdown_1 = ctk.CTkOptionMenu(self.Frame_other, variable = team.robot1_park, values = ["not parked", "low park", "high park"])
        self.climbing_dropdown_1.grid(row=1, column=1, columnspan=2, sticky='nsew', padx=0 * scaling_unit, pady=5 * scaling_unit)

        #define dropdown menu with 3 states of climbing and a label for robot 2
        self.climbing_label_2 = ctk.CTkLabel(self.Frame_other, text = "Robot 1", fg_color = groundcolor, font = ('Helvetica', 10 * scaling_unit,), corner_radius = 0)
        self.climbing_label_2.grid(row = 2, column = 0, columnspan = 1, sticky = 'nsew', padx = 0 * scaling_unit, pady = 5 * scaling_unit)

        self.climbing_dropdown_2 = ctk.CTkOptionMenu(self.Frame_other, variable = team.robot2_park , values = ["not parked", "low park", "high park"])
        self.climbing_dropdown_2.grid(row=2, column=1, columnspan=2, sticky='nsew', padx=0 * scaling_unit, pady=5 * scaling_unit)


        #create penalty points in the form of a label, where the amount of current penalty points is displayed and four buttons where one can add and remove two different amounts of points
        self.penalty_label = ctk.CTkLabel(self.Frame_other, textvariable = team.penalty, fg_color = groundcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'))
        self.penalty_label.grid(row = 4, column = 0, sticky = 'nsew', padx = 0 * scaling_unit, pady = 1 * scaling_unit)

        self.penalty_text_label = ctk.CTkLabel(self.Frame_other, text = "Penalty Points:", fg_color = groundcolor, font = ('Helvetica', 8 * scaling_unit, 'bold'))
        self.penalty_text_label.grid(row = 3, column = 0, sticky = 'nsew', padx =0 * scaling_unit, pady = 1 * scaling_unit)

        self.penalty_button_p1 = ctk.CTkButton(self.Frame_other, text = "+small", fg_color = 'green', font = ('Helvetica', 10 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.small_penalty(team.penalty))
        self.penalty_button_p2 = ctk.CTkButton(self.Frame_other, text = "+big", fg_color = 'green', font = ('Helvetica', 10 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.big_penalty(team.penalty))
        self.penalty_button_m1 = ctk.CTkButton(self.Frame_other, text = "-small", fg_color = 'red', font = ('Helvetica', 10 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.small_penalty(team.penalty, False))
        self.penalty_button_m2 = ctk.CTkButton(self.Frame_other, text = "-big", fg_color = 'red', font = ('Helvetica', 10 * scaling_unit, 'bold'), corner_radius = 15, width = 10, command = lambda: team.big_penalty(team.penalty, False))

        self.penalty_button_p1.grid(row = 3, column = 1, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.penalty_button_p2.grid(row = 4, column = 1, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.penalty_button_m1.grid(row = 3, column = 2, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
        self.penalty_button_m2.grid(row = 4, column = 2, sticky = 'ns', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

#use for in display, e.g. for settings
class labeled_box(ctk.CTkFrame):
    def __init__(self, master, labeltext, boxtext):
        super().__init__(master)

        
        self.box = ctk.CTkEntry(self, placeholder_text = boxtext, fg_color = groundcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 50)
        self.box.pack(side = 'left', fill = tk.BOTH, expand = False, padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        self.label = ctk.CTkLabel(self, text = labeltext, fg_color = "transparent", font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 60)
        self.label.pack(side = 'left', fill = tk.BOTH, expand = False, padx = 5 * scaling_unit, pady = 5 * scaling_unit)


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


def end_match():
    global updating_time_gui

    updating_time_gui = False

    window.change_state("end")
    window.override_time(f"{MATCH_DURATION/1e9} / {MATCH_DURATION/1e9}")
    state["period"] = "finished"

    print("END!!!")
    print("press <ENTER> to confirm points")

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


if __name__ == "__main__":
    controller = Controller()
    controller.mainloop()

        