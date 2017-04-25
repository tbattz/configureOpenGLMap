''' Created by Trevor Batty
    Date: April 25th 2017
   
    Tools for the running of the GUI.
'''

import tkinter as tk
from tkinter import ttk

import sys


# Close window on ESC
def close(event):
    sys.exit()




class Generate(ttk.Frame):   
    def __init__(self,mainFrame):
        # Create Generate frame
        ttk.Frame.__init__(self,mainFrame,padding="3 3 3 3")
        # Create Load Button
        self.loadButton = tk.Button(self,text="Load Config",command=self.on_load_config)
        self.loadButton.grid(column=0,row=0)
        # Create Save Button
        self.loadButton = tk.Button(self,text="Save Config",command=self.on_save_config)
        self.loadButton.grid(column=1,row=0)
         # Create Generate Button
        self.genButton = tk.Button(self,text="Generate Configuration",command=self.on_gen_config)
        self.genButton.grid(column=0,row=1,columnspan=2)
        
    def on_load_config(self):
        print 1
        
    def on_save_config(self):
        print 1
    
    def on_gen_config(self):
        print 1