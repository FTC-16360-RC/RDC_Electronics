import serial
import keyboard


SERIAL_PORT = "COM7"
SERIAL_BAUDRATE = 9600
q_pressed = False
w_pressed = False

def send_serial_command(command):
    global ser

    if not ser.is_open:
        print(f"esp not connected. Command: {command}")
        return
    print(f"Writing serial command: {command}")
    ser.write(command.encode('utf-8'))
    ser.flush()


if __name__ == "__main__":
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE)

    while True:
        if keyboard.is_pressed('q') and not q_pressed:
            print("sent RED_LOW_OPEN")
            send_serial_command("RED_LOW_OPEN\n")
            q_pressed = True
        if not keyboard.is_pressed('q') and q_pressed:
            q_pressed = False

        if keyboard.is_pressed('w') and not w_pressed:
            print("sent RED_LOW_CLOSE")
            send_serial_command("RED_LOW_CLOSE\n")
            w_pressed = True
        if not keyboard.is_pressed('w') and w_pressed:
            w_pressed = False


