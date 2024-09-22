import tkinter as tk

#this is the class for all the match settings and tkinter variables that are imported everywhere
#singleton class to store all the settings that can be set in the controller and displayed in the display

       #set this here manually

#set this also in TeamDisplay.py !!
pointslow = 5
pointsmid = 7
pointshigh = 10
pointsparkhigh = 15
pointsparklow = 6
small_penalty = -15
big_penalty = -30

class MatchSettings:

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MatchSettings, cls).__new__(cls)
            cls._instance.init()
        return cls._instance

    def init(self):

 

        #all the settings that can be changed for the match, times are at which time this happens
        self.total_matchtime = 180 + 5
        self.endgame_duration = 30
        self.firstball_drop = self.total_matchtime - 60 - 5
        self.secondball_drop = self.total_matchtime - 90 - 5
        self.thirdball_drop = self.total_matchtime - 120 - 5

        self.event_trigger = tk.StringVar(value = "nothing")
        self.match_stopped = tk.BooleanVar(value = False)
        self.show_confirm = tk.BooleanVar(value = False)

        self.current_time = tk.DoubleVar(value = self.total_matchtime)
        self.refill_time = tk.DoubleVar(value = self.firstball_drop - self.total_matchtime)

        self.teamblue_1_name = tk.StringVar(value ='b1')
        self.teamblue_2_name = tk.StringVar(value = 'b2')
        self.teamred_1_name = tk.StringVar(value = 'r1')
        self.teamred_2_name = tk.StringVar(value = 'r2')
    
    #easy match reset for the next match
    def reset_matchstate(self):

        self.current_time.set(value = self.total_matchtime)
        self.refill_time.set(value =  self.total_matchtime  - self.firstball_drop)
        self.event_trigger.set(value = "reset match")
        self.match_stopped.set(True)
        self.show_confirm.set(False)
    
class TeamScores:

    def __init__(self):

        self.highgoal = tk.IntVar(value = 0)
        self.midgoal = tk.IntVar(value = 0)
        self.lowgoal = tk.IntVar(value = 0)
        self.robot1_park = tk.StringVar(value = "not parked")
        self.robot2_park = tk.StringVar(value = "not parked")
        self.penalty = tk.IntVar(value = 0)

        self.total_score = tk.IntVar(value = 0)

        # Trace changes to individual variables to update the total score live
        self.highgoal.trace_add("write", self.update_total_score)
        self.midgoal.trace_add("write", self.update_total_score)
        self.lowgoal.trace_add("write", self.update_total_score)
        self.robot1_park.trace_add("write", self.update_total_score)
        self.robot2_park.trace_add("write", self.update_total_score)
        self.penalty.trace_add("write", self.update_total_score)



    def reset_team_score(self):


        self.highgoal.set(0)
        self.midgoal.set(0)
        self.lowgoal.set(0)
        self.robot1_park.set(value = "not parked")
        self.robot2_park.set(value = "not parked")
        self.penalty.set(0)       

    def update_total_score(self, *args):
        total = (self.highgoal.get()*pointshigh +
                    self.midgoal.get()*pointsmid +
                    self.lowgoal.get()*pointslow)
        
        if(self.robot1_park.get() == "high park"):
            total += pointsparkhigh
        elif(self.robot1_park.get() == "low park"):
            total += pointsparklow

        if(self.robot2_park.get() == "high park"):
            total += pointsparkhigh
        elif(self.robot2_park.get() == "low park"):
            total += pointsparklow

        total += self.penalty.get()

        self.total_score.set(total)
        


    def increment_score(self, variable):
        variable.set( variable.get() + 1)
        print("incremented score")

    def decrement_score(self,variable):
        variable.set(variable.get() - 1)
        print("decremented score")

    def small_penalty(self, variable, add = True):

        if(add):
            print("added small penalty")
            variable.set(variable.get() + small_penalty)
        else:
            print("subtracted small penalty")
            variable.set(variable.get() - small_penalty)

    def big_penalty(self, variable, add = True):

        if(add):
            print("added big penalty")
            variable.set(variable.get() + big_penalty)
        else:
            print("subtracted big penalty")
            variable.set(variable.get() - big_penalty)
