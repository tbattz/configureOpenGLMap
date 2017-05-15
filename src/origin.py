''' Created by Trevor Batty
    Date: May 14th 2017
   
    Creates the origin section of the GUI.
'''

import tkinter as tk
from tkinter import ttk
import tkMessageBox

import subprocess as sp


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
        self.latVar = tk.DoubleVar()
        self.latEntry = tk.Entry(self,textvariable=self.latVar,width=10)
        self.latVar.set(-37.958926)
        self.latEntry.grid(column=1, row=1, sticky=tk.W)
        self.lonVar = tk.DoubleVar()
        self.lonEntry = tk.Entry(self,textvariable=self.lonVar,width=10)
        self.lonVar.set(145.238343)
        self.lonEntry.grid(column=1, row=2, sticky=tk.W)
        # Create Altitude, Heading label
        self.grid_columnconfigure(2,minsize=50)
        self.altLabel = ttk.Label(self, text="Altitude").grid(column=3, row=1, sticky=tk.W)
        self.headLabel = ttk.Label(self, text="Heading").grid(column=3, row=2, sticky=tk.W)
        # Create Altitude, Heading Entry Boxes
        self.altVar = tk.DoubleVar()
        self.altEntry = tk.Entry(self,textvariable=self.altVar,width=10)
        self.altVar.set(44)
        self.altEntry.grid(column=4, row=1, sticky=tk.W)
        self.headVar = tk.DoubleVar()
        self.headEntry = tk.Entry(self,textvariable=self.headVar,width=10)
        self.headVar.set(0)
        self.headEntry.grid(column=4, row=2, sticky=tk.W)
        # Add Traces
        self.latVar.trace("w",self.on_lat_changed)
        self.lonVar.trace("w",self.on_lon_changed)
        self.altVar.trace("w",self.on_alt_changed)
        self.headVar.trace("w",self.on_head_changed)
        
        
    def on_lat_changed(self,*args):
        # Lattitude Changed
        lat = self.latVar.get()
        if (len(str(lat))>1):
            if (lat<-90 or lat>90):
                tkMessageBox.showerror(message="Latitude must be between -90 and 90.")
                if (lat<-90):
                    self.latVar.set(-90)
                elif (lat>90):
                    self.latVar.set(90)

    def on_lon_changed(self,*args):
        # Longitude Changed
        lon = self.lonVar.get()
        if (lon<-180 or lon>180):
            tkMessageBox.showerror(message="Longitude must be between -180 and 180.")
            if (lat<-180):
                self.latVar.set(-180)
            elif (lat>180):
                self.latVar.set(180)
    
    def on_alt_changed(self,*args):
        # Altitude Changed
        pass
        
    def on_head_changed(self,*args):
        # Heading Changed
        head = self.headVar.get()
        if (head<0 or head>360):
            tkMessageBox.showerror(message="Heading must be between 0 and 360.")
            if (lat<0):
                self.latVar.set(0)
            elif (lat>360):
                self.latVar.set(360)

    def writeConfig(self,f):
        '''# Writes the display section of the config to file
            f.write("# Display Settings\n")
            f.write("screenID int %i\n" % (self.currMon+1))
            f.write("xRes int %i\n" % int(self.xResVar.get()))
            f.write("yRes int %i\n" % int(self.yResVar.get()))
            f.write("fullscreen bool %i\n" % self.fsCheckVar.get())
        f.write("\n")'''
        pass
            
        

