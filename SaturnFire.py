import serial
import time
import logging
import serial.rs485
import serial.tools.list_ports
import threading
import multiprocessing
from Queue import Queue
from tkinter import *
from tkinter import messagebox
from tkinter import Toplevel

root = Tk()

START_OF_HEADER = bytes(0x01)
START_OF_TEXT = bytes(0x02)
END_OF_TEXT = bytes(0x03)
END_OF_TRANSMITION = bytes(0x04)


# serialport = '/dev/ttyUSB0'
serialport = StringVar()
serialbaudrate = 9600
polltime = 200 # In ms
spincount = 1
firetimeout = IntVar()
firetimeout.set(30)
portstatus = StringVar()
portstatus.set("Closed")
logfile = "HuxleyLogfile.log"


logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')



class FireWheel:
    def __init__(self, root):
        self.last_time = int(round(time.time() * 1000))
        self.last_fire_time = int(round(time.time() * 1000))
        self.Process = multiprocessing.Process(target=self.send_command)
        self.thread_queue = Queue()

        print("Launching GUI")
        root.title("Serial Tests")
        self.port = Entry(root, textvariable=serialport)
        self.port.grid(row=0, column=1)
        self.seriallabel = Label(root, text="Serial Port: ")
        self.seriallabel.grid(row=0, column=0)
        self.timeoutlabel = Label(root, text="Fire Timeout: ")
        self.timeoutlabel.grid(row=1, column=0)
        self.timeoutentry = Entry(root, textvariable=firetimeout)
        self.timeoutentry.grid(row=1, column=1)
        self.openbutton = Button(root, text="Open Port", command=lambda: self.open_serial())
        self.openbutton.grid(row=3, column=0)
        self.closebutton = Button(root, text="Close Port", command=lambda: self.close_serial())
        self.closebutton.grid(row=3, column=1)
        self.opencclose = Label(root, textvariable=portstatus)
        self.opencclose.grid(row=0, column=2)
        self.runwheel = Button(root, text="Start Wheel", command=lambda: self.Process.start())
        self.runwheel.grid(row=5, column=0)
        self.stopwheel = Button(root, text="Stop Wheel", command=lambda: self.stop_wheel())
        self.stopwheel.grid(row=5, column=1)
        self.start_log()

        # TODO: Write the logs in to text box, assuming it's not going to block. Toplevel? Thread?


    def start_log(self):
        logwindow = Toplevel()
        self.scrollbar = Scrollbar(logwindow)
        self.scrollbar.grid(row=0, column=5, sticky=(N, S, E))
        self.text = Text(logwindow, yscrollcommand=self.scrollbar.set)
        self.text.grid(row=0, column=4, sticky=(N, S, E, W))
        self.scrollbar.config(command=self.text.yview)
        self.text.insert(END, "ThisIsSOmething \n")


    def open_serial(self):
        print("Opening Serial Port")
        try:
            self.ser = serial.rs485.RS485(port=serialport.get(), baudrate=serialbaudrate, stopbits=serial.STOPBITS_ONE, parity = serial.PARITY_NONE, bytesize=serial.EIGHTBITS, timeout=1, rtscts=0)
            self.ser.rs485_mode = serial.rs485.RS485Settings(False, True)
            print("Serial Port Opened on port " + str(serialport.get()))
            portstatus.set("Opened")
            self.text.insert(END, "Port Opened")
        except serial.SerialException as e:
            print("Something Went Wrong! \n" + str(e))
            self.message_box(e)

    def serial_ports():
        return serial.tools.list_ports.comports()

    def read_serial_test(self, pollmessage):
        incoming = pollmessage
        self.text.insert(END, incoming)
        # qpolls = self.thread_queue.get()
        # self.text.insert(END,qpolls)
        # print(self.thread_queue.get())
        self.text.insert(END,"Hello")
        print("MESSAGE" + pollmessage)

        # print(pollmessage)

    def stop_wheel(self):
        print(self.Process.is_alive())
        self.Process.terminate()
        print(self.Process.is_alive())
        print("Wheel Process Stopped")
        self.Process = multiprocessing.Process(target=self.send_command)

    def close_serial(self):
        print("Closing Serial Port")
        # self.wheelrunning = False
        self.ser.close()
        portstatus.set("Closed")
        print("Serial Port Closed")

    def send_command(self):
        self.read_serial_test("STARTING WHEEL POLLING")
        print(portstatus.get())
        if portstatus.get() == "Closed":
            self.message_box("PLEASE OPEN SERIAL PORT FIRST")
        else:
            print("Starting")
        if firetimeout.get() < 20:
            print "Enter a timeout value over 20"
            self.message_box("Please enter a fire timeout above 20")
        else:
            while True:
                sr1hexcommand = bytearray.fromhex("01 30 32 02 53 52 31 03 7e 04")
                sr2hexcommand = bytearray.fromhex("01 30 32 02 53 52 32 03 7f 04")
                sr3hexcommand = bytearray.fromhex("01 30 34 02 53 52 33 03 82 04")
                print("Poll Time = " + str(polltime))
                print("Fire Timeout = " + str(firetimeout.get()))
                print("LastTime = " + str(self.last_time))
                try:
                    while True:

                        if int(round(time.time() * 1000)) > self.last_time + (polltime):
                            self.ser.write(sr1hexcommand)
                            #self.readData()
                            self.ser.write(sr2hexcommand)
                            self.readData()
                            self.last_time = int(round(time.time() * 1000))
                            if int(round(time.time() * 1000)) > self.last_fire_time + (firetimeout.get() * 1000):
                                print("Sending Fire Command")
                                self.last_fire_time = int(round(time.time() * 1000))
                            else:
                                continue
                except serial.SerialException as e:
                    print("Something bad happened" + str(e))
                    self.message_box(e)
                    self.ser.close()

    def send_fire(self):
        print("Firing")
        self.read_serial_test("Sent Fire Command")
        self.text.insert("Fire COmmend Sent")
        # TODO: Validate hex command here
        firehexcommand = bytearray.fromhex("01 30 34 02 52 43 30 03 7f 04")
        self.ser.write(firehexcommand)
        self.readData()

    def readData(self):
        buffer = ""
        while True:
            oneByte = self.ser.read(1)
            if oneByte == b"\4":
                print(buffer)
                logging.info(buffer)
                self.read_serial_test(buffer)
                return buffer
            else:
                buffer += oneByte.decode("ascii")



    def checksum_calc(self, text):
        csbytes = bytearray(text.encode())
        checksum = int(0)
        # checksum = hex(sum(sr2hexcommand) & 0x3f | 0x40)
        # print(checksum)

    def message_box(self, openerror):
        messagebox.showerror("ERROR!", openerror)



app = FireWheel(root)
root.mainloop()

#startapp = FireWheel()
#startapp.send_command()


