from tkinter import *
# from SaturnFire import serialport


class WheelFireGUI:
    def __init__(self, root):
        print("Launching GUI")
        selectport = serialport
        root.title("Serial Tests")
        self.port = Entry(root, textvariable=selectport)
        self.port.grid(row=0, column=0)
        self.label = Label(root, text="ThisIsText")
        self.label.grid(row=0, column=1)

# baudlabel = Label(window, text="Baud Rate: ")
# portlabel = Label(window, text="Port:: ")
# baudentry = Entry(window, textvariable=serialbaudrate)
# portentry = Entry(window, textvariable=serialport)
# baudlabel.grid(row=0, column=0)
# portlabel.grid(row=1, column=0)
# baudentry.grid(row=0, column=1)
# portentry.grid(row=1, column=1)
# openconnection = Button(window, text="Open Serial", command=lambda: open_serial())
# openconnection.grid(row=3, column=1)
#
#
#
#
# def message_box(openerror):
#     messagebox.showerror("ERROR!", openerror)




root = Tk()
app = WheelFireGUI(root)
root.mainloop()


