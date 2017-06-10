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
import tkFileDialog





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
        # Loads the config file
        filename = tkFileDialog.askopenfilename(defaultextension=".txt",title="Load Configuration",initialdir="../../Configs/",filetypes=(("Configuration Files","*.txt"),))
        if len(filename)>0:
            self.parseConfig(filename)
        
    def on_save_config(self):
        f = tkFileDialog.asksaveasfile(mode='w',defaultextension=".txt",title="Save Configuration",initialdir='../../Configs/',filetypes=(("Configuration Files","*.txt"),))
        if f is not None:
            # Write File
            self.write_file(f)
    
    def on_gen_config(self):
        # Generates the current configuration
        filename = 'currentConfig.txt'
        directory = '../../Configs/'
        # Check Config directory exists
        if not os.path.isdir(directory):
            os.mkdir(directory)
        # Open File
        f = open(directory + filename,'w')
        # Write File
        self.write_file(f)

    def write_file(self,f):
        # Writes the current config to file
        # Print Header
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
        tkMessageBox.showinfo(message="File written to %s" % f.name)
        
    def parseConfig(self,filename):
        # Parses the config file
        # Open File
        f = open(filename)
        # Remove all current aircraft rows
        for i in range(0,len(self.aircraftFrame.name)):
            self.aircraftFrame.removeRow()
        # Remove all volumes
        for i in range(0,len(self.volumeFrame.polygonRows)):
            self.volumeFrame.on_remove_row()
        # Counters
        aircraftNum = 0
        volumeNum = -1
        # Parse File
        line = f.readline()
        while len(line)>0:
            lineSplit = line.split()
            if len(lineSplit)>0:
                if lineSplit[0][0]!='#':
                    if lineSplit[0]=='screenID':
                        if len(lineSplit)!=3:
                            print "Incorrect screenID definition: %s" % line
                        else:
                            if int(lineSplit[2])>len(self.displayFrame.monList):
                                print "Screen number is larger than the current number of screens. Setting to zero."
                                self.displayFrame.varMonList.set(self.displayFrame.monList[0])
                            else:
                                self.displayFrame.varMonList.set(self.displayFrame.monList[int(lineSplit[2])-1])
                    elif lineSplit[0]=='yRes':
                        if len(lineSplit)!=3:
                            print "Incorrect yRes definition: %s" % line
                        else:
                            self.displayFrame.yResVar.set(int(lineSplit[2]))
                    elif lineSplit[0]=='xRes':
                        if len(lineSplit)!=3:
                            print "Incorrect xRes definition: %s" % line
                        else:
                            self.displayFrame.xResVar.set(int(lineSplit[2]))
                    elif lineSplit[0]=='fullscreen':
                        if len(lineSplit)!=3:
                            print "Incorrect fullscreen definition: %s" % line
                        else:
                            self.displayFrame.fsCheckVar.set(int(lineSplit[2]))
                    elif lineSplit[0]=='origin':
                        if len(lineSplit)!=5:
                            print "Incorrect origin definition: %s" % line
                        else:
                            self.originFrame.latVar.set(lineSplit[1])
                            self.originFrame.lonVar.set(lineSplit[2])
                            self.originFrame.altVar.set(lineSplit[3])
                            self.originFrame.headVar.set(lineSplit[4])
                    elif lineSplit[0]=='aircraft':
                        if len(lineSplit)!=5:
                            print "Incorrect aircraft definition: %s" % line
                        else:
                            aircraftNum += 1
                            self.aircraftFrame.addRow()
                            self.aircraftFrame.name[aircraftNum-1].set(lineSplit[1])
                            self.aircraftFrame.filename[aircraftNum-1] = lineSplit[2]
                            self.aircraftFrame.loadFile(aircraftNum-1,dialog=False)
                            self.aircraftFrame.ip[aircraftNum-1].set(lineSplit[3])
                            self.aircraftFrame.port[aircraftNum-1].set(lineSplit[4])
                    elif lineSplit[0]=='volume':
                        # Add Row
                        self.volumeFrame.on_add_row()
                        volumeNum += 1
                        # Setup row
                        self.volumeFrame.polygonRows[volumeNum].nameVar.set(lineSplit[1])
                        self.volumeFrame.polygonRows[volumeNum].rVar.set(lineSplit[2])
                        self.volumeFrame.polygonRows[volumeNum].gVar.set(lineSplit[3])
                        self.volumeFrame.polygonRows[volumeNum].bVar.set(lineSplit[4])
                        self.volumeFrame.polygonRows[volumeNum].alphaVar.set(lineSplit[5])
                        numPts = int(lineSplit[6])
                        poly = self.volumeFrame.polygonRows[volumeNum].polygon
                        # Change positions of first three points
                        for i in range(0,3):
                            # Parse Point
                            poly.removePoint(0)
                        # Add pts (after first three)
                        for i in range(0,numPts):
                            # Parse Point
                            pt = lineSplit[7+i]
                            ptS = pt[1:-1].split(',')
                            x = float(ptS[1]) # Lon
                            y = float(ptS[0]) # Lat
                            lowAlt = float(ptS[2])
                            highAlt = float(ptS[3])
                            self.volumeFrame.addPoint(poly,x,y,lowAlt=lowAlt,highAlt=highAlt)
                        # Resort Points
                        poly.resortPts()
                        # Redraw Polygon
                        poly.updatePoints()
                        poly.reDrawPolyPoints()
                        poly.fig.canvas.draw()
                        # Redraw points
                        for pt in poly.pointList:
                            pt.axes.draw_artist(pt)
                                                   
                    else:
                        print "Unable to parse line:"
                        print line                  
            
            line = f.readline()
        # Close File
        f.close()
        # Dialog
        tkMessageBox.showinfo(message="Loaded file %s" % filename)
    
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
        
      
        
