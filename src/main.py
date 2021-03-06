''' Created by Trevor Batty
    Date: April 25th 2017
   
    Launches a GUI that allows the user to create an OpenGLMap settings file.
'''

from tkinter import *
from tkinter import ttk



import mydisplay, tools, aircraft, volume, origin

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
displayFrame.grid(column=0,row=0,stick='w')

# Add horizontal line
ttk.Separator(mainFrame,orient=HORIZONTAL).grid(column=0,row=1,sticky='ew')

# Add Aircraft section
aircraftFrame = aircraft.Aircraft(root,mainFrame)
aircraftFrame.grid(column=0,row=2,sticky='w')

# Add horizontal line
ttk.Separator(mainFrame,orient=HORIZONTAL).grid(column=0,row=3,sticky='ew')

# Add Origin Section
originFrame = origin.Origin(root,mainFrame)
originFrame.grid(column=0,row=4,sticky='w')

# Add horizontal line
ttk.Separator(mainFrame,orient=HORIZONTAL).grid(column=0,row=5,sticky='ew')

# Create Volumne section
volumeFrame = volume.Volume(root,mainFrame,originFrame)
volumeFrame.grid(column=0,row=6,sticky='w')
originFrame.volFrame = volumeFrame

# Add horizontal line
ttk.Separator(mainFrame,orient=HORIZONTAL).grid(column=0,row=7,sticky='ew')

# Create Generate section
generateFrame = tools.Generate(root,mainFrame,displayFrame,aircraftFrame,originFrame,volumeFrame)
generateFrame.grid(column=0,row=8)




# Close on Escape
root.bind('<Key-Escape>',generateFrame.close)

# Change close function
root.protocol("WM_DELETE_WINDOW", generateFrame.closeExitButton)

# Show gui
root.mainloop()
