import serial
import time
import logging
import serial.rs485
from SaturnFireGUI import *

START_OF_HEADER = bytes(0x01)
START_OF_TEXT = bytes(0x02)
END_OF_TEXT = bytes(0x03)
END_OF_TRANSMITION = bytes(0x04)


serialport = '/dev/ttyUSB0'
serialbaudrate = 9600
polltime = 200 # In ms
spincount = 1
logfile = "HuxleyLogfile.log"

logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO)


class FireWheel:
    def __init__(self):
        self.last_time = int(round(time.time() * 1000))
        self.ser = serial.rs485.RS485(port=serialport, baudrate=serialbaudrate, stopbits=serial.STOPBITS_ONE, parity = serial.PARITY_NONE, bytesize=serial.EIGHTBITS, timeout=1, rtscts=0)
        self.ser.rs485_mode = serial.rs485.RS485Settings(False, True)

    def send_command(self):
        print("Starting")
        while True:
            sr1hexcommand = bytearray.fromhex("01 30 32 02 53 52 31 03 7e 04")
            sr2hexcommand = bytearray.fromhex("01 30 32 02 53 52 32 03 7f 04")
            sr3hexcommand = bytearray.fromhex("01 30 32 02 53 52 33 03 80 04")

            print("FireTimeout = " + str(polltime))
            print("LastTime = " + str(self.last_time))
            try:
                while True:
                    # self.start_log()
                    if int(round(time.time() * 1000)) > self.last_time + (polltime):
                        self.ser.write(sr1hexcommand)
                        self.readData()
                        self.ser.write(sr2hexcommand)
                        self.readData()

                        self.last_time = int(round(time.time() * 1000))
            except serial.SerialException as e:
                print("Something bad happened" + str(e))


    def readData(self):
        buffer = ""
        while True:
            oneByte = self.ser.read(1)
            if oneByte == b"\4":
                print(buffer)
                logging.info(buffer)
                return buffer
            else:
                buffer += oneByte.decode("ascii")



    def checksum_calc(self, text):
        csbytes = bytearray(text.encode())
        checksum = int(0)
        # checksum = hex(sum(sr2hexcommand) & 0x3f | 0x40)
        # print(checksum)


WheelFireGUI()


#startapp = FireWheel()
#startapp.send_command()


