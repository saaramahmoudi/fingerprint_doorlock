import re
import struct
import time
from tkinter import *
from tkinter import messagebox
import xlsxwriter

import pexpect
import serial.tools.list_ports
from pexpect.popen_spawn import PopenSpawn
from serial import Serial

window = Tk()
arduino = serial.Serial


def checkinput(trigger, command):
    if str('L') in str(command):
        read = ""
        t = 0
        while str(trigger) not in str(read) and t < 25:
            arduino.write(str(command).encode())
            read = arduino.read(1)
            if str('l') in str(read):
                print("logged out")
                return 'l'
            time.sleep(1)
            t += 1
        return read
    read = ""
    while str(trigger) not in str(read):
        arduino.write(str(command).encode())
        read = arduino.read(1)
        # print(read)
        if str('l') in str(read):
            print("logged out")
            return 'l'
        time.sleep(.25)
    return read


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        arduino.close()
        window.destroy()


window.title("Fingerprint Scanner Controller")
window.protocol("WM_DELETE_WINDOW", on_closing)

window.geometry('501x425')
window.resizable(False, False)
frame = Frame(window)
frame.pack()


# def countdown(count):
#     # change text in label
#     label['text'] = "Remaining Time : " + str(count)
#     label.wait_window

#     if count > 0:
#         # call countdown again after 1000ms (1s)
#         window.after(1000, countdown, count-1)
#     else:
#         window.destroy()


# label = Label(window)
# label.config(fg="red")
# label.place(x=198, y=400)


def promptTextFiller(s):
    promptText.config(state=NORMAL)
    promptText.delete("1.0", END)
    promptText.insert(INSERT, s)
    promptText.config(state=DISABLED)


def disableenablebtns(enable):
    if enable == False:
        adduserbtn.config(state='disable')
        addadminbtn.config(state='disable')
        deleteuserbtn.config(state='disable')
        deleteadminbtn.config(state='disable')
        getreportbtn.config(state = 'disable')
        logginbtn.config(state='normal')
        messagebox.showwarning(title="Time Out!",
                               message="Please Login Again!")
    elif enable == True:
        adduserbtn.config(state='normal')
        addadminbtn.config(state='normal')
        deleteuserbtn.config(state='normal')
        deleteadminbtn.config(state='normal')
        logginbtn.config(state='disable')
        getreportbtn.config(state = 'normal')

def getReport():
    res = checkinput('V', 'v')
    if str('l') in str(res):
        print("logged out")
        disableenablebtns(False)
        return
    stids = []
    s = ""
    i = 0
    while i != 127 :
        res = arduino.readline(8)
        time.sleep(0.0025)
        s += str(res)
        # print(str(res))
        # print("ID : " + str(i) + " Student ID : "  + str(res).replace('b', ''))
        res = str(res).replace('b', '')
        res = str(res).replace('\\r', '')
        res = str(res).replace('\\n', '')
        if(len(res) > 2):
            i += 1
            stids.append(str(res))
    workbook = xlsxwriter.Workbook('StudentList.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0
    col = 1
    worksheet.write(row,col,'ID')
    worksheet.write(row,col+1,'Student ID')
    for row, data in enumerate(stids):
        # if len(data) > 4:
            worksheet.write(row + 1, col,row + 1)
            worksheet.write(row + 1,col+1,data)
            row += 1
    workbook.close()
    promptTextFiller('Report Has Been Generated Into Excel File : StudentList.xlsx')
    arduino.flushOutput()
    arduino.flushInput()
    return
    #print(stids)



def adduser():
    # if addusertxt.compare("end-1c", "==", "1.0"):
    #     messagebox.showwarning("Empty Field", "Enter ID First!")
    #     return
    # id = addusertxt.get("1.0", END)
    if adduseridtext.compare("end-1c", "==", "1.0"):
        messagebox.showwarning("Empty Field", "Enter Student ID First!")
        return
    stid = adduseridtext.get("1.0", END)
    # if int(id) > 127:
    #     messagebox.showwarning("Invalid ID", "ID Must Be Between 3 To 127")
    #     return
    r = checkinput("A", 'a')
    if str('l') in str(r):
        print("logged out")
        disableenablebtns(False)
        return
    arduino.flushOutput()

    s = str(('q' + str(stid) + 'z')).replace('\n', '')
    print(s)
    res = checkinput("i", s)
    
    res = arduino.read(1)
    # print(str(res))
    if str('l') in str(res):
        print("logged out")
        disableenablebtns(False)
        return
    elif str("Y") in str(res):
        promptTextFiller("ID {} Already Exists. Please Try To Delete It First Or Try With Another ID".format(
            id).replace('\n', ''))
        adduseridtext.delete("1.0", END)
        return
    elif str('U') in str(res):
        messagebox.showerror('Capacity', 'Database Is Full!')
    else:
        # time.sleep(1)
        print('Waiting For A Valid Finger...')
        messagebox.showinfo('Info','Waiting For A Valid Finger...')
        
        read = ""
        while (str('f') in str(read)) or len(read) == 0:
            read = arduino.read(1)
            #print(read)
            #print(len(read))
            if str('l') in str(read):
                print("logged out")
                disableenablebtns(False)
                return
        if str("t") not in str(read):
            print("Image Not Taken... \n")
            # promptTextFiller("An Error Occured,Please Try Again Later..!")
            adduseridtext.delete("1.0", END)
            return
        else:
            print("Image Taken... \n")
            # promptTextFiller("Image Taken... \n")s
            # time.sleep(1)
            # messagebox.showinfo("Image Taken... \n")
            read = ""
            while len(read) == 0:
                read = arduino.read(1)
            print(str(read))
            if str('l') in str(read):
                print("logged out")
                disableenablebtns(False)
                return
            elif str("c") not in str(read):
                print("Image Not Converted...\n")
                promptTextFiller("An Error Occured,Please Try Again Later..!")
                adduseridtext.delete("1.0", END)
                return
            else:
                print("Image Converted... \n")
                # promptTextFiller("Image Converted... \n")
                # time.sleep(1)
                # messagebox.showinfo("Image Converted... \n")
                read = ""
                while len(read) == 0:
                    read = arduino.read(1)
                if str('l') in str(read):
                    print("logged out")
                    disableenablebtns(False)
                    return
                elif str("r") not in str(read):
                    promptTextFiller(
                        "An Error Occured,Please Try Again Later..!")
                    adduseridtext.delete("1.0", END)
                    return
                else:
                    print("Remove Your Finger...\n")
                    time.sleep(0.25)
                    messagebox.showinfo('Info', 'Remove And Place The Same Finger...')
                    print("Place The Same Finger Again...\n")
                    read = ""
                    while str("f") in str(read) or len(read) == 0:
                        read = arduino.read(1)
                        if str('l') in str(read):
                            print("logged out")
                            disableenablebtns(False)
                            return
                    if str("t") not in str(read):
                        print("Second Image Not Taken...\n")
                        promptTextFiller(
                            "An Error Occured,Please Try Again Later..!")
                        adduseridtext.delete("1.0", END)
                        return
                    else:
                        print("Second Image Taken...\n")
                        read = ""
                        while len(read) == 0:
                            read = arduino.read(1)
                        if str('l') in str(read):
                            print("logged out")
                            disableenablebtns(False)
                            return
                        elif str("c") not in str(read):
                            print("Second Image Not Converted...\n")
                            promptTextFiller(
                                "An Error Occured,Please Try Again Later..!")
                            adduseridtext.delete("1.0", END)
                            return
                    print("Second Image Taken...\n")
                    read = ""
                    while len(read) == 0:
                        read = arduino.read(1)
                    if str('l') in str(read):
                        print("logged out")
                        disableenablebtns(False)
                        return
                    elif str("p") not in str(read):
                        print("Not Stored...\n")
                        promptTextFiller(
                            "An Error Occured,Please Try Again Later..!")
                        adduseridtext.delete("1.0", END)
                        return
                    else:
                        time.sleep(2)
                        print("Stored...\n")
                        id = str(arduino.readline())
                        print(id)
                        ss = []
                        ss = id.split('h')
                        sd = []
                        sd = ss[0].split('p')
                        id = sd[1]
                        print(sd[1])
                        messagebox.showinfo('Info', 'Successfuly Stored , ID : {}'.format(id))
                        promptTextFiller("Successfull!")
    adduseridtext.delete("1.0", END)


def addadmin():
    if addadmintxt.compare("end-1c", "==", "1.0"):
        messagebox.showwarning("Empty Field", "Enter ID First!")
        return
    id = addadmintxt.get("1.0", END)
    if int(id) > 127:
        messagebox.showwarning("Invalid ID", "ID Must Be Between 3 To 127")
        return
    checkinput("C", 'c')
    s = 'b\''+str(id)
    res = checkinput("i", s)
    if str('l') in str(res):
        print("logged out")
        disableenablebtns(False)
        addadmintxt.delete("1.0", END)
        return
    res = arduino.read(1)
    if str("e") in str(res):
        promptTextFiller("ID {} Does Not Exist".format(id).replace('\n', ''))
    elif str("X") in str(res):
        promptTextFiller(
            "ID {} Is Already An Admin".format(id).replace('\n', ''))
    elif str('l') in str(res):
        print("logged out")
        disableenablebtns(False)
        addadmintxt.delete("1.0", END)
        return
    else:
        promptTextFiller("ID {} Became An Admin".format(id).replace('\n', ''))
    addadmintxt.delete("1.0", END)


def deleteuser():

    if deleteusertxt.compare("end-1c", "==", "1.0"):
        messagebox.showwarning("Empty Field", "Enter ID First!")
        return
    id = deleteusertxt.get("1.0", END)
    if int(id) > 127:
        messagebox.showwarning("Invalid ID", "ID Must Be Between 3 To 127")
        return
    
    if messagebox.askokcancel("Delete User", "Delete User: # " + str(id) + " ?"):
        res = "ID:" + deleteusertxt.get("1.0", END)
        print(res)
        promptTextFiller(res)
        deleteusertxt.delete("1.0", END)

    res = checkinput('K', 'k')
    print(str(res))
    if str('l') in str(res):
        print("logged out")
        disableenablebtns(False)
        deleteusertxt.delete("1.0", END)
        return
    s = 'b\''+str(id)
    res = checkinput('i', s)
    print('i is read')
    res = arduino.read(1)
    if str('l') in str(res):
        print("logged out")
        disableenablebtns(False)
        deleteusertxt.delete("1.0", END)
        return
    if str('d') in str(res):
        promptTextFiller("The ID Is Deleted")
    elif str('X') in str(res):
        promptTextFiller("This ID Belongs To An Admin")
    else:
        print(res)
        promptTextFiller("An Error Occured, Please Try Again")
    deleteusertxt.delete("1.0", END)


def deleteadmin():

    if deleteadmintxt.compare("end-1c", "==", "1.0"):
        messagebox.showwarning("Empty Field", "Enter ID First!")
        return
    id = deleteadmintxt.get("1.0", END)
    if int(id) > 127:
        messagebox.showwarning("Invalid ID", "ID Must Be Between 3 To 127")
        return
    if messagebox.askokcancel("Delete Admin", "Delete Admin: # " + str(id) + " ?"):
        res = "ID:" + deleteadmintxt.get("1.0", END)
        print(res)
        promptTextFiller(res)
        deleteadmintxt.delete("1.0", END)
    res = checkinput('D', 'd')
    if str('l') in str(res):
        print("logged out")
        disableenablebtns(False)
        deleteadmintxt.delete("1.0", END)
        return
    s = 'b\''+str(id)
    res = checkinput('i', s)
    res = arduino.read(1)
    if str('l') in str(res):
        print("logged out")
        disableenablebtns(False)
        deleteadmintxt.delete("1.0", END)
        return
    if str('s') in str(res):
        promptTextFiller("The ID Is Now A User")
        return
    elif str('X') in str(res):
        promptTextFiller("This ID Belongs To A Super Admin! :)")
    else:
        print(res)
        promptTextFiller("An Error Occured, Please Try Again")
    deleteadmintxt.delete("1.0", END)


def login():
    res = checkinput('M', 'L')
    if str('M') in str(res):
        disableenablebtns(True)
    else:
        disableenablebtns(False)



def on_entry_click(event):
    """function that gets called whenever entry is clicked"""
    
    # addusertxt.delete("1.0", END) # delete all the text in the entry
    # addusertxt.insert(0, '') #Insert blank for user input
    # addusertxt.config(fg = 'black')


promptText = Text(frame, width=50, height=10)
promptText.config(state=DISABLED)


adduserbtn = Button(frame, width=15, text="Add New User",
                    command=adduser, fg="green")
# addusertxt = Text(frame, height=1, width=8)
adduseridtext = Text(frame, height=1, width=13)

addadminbtn = Button(frame, width=15, text="Add New Admin",
                     command=addadmin, fg="green")
addadmintxt = Text(frame, height=1, width=8)
getreportbtn = Button(frame, width=15, text="Get Report",
                    command=getReport, fg="purple")

deleteuserbtn = Button(frame, width=15, text="Delete User",
                       command=deleteuser, fg="red")
deleteusertxt = Text(frame, height=1, width=8)

deleteadminbtn = Button(
    frame, width=15, text="Delete Admin", command=deleteadmin, fg="red")
deleteadmintxt = Text(frame, height=1, width=8)


logginbtn = Button(
    frame, width=15, text="Log in", command=login, fg="blue")

adduserbtn.grid(column=2, row=0)
# addusertxt.insert(INSERT, 'ID')
# addusertxt.grid(column=2, row=2)
adduseridtext.grid(column = 2, row = 3)
# adduseridtext.insert(END, 'Student ID')
# addusertxt.bind('<FocusIn>', on_entry_click)


deleteuserbtn.grid(column=2, row=20)
deleteusertxt.grid(column=2, row=22)

addadminbtn.grid(column=2, row=40)
addadmintxt.grid(column=2, row=42)

deleteadminbtn.grid(column=2, row=60)
deleteadmintxt.grid(column=2, row=62)

getreportbtn.grid(column=2, row = 80)


logginbtn.grid(column=2, row=100)

promptText.grid(column=2, row=250)





if __name__ == "__main__":

    # find out which port is connected to arduino
    connectedport = ""
    myports = [tuple(p) for p in list(serial.tools.list_ports.comports())]
    print(myports)
    for i in myports:
        # use the port name which the board is connected to
        if 'USB Serial Device' in i[1]:
            connectedport = str(i[0])
    print(connectedport)
    arduino = serial.Serial(connectedport, 9600, timeout=0, write_timeout=0)

    adduserbtn.config(state='disable')
    addadminbtn.config(state='disable')
    deleteuserbtn.config(state='disable')
    deleteadminbtn.config(state='disable')
    logginbtn.config(state='normal')
    getreportbtn.config(state = 'disable')

    arduino.read(1)
    # countdown(60)

    window.mainloop()
