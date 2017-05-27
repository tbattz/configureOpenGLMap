''' Created by Trevor Batty
    Date: May 19th 2017
   
    Creates a window to edit the coordinates of the polygon.
'''

import tkinter as tk
from tkinter import ttk

class EditPointsFrame:
    # Frame to edit coordinates of the polygon
    def __init__(self,master,polygonLine):
        self.master = master
        self.polygonLine = polygonLine
        self.frame = ttk.Frame(self.master)
        self.frame.grid(column=0,row=0)
        # Create labels
        self.ptNumLabel = ttk.Label(self.frame,text="Point Num").grid(column=0,row=0,padx=5,sticky=tk.W)
        self.latLabel = ttk.Label(self.frame,text="Latitude (deg)").grid(column=1,row=0,padx=5,sticky=tk.W)
        self.lonLabel = ttk.Label(self.frame,text="Longitude (deg)").grid(column=2,row=0,padx=5,sticky=tk.W)
        self.lowAltLabel = ttk.Label(self.frame,text="Low Altitude (m)").grid(column=3,row=0,padx=5,sticky=tk.W)
        self.highAltLabel = ttk.Label(self.frame,text="High Altitude (m)").grid(column=4,row=0,padx=5,sticky=tk.W)
        self.removeLabel = ttk.Label(self.frame,text="Remove pt").grid(column=5,row=0,padx=4,sticky=tk.W)
        # Separator Line
        ttk.Separator(self.frame,orient=tk.HORIZONTAL).grid(column=0,row=1,columnspan=6,sticky='ew')

        # Create initial rows
        self.fillInitialRows()

    def fillInitialRows(self):
        # Creates the initial rows of entry boxes
        self.entryRow= []
        for i in range(0,len(self.polygonLine.polygon.pointList)):
            self.entryRow.append(EntryRow(self.frame,self.polygonLine,i+2,i))


class EntryRow:
    # Creates an row of entry boxes
    def __init__(self,frame,polygonLine,row,num):
        self.frame = frame
        self.polygonLine = polygonLine
        self.row = row
        self.num = num
        # Create point number label
        self.ptLabel = ttk.Label(self.frame,text=str(num))
        self.ptLabel.grid(column=0,row=row)
        # Create Entry rows
        self.latVar = tk.StringVar()
        self.latEntry = tk.Entry(self.frame,textvariable=self.latVar,width=10)
        self.latEntry.grid(column=1,row=row)
        self.lonVar = tk.StringVar()
        self.lonEntry = tk.Entry(self.frame,textvariable=self.lonVar,width=10)
        self.lonEntry.grid(column=2,row=row)
        self.lowAltVar = tk.StringVar()
        self.lowAltEntry = tk.Entry(self.frame,textvariable=self.lowAltVar,width=10)
        self.lowAltEntry.grid(column=3,row=row)
        self.highAltVar = tk.StringVar()
        self.highAltEntry = tk.Entry(self.frame,textvariable=self.highAltVar,width=10)       
        self.highAltEntry.grid(column=4,row=row)
        self.removeButton = tk.Button(self.frame,bg="red",text="-",command=self.on_remove_row)
        self.removeButton.grid(column=5,row=row)
        
    def updateFromPolygon(self):
        # Updates the entry values from the polygon values
        self.latVar.set(self.polygonLine)
    
    def on_remove_row(self):
        # Remove row and point
        pass
        