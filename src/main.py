''' Created by Trevor Batty
    Date: April 25th 2017
   
    Launches a GUI that allows the user to create an OpenGLMap settings file.
'''

from tkinter import *
from tkinter import ttk



import mydisplay, tools

# Init Tkinter
root = Tk()
root.title("Configure OpenGLMap")

# Create Frame
mainFrame = ttk.Frame(root,padding="3 3 3 3")
mainFrame.grid(column=0,row=0,sticky=(N,W,E,S))
mainFrame.columnconfigure(0,weight=1)
mainFrame.rowconfigure(0,weight=1)

# Add Display section
displayFrame = mydisplay.Display(root,mainFrame)
displayFrame.grid(column=0,row=0)

# Add horizontal line
ttk.Separator(mainFrame,orient=HORIZONTAL).grid(column=0,row=1,sticky='ew')

# Create Generate section
generateFrame = tools.Generate(mainFrame,displayFrame)
generateFrame.grid(column=0,row=2)





# Close on Escape
root.bind('<Escape>',tools.close)

# Show gui
root.mainloop()