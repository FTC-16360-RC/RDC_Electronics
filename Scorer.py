import pynput.keyboard as pkeyboard


class Scorer:    

    #category: "penalty points" / "balls" 
    #[{"category": ...., "position" : ..., "change" : ...}, {...}, ...]
    events = [] 
    listener = ''

    some_key_pressed = False
    pressed_key = ''

    def release_handler(self, key):
        global some_key_pressed
        global pressed_key
        if key == self.pressed_key:
            self.some_key_pressed = False   
            #print(f"released {self.pressed_key}")
        

    def press_handler(self, key):
        if self.some_key_pressed:
            return
        self.some_key_pressed = True
        self.pressed_key = key

        category = ""
        position = ""
        change = 0

        if key.char == 'q':
            category = "balls"
            position = "blu_top"
            change = 1
        
        if key.char == 'w':
            category = "balls"
            position = "blu_top"
            change = -1

        if key.char == 'a':
            category = "balls"
            position = "blu_mid"
            change = 1

        if key.char == 's':
            category = "balls"
            position = "blu_mid"
            change = -1

        if key.char == 'y':
            category = "balls"
            position = "blu_low"
            change = 1

        if key.char == 'x':
            category = "balls"
            position = "blu_low"
            change = -1


        if key.char == 'e':
            category = "balls"
            position = "red_top"
            change = 1
        
        if key.char == 'r':
            category = "balls"
            position = "red_top"
            change = -1

        if key.char == 'd':
            category = "balls"
            position = "red_mid"
            change = 1

        if key.char == 'f':
            category = "balls"
            position = "red_mid"
            change = -1

        if key.char == 'c':
            category = "balls"
            position = "red_low"
            change = 1

        if key.char == 'v':
            category = "balls"
            position = "red_low"
            change = -1


        if key.char == 't':
            category = "penalty points"
            position = "blu"
            change = 25

        if key.char == 'z':
            category = "penalty points"
            position = "blu"
            change = -25

        if key.char == 'g':
            category = "penalty points"
            position = "blu"
            change = 10

        if key.char == 'h':
            category = "penalty points"
            position = "blu"
            change = -10


        if key.char == 'u':
            category = "penalty points"
            position = "red"
            change = 25

        if key.char == 'i':
            category = "penalty points"
            position = "red"
            change = -25

        if key.char == 'j':
            category = "penalty points"
            position = "red"
            change = 10

        if key.char == 'k':
            category = "penalty points"
            position = "red"
            change = -10


        if position != '':
            self.events.append({"category": category, "position" : position, "change" : change})
            #print(f"pressed {key.char}")

    def __init__(self):
        global listener
        listener = pkeyboard.Listener(
                on_press=self.press_handler,
                on_release=self.release_handler)
        listener.start()


    def update(self):
        return
    
    def pop_top(self):
        if len(self.events) != 0:
            return self.events.pop(0)
        else:
            return "empty"