import serial

def read_serial(port, baudrate):
    """
    Reads data from the specified serial port and prints it.
    
    Parameters:
        port (str): The name of the serial port (e.g., 'COM6').
        baudrate (int): The baud rate for serial communication.
    """
    try:
        ser = serial.Serial(port, baudrate)
        print(f"Reading from serial port {port} at {baudrate} baud rate...")
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('latin1').strip()
                print("Received:", data)
    except serial.SerialException as e:
        print("Serial exception:", e)
    finally:
        if ser.is_open:
            ser.close()

if __name__ == "__main__":
    read_serial('COM6', 9600)