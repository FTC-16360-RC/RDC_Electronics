import serial
import json
import keyboard


ser = serial.Serial('COM7', 9600)


def send_serial(message):
    global ser
    
    #print(".", end =" ")
    print(f"sending message {message}")
    ser.write(message.encode('utf-8'))


def on_key_press(event):
    key = event.name
    #print(f"keyboard event {key}")

    if key == 'q':
        #print("pressing: q")
        send_serial("RED_TOP_OPEN")
        pressed = True
        return

    if key == 'a':
        #print("pressing: a")
        send_serial("RED_MID_OPEN")
        pressed = True
        return

    if key == 'y':
        #print("pressing: y")
        send_serial("RED_LOW_OPEN")
        pressed = True
        return


    if key == 'w':
        #print("pressing: w")
        send_serial("RED_TOP_CLOSE")
        pressed = True
        return

    if key == 's':
        #print("pressing: s")
        send_serial("RED_MID_CLOSE")
        pressed = True
        return

    if key == 'x':
        #print("pressing: x")
        send_serial("RED_LOW_CLOSE")
        pressed = True
        return
    

    if key == 'o':
        #print("pressing: o")
        send_serial("BLU_TOP_OPEN")
        pressed = True
        return

    if key == 'k':
        #print("pressing: k")
        send_serial("BLU_MID_OPEN")
        pressed = True
        return

    if key == 'n':
        #print("pressing: n")
        send_serial("BLU_LOW_OPEN")
        pressed = True
        return
    

    if key == 'p':
        #print("pressing: p")
        send_serial("BLU_TOP_CLOSE")
        pressed = True
        return

    if key == 'l':
        #print("pressing: l")
        send_serial("BLU_MID_CLOSE")
        pressed = True
        return

    if key == 'm':
        #print("pressing: m")
        send_serial("BLU_LOW_CLOSE")
        pressed = True
        return
    
    pressed = False


print("press ctr + c or 'z' to exit...")
print("RED: ")
print("Q - open top, W - close top")
print("A - open mid, S - close mid")
print("Y - open low, X - close low")

print("BLUE: ")
print("O - open top, P - close top")
print("K - open mid, L - close mid")
print("N - open low, M - close low")

pressed = False

keyboard.on_press(on_key_press)

keyboard.wait('b')
print("Quitting...")