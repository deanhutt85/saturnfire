import serial
import time
import logging
import serial.rs485
import serial.tools.list_ports
from tkinter import *
from tkinter import messagebox

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

logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO)



class FireWheel:
    def __init__(self, root):
        self.last_time = int(round(time.time() * 1000))
        self.last_fire_time = int(round(time.time() * 1000))
        # self.ser = serial.rs485.RS485(port=serialport, baudrate=serialbaudrate, stopbits=serial.STOPBITS_ONE, parity = serial.PARITY_NONE, bytesize=serial.EIGHTBITS, timeout=1, rtscts=0)
        # self.ser.rs485_mode = serial.rs485.RS485Settings(False, True)

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
        self.runwheel = Button(root, text="Start Wheel", command=lambda: self.send_command())
        self.runwheel.grid(row=5, column=0)
        self.stopwheel = Button(root, text="Stop Wheel", command=lambda: self.close_serial())
        self.stopwheel.grid(row=5, column=1)
        # TODO: Write the logs in to text box, assuming it's not going to block. Toplevel? Thread?
        self.scrollbar = Scrollbar(root)
        self.scrollbar.grid(row=0, column=5, sticky=(N, S, E))
        self.text = Text(root, yscrollcommand=self.scrollbar.set)
        self.text.grid(row=0, column=4, sticky=(N, S, E, W))
        self.scrollbar.config(command=self.text.yview)

    def open_serial(self):
        print("Opening Serial Port")
        try:
            self.ser = serial.rs485.RS485(port=serialport.get(), baudrate=serialbaudrate, stopbits=serial.STOPBITS_ONE, parity = serial.PARITY_NONE, bytesize=serial.EIGHTBITS, timeout=1, rtscts=0)
            self.ser.rs485_mode = serial.rs485.RS485Settings(False, True)
            print("Serial Port Opened on port " + str(serialport.get()))
            portstatus.set("Opened")
        except serial.SerialException as e:
            print("Something Went Wrong! \n" + str(e))
            self.message_box(e)

    def serial_ports():
        return serial.tools.list_ports.comports()

    def close_serial(self):
        print("Closing Serial Port")
        self.ser.close()
        portstatus.set("Closed")
        print("Serial Port Closed")

    def send_command(self): # TODO: Check that this does not block the gui. Threads?
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
                            if int(round(time.time() * 1000)) > self.last_fire_time + (firetimeout.get()):
                                print("Sending Fire Command")
                            else:
                                continue
                except serial.SerialException as e:
                    print("Something bad happened" + str(e))
                    self.message_box(e)
                    self.ser.close()

    def send_fire(self):
        print("Firing")
        # TODO: Fix hex command here
        firehexcommand = bytearray.fromhex("01 30 32 02 53 52 31 03 7e 04")
        self.ser.write(firehexcommand)
        self.readData()

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

    def message_box(self, openerror):
        messagebox.showerror("ERROR!", openerror)


app = FireWheel(root)
root.mainloop()

#startapp = FireWheel()
#startapp.send_command()


