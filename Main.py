from  tkinter   import *
import Client
import Server


def ServerClick():
    window.destroy()
    Server.main()

def ClientClick():
    window.destroy()
    Client.main()



window = Tk()

window.geometry("800x500+260+100")

serverBtn = Button(window,text="Server" , width=30)
clientBtn = Button(window,text="client" , width=30)

serverBtn.config(command=ServerClick)
clientBtn.config(command=ClientClick)
serverBtn.place(x= 280 , y= 150)
clientBtn.place(x=280 , y= 250)




window.mainloop()