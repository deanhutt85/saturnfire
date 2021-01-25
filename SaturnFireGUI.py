import serial
import serial.rs485
import serial.tools.list_ports

serialport = "/dev/ttyUSB0"
serialbaudrate = 9600


class Thing():
    def __init__(self):
        print("Welcome")
        self.ser = serial.rs485.RS485(port=serialport, baudrate=serialbaudrate, stopbits=serial.STOPBITS_ONE, parity=serial.PARITY_NONE, bytesize=serial.EIGHTBITS, timeout=1, rtscts=0)
        self.ser.rs485_mode = serial.rs485.RS485Settings(False, True)

    def run(self):
        sr1hexcommand = bytearray.fromhex("01 30 32 02 53 52 31 03 7e 04")
        sr2hexcommand = bytearray.fromhex("01 30 32 02 53 52 32 03 7f 04")
        sr3hexcommand = bytearray.fromhex("01 30 34 02 53 52 33 03 42 04")

        print("Serial Port Opened on port " + str(serialport))
        self.ser.write(sr3hexcommand)
        print("Sent Command" + str(sr3hexcommand))
        self.read()
        # self.fire()

    def read(self):
        readback = self.ser.read(50)
        print(readback)
        # hexbuffer = ""
        # while True:
        #     oneByte = self.ser.read(1)
        #     if oneByte == b"\4":
        #         print(hexbuffer)
        #         # print(hexbuffer[48])
        #         return hexbuffer
        #     else:
        #         hexbuffer += oneByte.decode("ascii")
        #     continue

    def fire(self):
        print("Firing Wheel")
        # TODO: Validate hex command here
        sr3hexcommand = bytearray.fromhex("01 30 34 02 53 52 33 03 82 04")
        firehexcommand = bytearray.fromhex("01 30 34 02 52 43 30 33 03 62 04")
        self.ser.write(firehexcommand)
        print("***\n" + str(firehexcommand) + "\n***")
        self.read()

    def checksum(self):
        firehex = bytearray.fromhex("01 30 34 02 53 52 33 03")
        checksum = hex(sum(firehex) & 0x3f | 0x40)
        print(str(checksum))



app = Thing()

# app.checksum()
app.run()