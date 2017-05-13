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
        self.latVar = tk.StringVar()
        self.latEntry = tk.Entry(self,textvariable=self.latVar,width=10)
        self.latEntry.insert(0,-37.958926)
        self.latEntry.grid(column=1, row=1, sticky=tk.W)
        self.lonVar = tk.StringVar()
        self.lonEntry = tk.Entry(self,textvariable=self.lonVar,width=10)
        self.lonEntry.insert(0,145.238343)
        self.lonEntry.grid(column=1, row=2, sticky=tk.W)
        # Create Altitude, Heading label
        self.grid_columnconfigure(2,minsize=50)
        self.altLabel = ttk.Label(self, text="Altitude").grid(column=3, row=1, sticky=tk.W)
        self.headLabel = ttk.Label(self, text="Heading").grid(column=3, row=2, sticky=tk.W)
        # Create Altitude, Heading Entry Boxes
        self.altVar = tk.StringVar()
        self.altEntry = tk.Entry(self,textvariable=self.altVar,width=10)
        self.altEntry.insert(0,44)
        self.altEntry.grid(column=4, row=1, sticky=tk.W)
        self.headVar = tk.StringVar()
        self.headEntry = tk.Entry(self,textvariable=self.headVar,width=10)
        self.headEntry.insert(0,0)
        self.headEntry.grid(column=4, row=2, sticky=tk.W)
        # Add Traces
        self.latVar.trace("w",self.on_lat_changed)
        self.lonVar.trace("w",self.on_lon_changed)
        self.altVar.trace("w",self.on_alt_changed)
        self.headVar.trace("w",self.on_head_changed)
        
        
    def on_lat_changed(self,*args):
        # Lattitude Changed
        pass
    
    def on_lon_changed(self,*args):
        # Longitude Changed
        pass
    
    def on_alt_changed(self,*args):
        # Altitude Changed
        pass
        
    def on_head_changed(self,*args):
        # Heading Changed
        pass

    def writeConfig(self,f):
        '''# Writes the display section of the config to file
            f.write("# Display Settings\n")
            f.write("screenID int %i\n" % (self.currMon+1))
            f.write("xRes int %i\n" % int(self.xResVar.get()))
            f.write("yRes int %i\n" % int(self.yResVar.get()))
            f.write("fullscreen bool %i\n" % self.fsCheckVar.get())
        f.write("\n")'''
        pass
            
        

