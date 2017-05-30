''' Created by Trevor Batty
    Date: May 14th 2017
   
    Creates the origin section of the GUI.
'''

import tkinter as tk
from tkinter import ttk
import tkMessageBox

import subprocess as sp

import tools


class Origin(ttk.Frame):   
    def __init__(self,root,mainFrame):
        # Create Origin frame
        ttk.Frame.__init__(self,mainFrame,padding="3 3 3 3")
        # Create Origin label
        self.dispLabel = ttk.Label(self, text="ORIGIN", font=(None,16)).grid(column=0, row=0, sticky=tk.W)
        # Create Lat,Lon label
        self.latLabel = ttk.Label(self, text="Latitude").grid(column=0, row=1, sticky=tk.W)
        self.latLabel = ttk.Label(self, text="Longitude").grid(column=0, row=2, sticky=tk.W)
        # Create Lat,Lon Entry Boxes
        self.latVar = tk.StringVar()
        self.latEntry = tk.Entry(self,textvariable=self.latVar,width=10)
        self.latVar.set('-37.958926')
        self.latEntry.grid(column=1, row=1, sticky=tk.W)
        self.lonVar = tk.StringVar()
        self.lonEntry = tk.Entry(self,textvariable=self.lonVar,width=10)
        self.lonVar.set(145.238343)
        self.lonEntry.grid(column=1, row=2, sticky=tk.W)
        # Create Altitude, Heading label
        self.grid_columnconfigure(2,minsize=50)
        self.altLabel = ttk.Label(self, text="Altitude").grid(column=3, row=1, sticky=tk.W)
        self.headLabel = ttk.Label(self, text="Heading").grid(column=3, row=2, sticky=tk.W)
        # Create Altitude, Heading Entry Boxes
        self.altVar = tk.StringVar()
        self.altEntry = tk.Entry(self,textvariable=self.altVar,width=10)
        self.altVar.set(44)
        self.altEntry.grid(column=4, row=1, sticky=tk.W)
        self.headVar = tk.StringVar()
        self.headEntry = tk.Entry(self,textvariable=self.headVar,width=10)
        self.headVar.set(0)
        self.headEntry.grid(column=4, row=2, sticky=tk.W)
        # Add Traces
        self.latVar.trace("w",self.on_lat_changed)
        self.lonVar.trace("w",self.on_lon_changed)
        self.altVar.trace("w",self.on_alt_changed)
        self.headVar.trace("w",self.on_head_changed)
        
        
    def on_lat_changed(self,*args):
        # Latitude Changed
        latStr = self.latVar.get()
        valid, lat = tools.validateFloat(latStr)
        
        if not valid:
            tkMessageBox.showerror(message="Latitude must be between -90 and 90.")
            self.latVar.set(0)
        else:
            if (lat<-90) or (lat>90):
                tkMessageBox.showerror(message="Latitude must be between -90 and 90.")
                self.latVar.set(cmp(lat,0)*90)

    def on_lon_changed(self,*args):
        # Longitude Changed
        lonStr = self.lonVar.get()
        valid, lon = tools.validateFloat(lonStr)
        
        if not valid:
            tkMessageBox.showerror(message="Longitude must be between -180 and 180.")
            self.lonVar.set(0) 
        else:
            if (lon<-180) or (lon>180):
                tkMessageBox.showerror(message="Longitude must be between -180 and 180.")
                self.lonVar.set(cmp(lon,0)*180)
    
    def on_alt_changed(self,*args):
        # Altitude Changed
        altStr = self.altVar.get()
        valid, alt = tools.validateFloat(altStr)
        
        if not valid:
            tkMessageBox.showerror(message="Altitude must be a float.")
            self.altVar.set(0) 
        
    def on_head_changed(self,*args):
        # Heading Changed
        headStr = self.headVar.get()
        valid, head = tools.validateFloat(headStr)
        
        if not valid:
            tkMessageBox.showerror(message="Heading must be between 0 and 360.")
            self.headVar.set(0)
        else:
            if (head<0):
                tkMessageBox.showerror(message="Heading must be between 0 and 360.")
                self.headVar.set('0')
            elif (head>360):
                tkMessageBox.showerror(message="Heading must be between 0 and 360.")
                self.headVar.set('360')

    def checkEmptyEntry(self,str):
        # Checks if the entry is empty or '-'
        if (str == "") or (str == "-"):
            val = "0"
        else:
            val = str
            
        return val

    def writeConfig(self,f):
        # Writes the display section of the config to file
        # Check for empty entries
        lat = self.checkEmptyEntry(self.latVar.get())
        lon = self.checkEmptyEntry(self.lonVar.get()) 
        alt = self.checkEmptyEntry(self.altVar.get()) 
        head = self.checkEmptyEntry(self.headVar.get()) 
        # Write to file
        f.write("# Origin Settings\n")
        f.write("origin ")
        f.write(lat + " ")
        f.write(lon + " ")
        f.write(alt + " ")
        f.write(head)
        f.write("\n")
        
            
        

