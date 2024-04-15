
from tkinter import *
import socket 
import re
import threading
import os 
import json
import atexit 

def cleanup_empty_files():
    folder_path = "client_receive_files"
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.getsize(file_path) == 0:
            os.remove(file_path)

# Register the cleanup function to be called upon program exit
atexit.register(cleanup_empty_files)


def read_client_counter():
    with open('naming.json', 'r') as file:
        data = json.load(file)
        return data['ClientCtr']
    
def write_client_counter(counter):
    with open('naming.json', 'r+') as file:
        data = json.load(file)
        data['ClientCtr'] = counter
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()    



def is_valid_ipv4(ip):
    ipv4_pattern = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    return re.match(ipv4_pattern, ip) is not None
    

def recvFile(recFrame):
    file_counter = read_client_counter()
    folder_name = "client_receive_files"
     # Create a Canvas widget to contain the scrollable frame
    canvas = Canvas(recFrame)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)
    
    # Create a Scrollbar widget and associate it with the Canvas
    scrollbar = Scrollbar(recFrame, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Create a Frame to hold the labels
    frame = Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor=NW)
    
    # Function to update scroll region when the frame size changes
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    
    frame.bind("<Configure>", on_frame_configure)

    while True:
        # Ensure the folder for received files exists
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        # Create client_receive_socket
        client_receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_receive_socket.connect((IP, 12345))  # Adjust the IP and port as needed
        print("Connected to server for receiving files...")

        filename = os.path.join(folder_name, f"rec{file_counter}.rar")
        file_counter+=1
        write_client_counter(file_counter)
        with open(filename, "wb") as file:
            while True:
                data = client_receive_socket.recv(1024)
                if not data:
                    break
                file.write(data)

        print(f"File '{filename}' received successfully")
        label = Label(frame, text=f"{filename}",font=19)
        label.pack()
        

        # Close the client socket after receiving the file
        client_receive_socket.close()


def sendFile(sendBtn , fileEntry):
    sendBtn.config(command = lambda: send_Click(fileEntry.get()))
    def send_Click(filename):
        
        if not os.path.isfile(filename):
            print(f"File '{filename}' not found")
            return
        fileEntry.delete(0 , END)
        client_send_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        client_send_socket.connect((IP,12346))
        with open(filename, "rb") as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                client_send_socket.send(data)

        client_send_socket.close()
        print("File sent successfully")




IP ="0.0.0.0"  


def main():
    def connect(ip):
        global IP
        if not is_valid_ipv4(ip):
            return
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, 1234))
            IP = ip
            # Destroy the GUI elements upon successful connection
            ipLabel.destroy()
            ipEntry.destroy()
            connBtn.destroy()
            #Place the apropriate GUI elements 
            fileLabel.place(x=100 ,y=150)
            fileEntry.place(x=290 , y=150)
            sendBtn.place(x=570 ,y=150) 
            # Place the list of rec files 
            recFrame.place(x=100 , y= 200)
            sock.close()

        except socket.error as e:
            print(f"Error: {e}")
        threading.Thread(target=recvFile , args= (recFrame,) ).start()
        threading.Thread(target=sendFile , args=(sendBtn , fileEntry) ).start()
        

    window = Tk()
    window.title("Client")
    window.geometry("800x500+200+100")

    ipLabel = Label(window,text="Enter the ip of the server",font=20)
    ipLabel.place(x=100 ,y=200) 

    ipEntry = Entry(window,width=20,font=20)
    ipEntry.place(x=290 , y=200)

    connBtn = Button(window,text="Connect",font=19)
    connBtn.place(x=500 , y=200)

    connBtn.config(command= lambda : connect(ipEntry.get()))
    # file sending GUI elements
    fileLabel = Label(window,text="File: ",font=19)
    fileEntry = Entry(window,width=30,font=19)
    sendBtn = Button(window,text="Send",font=19)

    # file recieving labels list 
    recFrame = Frame(window,width=400 , height= 100 , borderwidth=2, relief="solid")

    recLabelList = []
    

    window.mainloop()
# take the ip from the client and try to connect using this ip 
# once the connection established go to the next window of sharing files 
