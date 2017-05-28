''' Created by Trevor Batty
    Date: May 19th 2017
   
    Creates a window to edit the coordinates of the polygon.
'''

import tkinter as tk
from tkinter import ttk
import tkMessageBox

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
            self.entryRow.append(EntryRow(self,self.frame,self.polygonLine,i+2,i))


class EntryRow:
    # Creates an row of entry boxes
    def __init__(self,master,frame,polygonLine,row,num):
        self.master = master
        self.frame = frame
        self.polygonLine = polygonLine
        self.row = row
        self.num = num
        self.firstLoad = True
        self.moving = False
        # Create point number label
        self.labelVar = tk.StringVar()
        self.labelVar.set(str(num))
        self.ptLabel = ttk.Label(self.frame,textvariable=self.labelVar)
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
        # Add traces
        self.latVar.trace('w',self.on_lat_change)
        self.lonVar.trace('w',self.on_lon_change)
        self.lowAltVar.trace('w',self.on_lowAlt_change)
        self.highAltVar.trace('w',self.on_highAlt_change)
        
        self.updateFromPolygon()
        
        self.firstLoad = False
        
    def updateFromPolygon(self):
        # Updates the entry values from the polygon values
        self.latVar.set(self.polygonLine.polygon.pointList[self.num].y)
        self.lonVar.set(self.polygonLine.polygon.pointList[self.num].x)
        self.lowAltVar.set(self.polygonLine.polygon.pointList[self.num].lowHeight)
        self.highAltVar.set(self.polygonLine.polygon.pointList[self.num].h)
        
    def on_remove_row(self):
        # Remove row and point
        if len(self.polygonLine.polygon.pointList)>3:
            # Remove entry information
            self.removeButton.destroy()
            self.highAltEntry.destroy()
            self.lowAltEntry.destroy()
            self.lonEntry.destroy()
            self.latEntry.destroy()
            self.ptLabel.destroy()
            # Remove point from polygon
            self.polygonLine.polygon.removePoint(self.num)
            # Renumber pts
            i = -1
            for pt in self.master.entryRow:
                if (i != self.num):
                    i += 1
                    pt.num = i
                    pt.labelVar.set(str(i))
            # Remove Entry Row
            self.master.entryRow.remove(self)
        else:
            tkMessageBox.showerror(message='Cannot remove point. Minimum number of points for polygon: 3')
    
    def move_row(self,newRow):
        # Move row
        self.row = newRow
        self.num = newRow - 2
        self.labelVar.set(str(self.num))
        self.ptLabel.grid(column=0,row=newRow)
        self.latEntry.grid(column=1,row=newRow)
        self.lonEntry.grid(column=2,row=newRow)
        self.lowAltEntry.grid(column=3,row=newRow)
        self.highAltEntry.grid(column=4,row=newRow)
        self.removeButton.grid(column=5,row=newRow)
    
    def on_lat_change(self,*args):
        if (not self.firstLoad) and (not self.moving):
            # Lat Entry changes
            point = self.polygonLine.polygon.pointList[self.num]
            lat = float(self.latVar.get())
            lon = float(self.lonVar.get())
            # Set values
            point.y = lat
            point.center = lon, lat
            point.heightAnn.set_position((lon,lat))
            # Redraw
            self.polygonLine.polygon.reDrawPolyPoints()
    
    def on_lon_change(self,*args):
        if (not self.firstLoad) and (not self.moving):
            # Lon Entry changes
            point = self.polygonLine.polygon.pointList[self.num]
            lat = float(self.latVar.get())
            lon = float(self.lonVar.get())
            # Set values
            point.x = lon
            point.center = lon, lat
            point.heightAnn.set_position((lon,lat))
            # Redraw
            self.polygonLine.polygon.reDrawPolyPoints()
        
    def on_lowAlt_change(self,*args):
        if (not self.firstLoad) and (not self.moving):
            # Low Alt Entry changes
            self.polygonLine.polygon.pointList[self.num].lowHeight = float(self.lowAltVar.get())
                
    def on_highAlt_change(self,*args):
        if (not self.firstLoad) and (not self.moving):
            # High Alt Entry changes
            self.polygonLine.polygon.pointList[self.num].h = float(self.highAltVar.get())
            self.polygonLine.polygon.pointList[self.num].heightAnn.set_text(self.highAltVar.get())
            # Redraw
            self.polygonLine.polygon.reDrawPolyPoints()
            
    
