import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
from screeninfo import get_monitors

from  PIL import Image, ImageTk
import os

pointslow = 5
pointsmid = 7
pointshigh = 10
pointsparkhigh = 15
pointsparklow = 6
small_penalty = -15
big_penalty = -30


match_settings = None
#redcolor = '#ff9028'
redcolor = '#08cdf9'
bluecolor = '#e58124'  #RED AND BLUE SWITCHED!!
scaling_unit_height = 1
scaling_unit_width = 1
scaling_unit = 1
groundcolor = '#574f4e'
transparent_grey = '#808080'
#transparent_grey = '#737373'
greencolor = '#038024'
pinkcolor = '#cc376e'

'''#main window for the team display '''
class Display(ctk.CTkToplevel):
    def __init__(self, parent, settings, blue_score, red_score):
        global match_settings
        match_settings = settings
        self.red_score =   red_score
        self.blue_score = blue_score

        #select second monitor
        monitors = get_monitors()
        second_screen = monitors[0]  #CHANGE BEFORE NEXT YEAR!!!!!
    

        super().__init__(parent)
        self.title("RDC Match Display")
        self.geometry("800x600")
        #self.style = ttk.Style()
        #self.style.theme_use("bootstrap")
        #self.create_widgets()
        self.match_settings = match_settings

        #define a grid
        self.columnconfigure(0, weight = 3, uniform = 'b')
        self.columnconfigure(1, weight = 2, uniform = 'b')
        self.columnconfigure(2, weight = 3, uniform = 'b')

        self.rowconfigure(0, weight = 75)
        self.rowconfigure(1, weight = 25)

        #define the frames
        self.blue_console = TeamConsole(self, bluecolor, blue_score)
        self.blue_console.grid(row = 0, column = 0, sticky = 'nsew')

        self.middle_console = MiddleConsole(self)
        self.middle_console.grid(row = 0, column = 1, sticky = 'nsew')

        self.red_console = TeamConsole(self, redcolor, red_score)
        self.red_console.grid(row = 0, column = 2, sticky = 'nsew')

        self.match_status_console = MatchStatusConsole(self, blue_score, red_score)
        self.match_status_console.grid(row = 1, column = 0, columnspan = 3, sticky = 'nsew')

        #close the app on escape
        self.bind("<Escape>", lambda event: self.destroy())

        #final frame

        self.final_frame = ctk.CTkFrame(self,fg_color = groundcolor)
        self.display_final_score()

        match_settings.show_confirm.trace_add("write", self.confirm_score)

        #make fullscreen
        #self.wm_attributes('-fullscreen', True)


    def confirm_score(self, *args):


        if(match_settings.show_confirm.get()):
            #display winner
            if(self.blue_score.total_score.get() > self.red_score.total_score.get()):
                self.winner_label.grid(row = 0, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
                self.draw_1_label.grid_forget()
                self.draw_2_label.grid_forget()
            elif(self.blue_score.total_score.get() < self.red_score.total_score.get()):
                self.winner_label.grid(row = 0, column = 2, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
                self.draw_1_label.grid_forget()
                self.draw_2_label.grid_forget()
            else:
                self.draw_2_label.grid(row = 0, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
                self.draw_1_label.grid(row = 0, column = 2, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
                self.winner_label.grid_forget()

            self.highgoal.reconfigure(self.blue_score.highgoal.get() *pointshigh , self.red_score.highgoal.get() * pointshigh )
            self.midgoal.reconfigure(self.blue_score.midgoal.get()*pointsmid, self.red_score.midgoal.get()*pointsmid)
            self.lowgoal.reconfigure(self.blue_score.lowgoal.get()*pointslow, self.red_score.lowgoal.get()*pointslow)

            red_park = 0
            blue_park = 0
            if(self.blue_score.robot1_park.get() == "high park"):
                blue_park += pointsparkhigh
            elif(self.blue_score.robot1_park.get() == "low park"):
                blue_park += pointsparklow

            if(self.blue_score.robot2_park.get() == "high park"):
                blue_park += pointsparkhigh
            elif(self.blue_score.robot2_park.get() == "low park"):
                blue_park += pointsparklow

            if(self.red_score.robot1_park.get() == "high park"):
                red_park += pointsparkhigh
            elif(self.red_score.robot1_park.get() == "low park"):
                red_park += pointsparklow

            if(self.red_score.robot2_park.get() == "high park"):
                red_park += pointsparkhigh
            elif(self.red_score.robot2_park.get() == "low park"):
                red_park += pointsparklow

            self.parking.reconfigure(blue_park, red_park)
            self.penalty.reconfigure( self.blue_score.penalty.get(), self.red_score.penalty.get())

            self.total.reconfigure(self.blue_score.total_score.get(), self.red_score.total_score.get())


            #display this hell
            self.final_frame.grid(row = 0, column = 0, columnspan = 3,rowspan = 1,  sticky = 'nsew')
        else:
            self.final_frame.grid_forget()
            self.score_shown = False


        #self.test_label = ctk.CTkLabel(self, text = "This is a test")
        #self.test_label.pack(master = self.final_frame)

    def display_final_score(self):

        self.scoring_frame = ctk.CTkFrame(self.final_frame, fg_color = groundcolor, width = self.winfo_width() * 0.7)
        self.scoring_frame.pack(side = 'top', expand = True, fill = tk.BOTH)
        #title with info who won
        self.title_frame = ctk.CTkFrame(self.scoring_frame, fg_color = "black", corner_radius= 0)
        self.title_frame.pack(side = 'top', expand = True, fill = tk.BOTH)
        self.title_frame.columnconfigure(0, weight = 1, uniform = 'a')
        self.title_frame.columnconfigure(1, weight = 2, uniform = 'a')
        self.title_frame.columnconfigure(2, weight = 1, uniform = 'a')

        self.title_lable = ctk.CTkLabel(self.title_frame, text = "Endstand", font = ('Helvetica', 40 * scaling_unit, 'bold'), corner_radius = 0, fg_color = "black")
        self.title_lable.grid(row = 0, column = 1, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        self.winner_label = ctk.CTkLabel(self.title_frame, text = "Gewinner! ", font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, fg_color = "green")
        self.draw_1_label = ctk.CTkLabel(self.title_frame, text = "Unentschieden", font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, fg_color = "grey")
        self.draw_2_label = ctk.CTkLabel(self.title_frame, text = "Unentschieden", font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, fg_color = "grey")
        if(self.blue_score.total_score.get() > self.red_score.total_score.get()):
            self.winner_label.grid(row = 0, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
            self.draw_1_label.grid_forget()
            self.draw_2_label.grid_forget()
        elif(self.blue_score.total_score.get() < self.red_score.total_score.get()):
            self.winner_label.grid(row = 0, column = 2, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
            self.draw_1_label.grid_forget()
            self.draw_2_label.grid_forget()
        else:
            self.draw_2_label.grid(row = 0, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
            self.draw_1_label.grid(row = 0, column = 2, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5 * scaling_unit)
            self.winner_label.grid_forget()

        self.highgoal = self.table_Entry(self.scoring_frame, 0, 0, "Stufe 3", color = "black", colored_tiles = True)
        self.highgoal.pack(side = 'top', expand = True, fill = tk.BOTH)

        self.midgoal = self.table_Entry(self.scoring_frame, 0, 0 , "Stufe 2", color = "black", colored_tiles = True)
        self.midgoal.pack(side = 'top', expand = True, fill = tk.BOTH)

        self.lowgoal = self.table_Entry(self.scoring_frame, 0, 0 , "Stufe 1", color = "black", colored_tiles = True)
        self.lowgoal.pack(side = 'top', expand = True, fill = tk.BOTH)

        self.parking = self.table_Entry(self.scoring_frame, 0, 0 , "Parken", color = "black", colored_tiles = True)
        self.parking.pack(side = 'top', expand = True, fill = tk.BOTH)

        self.penalty = self.table_Entry(self.scoring_frame, 0, 0, "Strafen", color = "black", colored_tiles = True)
        self.penalty.pack(side = 'top', expand = True, fill = tk.BOTH)


        self.total = self.table_Entry(self.scoring_frame, 0, 0 , "Gesamt", color = pinkcolor, colored_tiles = False)
        self.total.pack(side = 'top', expand = True, fill = tk.BOTH)


    #use for in display, e.g. for settings
    class table_Entry(ctk.CTkFrame):
        def __init__(self, master, score_blue, score_red, category, color, colored_tiles):
            super().__init__(master, fg_color = color, corner_radius = 0)

            if(colored_tiles):
                self.blue = ctk.CTkLabel(self, text = score_blue, fg_color = bluecolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 60)
                self.blue.pack(side = 'left', fill = tk.BOTH, expand = False, padx = 5 * scaling_unit, pady = 5 * scaling_unit)

                self.category = ctk.CTkLabel(self, text = category, fg_color = "transparent", font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 0, width = 60)
                self.category.pack(side = 'left', fill = tk.BOTH, expand = True, padx = 5 * scaling_unit, pady = 5 * scaling_unit)

                self.red = ctk.CTkLabel(self, text = score_red, fg_color = redcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15, width = 60)
                self.red.pack(side = 'left', fill = tk.BOTH, expand = False, padx = 5 * scaling_unit, pady = 5 * scaling_unit)
            else:
                self.blue = ctk.CTkLabel(self, text = score_blue, fg_color = color, font = ('Helvetica', 60 * scaling_unit, 'bold'), corner_radius = 15, width = 60)
                self.blue.pack(side = 'left', fill = tk.BOTH, expand = False, padx = 5 * scaling_unit, pady = 5 * scaling_unit)

                self.category = ctk.CTkLabel(self, text = category, fg_color = "transparent", font = ('Helvetica', 60 * scaling_unit, 'bold'), corner_radius = 0, width = 60)
                self.category.pack(side = 'left', fill = tk.BOTH, expand = True, padx = 5 * scaling_unit, pady = 5 * scaling_unit)

                self.red = ctk.CTkLabel(self, text = score_red, fg_color = color, font = ('Helvetica', 60 * scaling_unit, 'bold'), corner_radius = 15, width = 60)
                self.red.pack(side = 'left', fill = tk.BOTH, expand = False, padx = 5 * scaling_unit, pady = 5 * scaling_unit)

        def reconfigure(self, new_blue_score, new_red_score):

            self.blue.configure(text = new_blue_score)
            self.red.configure(text = new_red_score)
class MatchStatusConsole(ctk.CTkFrame):
    def __init__(self, master, blue_score, red_score):
        super().__init__(master, fg_color = 'grey')

        global match_settings

        #define grid
        self.columnconfigure(0, weight = 3, uniform = 'c')
        self.columnconfigure(1, weight = 3, uniform = 'c')
        self.columnconfigure(2, weight = 3, uniform = 'c')


        self.rowconfigure(0, weight = 1, uniform = 'd') #progress bar
        self.rowconfigure(1, weight = 2, uniform = 'd')
        self.rowconfigure(2, weight = 2, uniform = 'd')

        #progress bar
        self.progress = ctk.CTkProgressBar(self, mode = 'determinate', corner_radius = 0)
        self.progress.grid(row = 0, column = 0, columnspan = 3, sticky = 'nsew')

        #points display
        self.pointsFrame = ctk.CTkFrame(self, fg_color = 'black')
        self.pointsFrame.grid(row = 1, column = 1, rowspan = 2, sticky = 'nsew')

        self.pointsFrame.columnconfigure(0, weight = 1, uniform = '1')
        self.pointsFrame.columnconfigure(1, weight = 1, uniform = '1')

        self.pointsFrame.rowconfigure(0,weight = 1 )


        self.points_blue_label = ctk.CTkLabel(self.pointsFrame, textvariable = blue_score.total_score, fg_color = bluecolor, font = ('Helvetica', 60 * scaling_unit_height, 'bold'), )
        self.points_red_label = ctk.CTkLabel(self.pointsFrame, textvariable = red_score.total_score, fg_color = redcolor, font = ('Helvetica', 60 * scaling_unit_height, 'bold'), )

        self.points_blue_label.grid(column = 0, row = 0, sticky = 'nsew')
        self.points_red_label.grid(column = 1, row = 0, sticky = 'nsew')

        #disable the real time score when match is finished
        match_settings.match_stopped.trace_add("write", self.hide_rt_score)

        #for continuously updating progress bar
        match_settings.current_time.trace_add("write", self.update_progress_bar)


        #team names
        name_height = scaling_unit_height * 50
        name_width = scaling_unit_width  * 250
        self.team1_1 = ctk.CTkLabel(self, textvariable = match_settings.teamblue_1_name, fg_color = groundcolor, font = ('Helvetica', 15 * scaling_unit, 'bold'), width = name_width, height = name_height,padx = 5*scaling_unit, pady = 5 * scaling_unit, anchor = 'w')
        self.team1_1.grid(row = 1, column = 0, sticky = 'ew')

        self.team1_2 = ctk.CTkLabel(self, textvariable = match_settings.teamblue_2_name, fg_color = groundcolor, font = ('Helvetica', 15 * scaling_unit, 'bold'), width = name_width, height = name_height,padx = 5*scaling_unit, pady = 10 * scaling_unit, anchor = 'w')
        self.team1_2.grid(row = 2, column = 0, sticky = 'ew')

        self.team2_1 = ctk.CTkLabel(self, textvariable = match_settings.teamred_1_name, fg_color = groundcolor, font = ('Helvetica', 15 * scaling_unit, 'bold'), width = name_width, height = name_height,padx = 5*scaling_unit, pady = 5 * scaling_unit, anchor = 'e')
        self.team2_1.grid(row = 1, column = 2, sticky = 'ew')

        self.team2_2 = ctk.CTkLabel(self, textvariable = match_settings.teamred_2_name, fg_color = groundcolor, font = ('Helvetica', 15 * scaling_unit, 'bold'), width = name_width, height = name_height,padx = 5*scaling_unit, pady = 10 * scaling_unit, anchor = 'e')
        self.team2_2.grid(row = 2, column = 2, sticky = 'ew')

    def update_progress_bar(self, *args):

        current_time_seconds = match_settings.current_time.get()
        self.progress.set(1- float(current_time_seconds) / float(match_settings.total_matchtime))

    def hide_rt_score(self, *args):
            red_score = self.master.red_score.total_score.get()
            blue_score = self.master.blue_score.total_score.get()

            if(match_settings.match_stopped.get()):
                self.points_blue_label.configure( textvariable = '')
                self.points_red_label.configure(textvariable = '')

                self.points_blue_label.configure(text = blue_score)
                self.points_red_label.configure(text = red_score)
                print("RT score disabled")
            else:
                self.points_blue_label.configure(textvariable = self.master.blue_score.total_score)
                self.points_red_label.configure(textvariable = self.master.red_score.total_score)
                print("RT score re-enabled")




class MiddleConsole(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color = groundcolor)
        self.create_widgets()

    def create_widgets(self):

        global match_settings
        #define grid

        self.columnconfigure(0, weight = 1)

        self.rowconfigure(0, weight = 1)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1)


        #refill_timer frame
        self.refill_timer_frame = ctk.CTkFrame(self, fg_color = groundcolor)
        self.refill_timer_frame.pack(fill = tk.X, expand = False)

        self.refill_timer_label = ctk.CTkLabel(self.refill_timer_frame, text = "Nachschub in: ", fg_color = groundcolor, font = ('Helvetica', 25 * scaling_unit, 'bold'))
        self.refill_timer_label.pack(fill = tk.X, expand = True)

        self.refill_timer_time = ctk.CTkLabel(self.refill_timer_frame, text = "0 s", fg_color = groundcolor, font = ('Helvetica', 25 * scaling_unit, 'bold'))
        self.refill_timer_time.pack()

        self.refill_endgame_label = ctk.CTkLabel(self.refill_timer_frame, text = "Finale Phase!", fg_color = "green", font = ('Helvetica', 20 * scaling_unit, 'bold'))
        #not packed here

        #self.refill_progress = ctk.CTkProgressBar(self, mode = 'determinate')
        #self.refill_progress.pack(fill = tk.X, expand = False)

        #timer display
        self.timer = ctk.CTkLabel(self, text = "00:00"  , fg_color = 'black', font = ('Helvetica', 80 * scaling_unit, 'bold'))
        self.timer.pack(fill = tk.BOTH, expand = True)


        #Attach trace to the current_time variable
        match_settings.current_time.trace_add("write", self.update_timer_display)
        match_settings.refill_time.trace_add("write", self.update_refill_timer)
        match_settings.event_trigger.trace_add("write", self.on_change_to_endgame)

    def update_timer_display(self, *args):
        # Get the current time in seconds
        current_time_seconds = int(match_settings.current_time.get())
        # Convert to minutes and seconds
        minutes = current_time_seconds // 60
        seconds = current_time_seconds % 60
        # Format the time as MM:SS
        formatted_time = f"{minutes:02}:{seconds:02}"
        # Update the timer label
        self.timer.configure(text=formatted_time)


    def on_change_to_endgame(self, *args):
        if match_settings.event_trigger.get() == "waiting_endgame":
            self.refill_timer_label.configure(text = "Finale Phase in: ")
            #print("waiting endgame")
        elif match_settings.event_trigger.get() == "endgame":
            self.refill_timer_label.configure(text = "Finale Phase! ")
            self.refill_timer_label.pack_forget()
            self.refill_timer_time.pack_forget()
            self.refill_endgame_label.pack(fill = tk.BOTH, expand = True)
            #print("enddgaaammmemee!")
        elif match_settings.event_trigger.get() == "reset match":
            self.refill_timer_label.configure(text = "Nachschub in ")
            self.refill_timer_label.pack()
            self.refill_timer_time.pack()
            self.refill_endgame_label.pack_forget()
            #print("reset match")
        else:
            self.refill_timer_label.configure(text = "Nachschub in ")
            self.refill_timer_label.pack()
            self.refill_timer_time.pack()
            self.refill_endgame_label.pack_forget()
            #print("normal mode"+ str(match_settings.event_trigger.get()))


    def update_refill_timer(self, *args):

        refill_time_seconds = int(match_settings.refill_time.get())
        formatted_time = f"{refill_time_seconds} s"
        self.refill_timer_time.configure(text=formatted_time)



    def animate_endgame(self):
        pass

class TeamConsole(ctk.CTkFrame):
    def __init__(self, master,color, team):
        super().__init__(master, fg_color = color)
        self.create_widgets(color, team)
        self.init_color = color

    def create_widgets(self, color, team):

        global match_settings
        #create grid
        self.init_color = color
        self.columnconfigure(0, weight = 3, uniform = 1)
        self.columnconfigure(1, weight = 5, uniform = 1)

        self.rowconfigure(0, weight = 2, uniform = 'a')
        self.rowconfigure(1, weight = 2, uniform = 'a')
        self.rowconfigure(2, weight = 2, uniform = 'a')
        self.rowconfigure(3, weight = 3, uniform = 'a')
        #import the image for the goal
        script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
        image_path = os.path.join(script_dir, "./Graphics/GoalZeichnung.png")
        self.resized_image = Image.open(image_path).resize((100, 100))


        self.image_canvas = tk.Canvas(self, background = groundcolor)
        self.image_canvas.grid(row = 0, column = 1, rowspan = 3, sticky = 'nsew', padx = 5 * scaling_unit, pady = 25 * scaling_unit)

         # Bind the configure event to resize the image
        self.image_canvas.bind('<Configure>', self.resize_image)

        #import labels for scores:
        self.highgoal_label = ctk.CTkLabel(self, textvariable = team.highgoal, fg_color = groundcolor, font = ('Helvetica', 30 * scaling_unit, 'bold'), corner_radius = 15)
        self.midgoal_label = ctk.CTkLabel(self,textvariable = team.midgoal, fg_color = groundcolor, font = ('Helvetica', 30 * scaling_unit, 'bold'), corner_radius = 15)
        self.lowgoal_label = ctk.CTkLabel(self, textvariable = team.lowgoal, fg_color = groundcolor, font = ('Helvetica', 30 * scaling_unit, 'bold'), corner_radius = 15)

        self.highgoal_label.grid(row = 0, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 25 * scaling_unit)
        self.midgoal_label.grid(row = 1, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 25 * scaling_unit)
        self.lowgoal_label.grid(row = 2, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 25 * scaling_unit)

        class parking_display(ctk.CTkFrame):
            def __init__(self, master, variable = None):
                super().__init__(master, border_color = "black", border_width= 5, fg_color = groundcolor)

                self.tkvariable = variable

                self.rowconfigure((0,1,2), weight = 1, uniform = 'f')
                self.columnconfigure(0, weight = 1, uniform = 'g')
                self.parkingindicator = ctk.CTkLabel(self, text = " - Parkieren -", bg_color= "transparent", fg_color = groundcolor, font = ('Helvetica', 30 * scaling_unit, 'bold'), corner_radius = 15)
                self.parkingindicator.grid(row = 0, column = 0, sticky = 'nsew', padx = 5 * scaling_unit, pady = 5* scaling_unit)

                self.parkingindicator_high = ctk.CTkLabel(self, text = "H", bg_color= "transparent", fg_color = transparent_grey, font = ('Helvetica', 30 * scaling_unit), corner_radius = 8)
                self.parkingindicator_high.grid(row = 1, column = 0, sticky = 'nsew', padx = 15 * scaling_unit, pady = 7 * scaling_unit)

                self.parkingindicator_low = ctk.CTkLabel(self, text = "T", bg_color= "transparent", fg_color = transparent_grey, font = ('Helvetica', 30 * scaling_unit), corner_radius = 8)
                self.parkingindicator_low.grid(row = 2, column = 0, sticky = 'nsew', padx = 15 * scaling_unit, pady = 7 * scaling_unit)

                # Trace the variable to call update_parking whenever it changes
                if variable is not None:
                    variable.trace_add("write", lambda *args: self.update_parking())

            def update_parking(self):
                if(self.tkvariable.get() == "not parked"):
                    self.parkingindicator_low.configure(fg_color = transparent_grey)
                    self.parkingindicator_high.configure(fg_color = transparent_grey)
                elif(self.tkvariable.get() == "low park"):
                    self.parkingindicator_low.configure(fg_color = greencolor)
                    self.parkingindicator_high.configure(fg_color = transparent_grey)
                elif(self.tkvariable.get() == "high park"):
                    self.parkingindicator_low.configure(fg_color = transparent_grey)
                    self.parkingindicator_high.configure(fg_color = greencolor)
                else:
                    print("Error occured")

        bottom_frame = tk.Frame(self,background = self.init_color)
        bottom_frame.grid(row = 3, column = 0, columnspan = 2, sticky = 'nsew')

        bottom_frame.grid_columnconfigure((1,2), weight = 1, uniform = 'h')
        bottom_frame.grid_rowconfigure(1, weight = 1, uniform = 'h')

        self.park1 = parking_display(bottom_frame, team.robot1_park).grid(row = 0, column = 1, sticky = 'nsew', padx = 30 * scaling_unit)
        self.park2 = parking_display(bottom_frame,team.robot2_park).grid(row = 0, column = 2, sticky = 'nsew', padx = 30 * scaling_unit)

        #self.penalty_frame = ctk.CTkLabel(bottom_frame, text = "0", fg_color = groundcolor, font = ('Helvetica', 20 * scaling_unit, 'bold'), corner_radius = 15)


    def resize_image(self, event):
        # Get the new size of the frame
        new_width = int(event.width)
        new_height = event.height

        # Resize the image to fit the frame
        resized_image = self.resized_image.resize((new_width, new_height))
        self.image_tk = ImageTk.PhotoImage(resized_image)

        # Update the label's image
        self.image_canvas.create_image(0, 0, image=self.image_tk, anchor='nw')
