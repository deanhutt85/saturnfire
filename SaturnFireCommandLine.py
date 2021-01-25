import serial
import time
import logging
import serial.rs485
import serial.tools.list_ports
import multiprocessing
from Queue import Queue
import sys


# Author: Dean Hutt


START_OF_HEADER = bytes(0x01)
START_OF_TEXT = bytes(0x02)
END_OF_TEXT = bytes(0x03)
END_OF_TRANSMITION = bytes(0x04)


#serialport = '/dev/ttyUSB0'
serialport = str(sys.argv[1])
serialbaudrate = 9600
polltime = 200 # In ms
spincount = 1
firetimeout = 60
logfile = "HuxleyLogfile.log"

#logging.basicConfig(filename=logfile, filemode='a', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')
logging.basicConfig(filename=logfile, level=logging.INFO, filemode='a', format="%(asctime)s:%(levelname)s: %(message)s")
logging.getLogger().addHandler(logging.StreamHandler())

class FireWheel:
    def __init__(self):
        print(32 * "*"  + "\nSTARTING SATURN FIRE APPLICATION\n" + 32 * "*")
        print("FIRE TIMEOUT SET TO " + str(firetimeout))
        self.last_time = int(round(time.time() * 1000))
        self.last_fire_time = int(round(time.time() * 1000))
        self.Process = multiprocessing.Process(target=self.send_command)
        self.thread_queue = Queue()
        self.error_flag = 0

        # Opening Serial
        print("Opening Serial Port")
        try:
            self.ser = serial.rs485.RS485(port=serialport, baudrate=serialbaudrate, stopbits=serial.STOPBITS_ONE, parity = serial.PARITY_NONE, bytesize=serial.EIGHTBITS, timeout=1, rtscts=0)
            self.ser.rs485_mode = serial.rs485.RS485Settings(False, True)
            print("Serial Port Opened on port " + str(serialport))
        except serial.SerialException as e:
            print("Something Went Wrong! \n" + str(e))
            print("EXITING!")
            quit()


    def serial_ports():
        return serial.tools.list_ports.comports()

    def stop_wheel(self):
        #print(self.Process.is_alive())
        self.Process.terminate()
        #print(self.Process.is_alive())
        print("Wheel Process Stopped")
        self.Process = multiprocessing.Process(target=self.send_command)

    def close_serial(self):
        print("Closing Serial Port")
        # self.wheelrunning = False
        self.ser.close()
        print("Serial Port Closed")

    def send_command(self):
        print("Starting")
        if firetimeout < 20:
            print "Enter a timeout value over 20"
        else:
            while True:
                sr1hexcommand = bytearray.fromhex("01 30 32 02 53 52 31 03 7e 04")
                sr2hexcommand = bytearray.fromhex("01 30 32 02 53 52 32 03 7f 04")

                print("Poll Time = " + str(polltime))
                print("Fire Timeout = " + str(firetimeout))
                # print("LastTime = " + str(self.last_time))
                try:
                    while True:
                        if int(round(time.time() * 1000)) > self.last_time + polltime:
                            self.ser.write(sr2hexcommand)
                            self.readData()
                            self.last_time = int(round(time.time() * 1000))
                            if int(round(time.time() * 1000)) > self.last_fire_time + (firetimeout * 1000):
                                print("Sending Fire Command")
                                self.send_fire()
                                self.last_fire_time = int(round(time.time() * 1000))
                                print(int(round(time.time() * 1000)) - self.last_fire_time)
                            else:
                                continue
                except serial.SerialException as e:
                    print("Something bad happened" + str(e))
                    self.ser.close()

    def send_fire(self):
        print("Firing")
        # TODO: Validate hex command here
        firehexcommand = bytearray.fromhex("01 30 34 02 52 43 30 33 03 62 04")
        self.ser.write(firehexcommand)
        print("***\n" + str(firehexcommand) + "\n***")

    def readData(self):
        #sr3hexcommand = bytearray.fromhex("01 30 34 02 53 52 33 03 82 04")
        buffer = ""
        while True:
            oneByte = self.ser.read(1)
            if oneByte == b"\4":
                print(buffer)
                logging.info(buffer)
                self.error_flag = buffer[48]
                print(self.error_flag)
                if self.error_flag == "1":
                    print("Wheel Error!!!")
                    self.read_error()
                else:
                    return buffer
            else:
                buffer += oneByte.decode("ascii")


    def read_error(self):
        print("Reading Error")
        sr3hexcommand = bytearray.fromhex("01 30 34 02 53 52 33 03 42 04")
        self.ser.write(sr3hexcommand)
        errorbuffer = ""
        while True:
            oneByte = self.ser.read(1)
            if oneByte == b"\4":
                print(errorbuffer)
                logging.warning(errorbuffer[5:12])
                print("*** WHEEL ERROR ***\n" + errorbuffer[5:12])
                # if self.Process.is_alive():
                #     self.Process.terminate()
                # else:
                #     pass
                # self.text.insert(END, errorbuffer[5:12])
                return errorbuffer
            else:
                errorbuffer += oneByte.decode("ascii")

    def reset_error(self):
        pass

    def checksum_calc(self, text):
        csbytes = bytearray(text.encode())
        checksum = int(0)
        # checksum = hex(sum(sr2hexcommand) & 0x3f | 0x40)
        # print(checksum)

    # def message_box(self, openerror):
    #     messagebox.showerror("ERROR!", openerror)


app = FireWheel()
# root.mainloop()
app.send_command()
