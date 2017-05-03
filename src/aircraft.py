''' Created by Trevor Batty
    Date: April 28th 2017
   
    Creates the display section of the GUI.
'''

import tkinter as tk
from tkinter import ttk, filedialog
import tkMessageBox


class Aircraft(ttk.Frame):   
    def __init__(self,root,mainFrame):
        # Create Aircraft frame
        ttk.Frame.__init__(self,mainFrame,padding="3 3 3 3")
        # Create AIRCRAFT label
        self.dispLabel = ttk.Label(self, text="AIRCRAFT", font=(None,16)).grid(column=0, row=0, sticky=tk.W)
        # Create Table titles label
        self.monLabel = ttk.Label(self, text="Aircraft Name").grid(column=0, row=1, sticky=tk.W, padx=5)
        self.pathLabel = ttk.Label(self, text="Model Path").grid(column=1,row=1, sticky=tk.W, padx=5)
        self.ipLabel = ttk.Label(self, text="Socket IP").grid(column=2,row=1, sticky=tk.W, padx=5)
        self.portLabel = ttk.Label(self, text="Socket Port").grid(column=3,row=1, sticky=tk.W, padx=5)
        # Create Row(s)
        row=2
        # Create Aircraft Name Entry
        self.name = tk.StringVar()
        self.name.set('Aircraft1')
        self.nameEntry = tk.Entry(self,textvariable=self.name,width=10)
        self.nameEntry.grid(column=0,row=row,sticky=tk.W, padx=5)
        # Create Model path selection
        self.button = ttk.Button(self, text="Select file", command=self.loadFile)
        self.button.grid(column=1,row=row,sticky=tk.W, padx=5)
        # Create Socket IP Entry
        self.ip = tk.StringVar()
        self.ip.set("192.168.1.1")
        self.ipEntry = tk.Entry(self,textvariable=self.ip,width=10)
        self.ipEntry.grid(column=2,row=row,sticky=tk.W, padx=5)
        # Create Port Entry
        self.port = tk.StringVar()
        self.port.set("14550")
        self.portEntry = tk.Entry(self,textvariable=self.port,width=10)
        self.portEntry.grid(column=3,row=row,sticky=tk.W, padx=5)
        
    def loadFile(self):
        # Opens the file load dialog window
        self.filename = filedialog.askopenfilename(filetypes=(("Object files","*.obj"),("All files","*.*")),initialdir="../../Models/")
        
        # Cut filename if in models folder
        if "/Models/" in self.filename:
            pos = self.filename.find("/Models/")
            self.fileLabel = self.filename[pos:]
        else:
            self.fileLabel = self.filename
        
        # Set Button Label
        self.button.config(text=self.fileLabel)
        
        
        
        
# TO ADD
# AIRCRAFT +/- buttons for multiple aircraft
# Set world origin in lat, lon, alt
# Skybox folder selection
# Plot toggle
# Timing checks - check for new tiles time
#               - aircraft mavlink delay time
# Display fps
# Display telemetry overlay toggle (more options to come, possibly aircraft name overlay)
# Select terrain data
        
