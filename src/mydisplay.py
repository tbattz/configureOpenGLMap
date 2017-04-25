''' Created by Trevor Batty
    Date: April 25th 2017
   
    Creates the display section of the GUI.
'''

import tkinter as tk
from tkinter import ttk

import subprocess as sp


class Display(ttk.Frame):   
    def __init__(self,root,mainFrame):
        # Create Display frame
        ttk.Frame.__init__(self,mainFrame,padding="3 3 3 3")
        # Create Display label
        self.dispLabel = ttk.Label(self, text="DISPLAY", font=(None,16)).grid(column=0, row=0, sticky=tk.W)
        # Create Monitor label
        self.monLabel = ttk.Label(self, text="Monitor").grid(column=0, row=1, sticky=tk.W)
        # Create Monitor selection
        self.monitors = getMonitors(root)
        self.monList = getMonitorStrings(self.monitors)
        self.varMonList = tk.StringVar()
        self.varMonList.set(self.monList[0])
        self.dropDownBox = tk.OptionMenu(self,self.varMonList,*self.monList)
        self.dropDownBox.grid(column=1, row=1, columnspan=4,sticky=tk.E)
        # Create Resolution Label
        self.resLabel = ttk.Label(self, text="Resolution").grid(column=0, row=2, sticky=tk.W)    
        # Create Resolution Entry Boxes
        self.xResEntry = tk.Entry(self,width=10)
        self.xResEntry.insert(0,self.monitors[0].currRes[0])
        self.xResEntry.grid(column=1, row=2, sticky=tk.W)
        self.yResEntry = tk.Entry(self,width=10)
        self.yResEntry.insert(0,self.monitors[0].currRes[1])
        self.yResEntry.grid(column=2, row=2, sticky=tk.W)
        # Create Fullscreen checkbox
        self.fsCheckVar = tk.IntVar()
        self.fsCheckbox = ttk.Checkbutton(self,text="Fullscreen",variable=self.fsCheckVar)
        self.fsCheckbox.grid(column=3,row=2,sticky=tk.W)
        
        

class Monitor:
    def __init__(self,port,id,currRes,currFps,mmSize):
        self.port       = port      # e.g. HDMI-0
        self.id         = id        # 0,1,2,...
        self.currRes    = currRes   # [xRes,yRes]
        self.currFps    = currFps   # e.g. 60
        self.mmSize     = mmSize    # [xmm,ymm]
        self.fullscreen = True      # True, False
        
        # Create display string
        self.dispString = "%i: %s %ix%i, %i fps, %ix%i(mm)" % (id,port,currRes[0],currRes[1],currFps,mmSize[0],mmSize[1])

def getMonitors(root):
    count = -1;
    monitors = []
        
    # Use xrandr to get all monitors and their resolution
    output = (sp.check_output('xrandr')).split('\n')
    # Parse output for monitors
    for i in range(0,len(output)):
        if " connected" in output[i]:
            count += 1
            if (count == 0):
                offset = 1
            else:
                offset = 0
            line = output[i].split()
            # Get connected port
            port = line[0]
            id = count + 1
            # Get resolution
            resString = line[2+offset]
            resString = resString[:resString.find('+')]
            resString = resString.split('x')
            currRes = [int(resString[0]),int(resString[1])]
            # Get size mm
            lineLen = len(line)
            xmm = int(line[lineLen-3][0:-2])
            ymm = int(line[lineLen-1][0:-2])
            mmSize = [xmm, ymm]
            # Get fps
            line = (output[i+1]).split()
            fps = float(line[1][:-2])
            # Create class
            monitors.append(Monitor(port,id,currRes,fps,mmSize))
            
    return monitors
            
def getMonitorStrings(monitorList):
    # Creates the string list to display from a group of monitors
    monList = []
    for mon in monitorList:
        monList.append(mon.dispString)
        
    return monList
    