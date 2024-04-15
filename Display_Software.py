# webhook_receiver.py
from flask import Flask, request, jsonify
import threading
import time
import tkinter as tk
import json


app = Flask(__name__)

time_zero = 0

webhook_port = 5001

state = {"balls" : 
            {"29" : 0, 
             "91" : 0, 
             "92" : 0, 
             "93" : 0, 
             "94" : 0, 
             "95" : 0},
        "time" : 0,         #time in ms
             }

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

    def update_time(self, time_zero):
        t_decimal = int(time.time()*10) - int(time.time()) * 10
        t_second = int(time.time()) - time_zero

        if t_second < 0:
            t_decimal = 9 - t_decimal
        
        if t_second >= 40:
            t_second = 40
            t_decimal = 0

        t = f"{t_second}.{t_decimal} / 40"
        self.time_label.config(text = t)
        self.root.update()

            
    def update(self):
        self.root.update_idletasks()
        self.root.update()


@app.route('/webhook_match_to_display', methods=['POST'])
def _receiver():
    global time_zero
    global state

    data = request.json  # Assuming the data is sent as JSON

    if "init" in data:
        time_zero = data["init"]
        print(f"start time DING:{time_zero}")
    
    if "balls" in data:
        state = data

    print("Received Webhook Data:", data)
    return jsonify({"status": "success"})


def permanent_loop():
    global time_zero
    global state

    window = Window(state)

    endgame = False
    program_running = True
    match_running = False

    print("Waiting for start time...")
    while time_zero == 0:    #wait until time_zero is recieved
        window.change_state("Waiting for start time...")    

    window.change_state("match about to start")

    last_second = 0

    while program_running:
        window.update()
        window.update_time(time_zero)
        window.update_state(state)

        if time.time() >= time_zero and not match_running:
            window.change_state("match running")
            match_running = True

        if int(time.time()) != last_second:    #time display (console)
            last_second = int(time.time())
            t = int(time.time() - time_zero)
            print(f"time display software: {t}")

        if time.time() - time_zero >= 30 and not endgame:
            endgame = True
            print("ENDGAME!!!!")
            window.change_state("endgame")

        if time.time() - time_zero >= 40:
            window.update_time(time_zero)
            print("END!!!")
            window.change_state("end")
            program_running = False

    while True:
        window.update()


def gui_loop():
    return
    window = Window("scope2")
    window.root.mainloop()


def load_settings():
    global webhook_port

    f = open("settings.json", "r")
    settings = json.load(f)

    webhook_port = settings["webhook port"]


if __name__ == '__main__':
    
    load_settings()
    
    loop_thread = threading.Thread(target=permanent_loop)
    loop_thread.start()

    gui_thread = threading.Thread(target=gui_loop)
    gui_thread.start()

    app.run(debug=False, host='0.0.0.0', port=webhook_port)

    while True:
        pass