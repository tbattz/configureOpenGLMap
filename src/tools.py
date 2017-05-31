''' Created by Trevor Batty
    Date: April 25th 2017
   
    Tools for the running of the GUI.
'''

import tkinter as tk
from tkinter import ttk
import tkMessageBox
import getpass

import os, sys
import time





class Generate(ttk.Frame):   
    def __init__(self,root,mainFrame,displayFrame,aircraftFrame,originFrame,volumeFrame):
        # Create Generate frame
        ttk.Frame.__init__(self,mainFrame,padding="3 3 3 3")
        self.root = root
        self.mainFrame = mainFrame
        self.displayFrame = displayFrame
        self.aircraftFrame = aircraftFrame
        self.originFrame = originFrame
        self.volumeFrame = volumeFrame
        # Create Load Button
        self.loadButton = tk.Button(self,text="Load Config",command=self.on_load_config)
        self.loadButton.grid(column=0,row=0)
        # Create Save Button
        self.loadButton = tk.Button(self,text="Save Config",command=self.on_save_config)
        self.loadButton.grid(column=1,row=0)
         # Create Generate Button
        self.genButton = tk.Button(self,text="Generate Configuration",command=self.on_gen_config)
        self.genButton.grid(column=0,row=1,columnspan=2)
        
    # Close window on ESC
    def close(self,event):
        self.volumeFrame.close()
        sys.exit()

    # On Exit Button Clicked
    def closeExitButton(self):
        self.volumeFrame.close()
        self.root.quit()
        
    def on_load_config(self):
        print 1
        
    def on_save_config(self):
        print 1
    
    def on_gen_config(self):
        # Check Config directory exists
        if not os.path.isdir('../../Configs'):
            os.mkdir('../../Configs')
        # Print Header
        filename = '../../Configs/currentConfig.txt'
        f = open(filename,'w')
        f.write("# OpenGLMap Configuration File\n")
        f.write("# Created %s by %s\n" % (time.strftime("%c"),getpass.getuser()))
        f.write("\n")
        # Display Section 
        self.displayFrame.writeConfig(f)
        # Origin Section
        self.originFrame.writeConfig(f)
        # Aircraft Section
        errorMsg = self.aircraftFrame.writeAllConfig(f)
        # Volume Section
        errorMsg2 = self.volumeFrame.writeAllConfig(f)
        
        # Close file
        f.close()
        
        # Show error dialog
        errorStr = ""
        for str in errorMsg:
            errorStr+=str+'\n'
        for str in errorMsg2:
            errorStr+=str+'\n'
        if (len(errorStr)>0):
            tkMessageBox.showinfo(message=errorStr)
        
        # Show dialog
        tkMessageBox.showinfo(message="File written to %s" % filename)
        
    
def valid_0255(string):
     # Check if string is valid from 0 to 255
     result = False
     if (string.isdigit()):
         val = int(string)
         if (val>=0 and val <=255):
             result = True
             
     return result


def validateFloat(string):
    # Checks if a string is a valid float
    valid = True
    if len(string)>0:
        if (string == '-'):
            val = 0
        else:
            try:
                val = float(string)
            except ValueError:
                val = 0
                valid = False
    else:
        val = 0
                
    return valid, val
        
      
        
