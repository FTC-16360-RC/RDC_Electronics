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

#main window for the match - controller display 
class Controller(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("RDC Match Display")
        self.geometry("800x600")
        
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
        
    def reset_match(self):
        global match_settings, blue_score, red_score
        blue_score.reset_team_score()
        red_score.reset_team_score()
        match_settings.reset_matchstate()
        match_settings.show_confirm.set(value = False)
    
    def toggle_confirm(self):
        global match_settings

        if(self.showed_confirm == False):
            match_settings.show_confirm.set(value = True)
            self.showed_confirm = True
            match_settings.match_stopped.set(value = False)

        else:
            match_settings.show_confirm.set(value = False)
            match_settings.match_stopped.set(value = True)
            self.showed_confirm = False

    ''' EDIT HERE FOR SERVO ACTION!!!!------------------------------------------------------------------------------------------------'''
    def update_matchtimer(self):
        global match_settings
        current_time = match_settings.current_time.get()
        
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
            match_settings.current_time.set(current_time -0.3) 
            self.after(10, self.update_matchtimer) #initiate the next instance
        else:
            print("Match Ended------------------------------------")
            match_settings.match_stopped.set(value = True)
            pass 
        print(current_time)
        print(match_settings.event_trigger.get())

    
    #start the match after the entire setup is done
    def start_match(self):
        global match_settings, blue_score, red_score

        match_settings.match_stopped.set(False)
        blue_score.reset_team_score()
        red_score.reset_team_score()
        match_settings.show_confirm.set(False)

        self.update_matchtimer()
    '''define functions that act on certain timed events, like ball drop and add functions in update_matchtimer function'''

    


#all the settings (may replace settings.json)
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

        '''
        #settings for total time
        time_display = labeled_box(self, ":Total Time", "120s")
        time_display.pack(side = 'top', fill = tk.BOTH, expand = True, padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        #time for refill
        refill_display = labeled_box(self, ":Refill Time", "30s")
        refill_display.pack(side = 'top', fill = tk.BOTH, expand = True, padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        #other crazy___ setting
        other_display = labeled_box(self, ":This is a very long long label:", "30s")
        other_display.pack(side = 'top', fill = tk.BOTH, expand = True, padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        pass
        '''

#scoring for both teams

''' EDIT HERE OR TAKE AS REFERENCE!!!----------------------------------------------------------------------------------------------------------'''
class Scoring(ctk.CTkFrame):
    def __init__(self, master, color, team):
        super().__init__(master, fg_color = color)
        self.color = color

        self.columnconfigure(0, weight = 1, uniform = 'a')
        self.columnconfigure(1, weight = 1, uniform = 'a')

        self.rowconfigure(0, weight = 1, uniform = 'b')
        self.rowconfigure(1, weight = 1, uniform = 'b')

        self.Frame_goals = ctk.CTkFrame(self, fg_color = 'grey')
        self.Frame_goals.pack(side= 'left', fill = tk.BOTH, expand = False, padx = 10 * scaling_unit, pady = 10 * scaling_unit)

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

controller = Controller()
controller.mainloop()
