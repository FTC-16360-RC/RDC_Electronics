import keyboard


class Scorer:    

    events = [] #[{"position" : ..., "change" : ...}, {...}, ...]

    some_key_pressed = False

    def release_handler(event):
        global some_key_pressed
        some_key_pressed = False

    def press_handler(event):
        global some_key_pressed
        if some_key_pressed:
            return
        some_key_pressed = True

        key = event.name
        position = ""
        change = 0

        if key == 'q':
            position = "blu_top"
            change = 1
        
        if key == 'w':
            position = "blu_top"
            change = -1

        if key == 'a':
            position = "blu_mid"
            change = 1

        if key == 's':
            position = "blu_mid"
            change = -1

        if key == 'y':
            position = "blu_low"
            change = 1

        if key == 'x':
            position = "blu_low"
            change = -1


        if key == 'o':
            position = "red_top"
            change = 1
        
        if key == 'p':
            position = "red_top"
            change = -1

        if key == 'k':
            position = "red_mid"
            change = 1

        if key == 'l':
            position = "red_mid"
            change = -1

        if key == 'n':
            position = "red_low"
            change = 1

        if key == 'm':
            position = "red_low"
            change = -1


        events.append({"position" : position, "change" : change})

    def __init__:
        keyboard.on_press(press_handler)
        keyboard.on_release(release_handler)
        keyboard.wait()
        
    def update():
        return
    
    def pop_top():
        return events.pop(0)