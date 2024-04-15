import socket
from tkinter import *
import threading
import os 
import json


def read_server_counter():
    with open('naming.json', 'r') as file:
        data = json.load(file)
        return data['ServerCtr']
def write_server_counter(counter):
    with open('naming.json', 'r+') as file:
        data = json.load(file)
        data['ServerCtr'] = counter
        file.seek(0)
        json.dump(data, file, indent=4)
        file.truncate()





def accept_connections(server, connLabel ,fileLabel , fileEntry , sendBtn , recFrame):
        client, address = server.accept()
        connLabel.config(text=f"Connection established with {address[0]}")
        # Place the gui elements of file sending 
        fileLabel.place(x=100 ,y=150)
        fileEntry.place(x=290 , y=150)
        sendBtn.place(x=570 ,y=150)
        # Place the list of rec files 
        recFrame.place(x=100 , y= 200)
        # close the Main connection 
        server.close()
        # now start sendfile thread


        threading.Thread(target= SendFile , args=(sendBtn , fileEntry) ).start()
        threading.Thread(target= ReceiveFile , args=(recFrame,) ).start()        
def SendFile(sendBtn , fileEntry):

    sendBtn.config(command = lambda: send_Click(fileEntry.get()))
     # Create server_send_socket
    server_send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_send_socket.bind((ServerIP, 12345))  # Adjust the IP and port as needed
    server_send_socket.listen(1)
    print("Server send socket is listening...")
    
    def send_Click(filename):
        
        if not os.path.isfile(filename):
            print(f"File '{filename}' not found")
            return
        fileEntry.delete(0 , END)
        client_send_socket, client_address = server_send_socket.accept()
        print(f"Connection established with {client_address}")

        with open(filename, "rb") as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                client_send_socket.send(data)

        client_send_socket.close()
        print("File sent successfully")
    
    
    # create server_send_socket 
    # start listening 
    # add event click function 
    # send click funtion 
    # # accept connection 
    # # open the file 
    # # while not eof  send data 
    # # finaly close the connection 


def ReceiveFile(recFrame):
    
    # Create server_rec_socket
    server_rec_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_rec_socket.bind((ServerIP, 12346))  # Adjust the IP and port as needed
    server_rec_socket.listen(1)  # Listen for incoming connections

    print("Waiting for client to send a file...")
    
    file_counter = read_server_counter()
    folder_name = "server_received_files"
    try:
        
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
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



        # Accept connections and create the received file
        while True:
            # Accept a connection from the client
            client_socket, client_address = server_rec_socket.accept()
            print(f"Connected to client at {client_address}")

            # Create a new file for receiving data
            received_filename = os.path.join(folder_name, f"SERVER_received{file_counter}.rar")
            file_counter+=1
            write_server_counter(file_counter)
            with open(received_filename, "wb") as file:
                # Receive data and write to the file until EOF
                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        print("End of file. Connection closed by client.")
                        break
                    file.write(data)

            print(f"File received from {client_address} and saved as {received_filename}")
            label = Label(frame , text= f"{received_filename}",font=19)
            label.pack()
            recLabelList.append(label)



    except KeyboardInterrupt:
        print("Server stopped")

    finally:
        # Close the server receive socket
        server_rec_socket.close()    
    
    # create server_rec_socket
    #start lsitening 
    # while true accept conn + create the rec  file 
    # #   while true  write in the file utill the client close connection 
    


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

ServerIP = get_ip()


def main():
    window = Tk()
    window.title("Server")
    window.geometry("800x500+200+100") 
    ipLabel = Label (window,text=f"IP Server: {ServerIP}",font= 19)
    ipLabel.place(x=270 , y=20)
    connLabel= Label(window, text="No connection established yet", font=18)
    connLabel.place(x=270, y=70)
    # file recieving labels list 
    recFrame = Frame(window,width=400 , height= 100 , borderwidth=2, relief="solid")
    
    global recLabelList 
    recLabelList = []

    # file sending elements 
    fileLabel = Label(window,text="File: ",font=19)
    fileEntry = Entry(window,width=30,font=19)
    sendBtn = Button(window,text="Send",font=19)
    
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ServerIP, 1234))
    server.listen(1)

    # Start a separate thread to handle connections
    threading.Thread(target=accept_connections, args=(server, connLabel , fileLabel , fileEntry , sendBtn , recFrame ), daemon=True).start()
    window.mainloop()    

