'''Created by Trevor Batty
    Date: May 9th 2017
    
    Creates the volumne section of the GUI.
'''

import tkinter as tk
from tkinter import ttk
import tkMessageBox

import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler
import matplotlib.patches as patches
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection

from matplotlib.figure import Figure


class Volume(ttk.Frame):
    def __init__(self,root,mainFrame):
        # Create Volume frame
        ttk.Frame.__init__(self,mainFrame,padding="3 0 0 0")
        # Create Volume label
        self.volLabel = ttk.Label(self, text='VOLUMES', font=(None,16)).grid(column=0, row=0, sticky=tk.W)
        # Create Add/Remove buttons
        self.addRemoveFrame = tk.Frame(self)
        self.addRemoveFrame.grid(column=3,row=0,sticky='e')
        self.addButton = tk.Button(self.addRemoveFrame,bg="green",text="+",command=self.on_add_row)
        self.addButton.grid(column=0,row=0)
        self.removeButton = tk.Button(self.addRemoveFrame,bg="red",text="-",command=self.on_remove_row)
        self.removeButton.grid(column=1,row=0)        
        # Create Figure
        self.createFigure(root)

    def on_add_row(self):
        # Adds a row at the bottom of the current rows
        pass

    def on_remove_row(self):
        # Removes the last row
        pass

    def createFigure(self,root):
        # Creates a matplotlib figure
        self.fig, self.axes = plt.subplots()  
        self.fig.tight_layout()
        self.fig.set_figheight(4)
        self.fig.set_figwidth(5.23)
        self.axes.axis('off')
        plt.subplots_adjust(left=0.0,right=1.0,bottom=0.0,top=1.0)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        
        # Create Points
        self.points = []
        self.points.append(DragPoint(self.fig,0.5,0.5,colStr='b'))
        self.points.append(DragPoint(self.fig,0.75,0.75,colStr='b'))
        self.points.append(DragPoint(self.fig,1.0,0.0,colStr='b'))
         
        # Create Polygon
        self.polygon = [PolyArea(self.fig, self.points, colStr='b')]
                
        # Add Patches 
        self.patchCollection = PatchCollection(self.polygon,alpha=0.5)
        self.patchCollection.set_zorder(1)
        self.axes.add_collection(self.patchCollection)
        
        # Show Canvas
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=0,row=1,columnspan=4)

        # Put old background back
        self.background = self.fig.canvas.copy_from_bbox(self.axes.bbox)
        self.fig.canvas.restore_region(self.background)

        # Redraw points to appear on top of polygon
        for pt in self.points:
            pt.set_zorder(2)
            self.axes.draw_artist(pt)
        
            
            

class PolyArea(Polygon):
    # The polygon defining an area on the map
    def __init__(self,fig,pointList,colStr='b'):
        self.fig = fig
        self.pointList = pointList # List of drag points
        self.pts = [] # [[x1,y1],[x2,y2],...[xn,yn]]
        self.polyCreated = False
        
        # Initialise first points
        self.ptsFromDragPointList()
        for pt in self.pointList:
            # Set Point connected polygon
            pt.masterPoly = self
            
        # Initialise polygon
        Polygon.__init__(self,self.pts,closed=True)
        
        # Add poly to axes
        self.fig.axes[0].add_patch(self)

    def ptsFromDragPointList(self):
        # Generates the list of points from the drag points list
        self.pts = []
        for drgPt in self.pointList:
            if drgPt != []:
                self.pts.append([drgPt.x,drgPt.y])
            
    def addPoint(self,dragPoint):
        # Adds a drag point to the polygon
        self.pointList.append(dragPoint)
        self.ptsFromDragPointList()
        if self.polyCreated:
            # Update x,y points
            self.set_xy(self.pts)
        
    def updatePoints(self):
        # Reparses the DragPoints and updates the polygon
        self.ptsFromDragPointList()
        self.set_xy(self.pts)
            

class DragPoint(patches.Ellipse):
    # Create lock that only one instance can hold at a time
    lock = None
    # A point that can be dragged with the mouse
    def __init__(self,fig,x,y,colStr='b',masterPolygon=None):
        patches.Ellipse.__init__(self,(x,y),0.03,0.03,fc=colStr,alpha=0.75,edgecolor='k')
        self.fig = fig
        self.x = x
        self.y = y
        self.masterPoly = masterPolygon

        # Setup Plot
        self.fig.axes[0].add_patch(self)
        self.pressed = False
        self.background = self.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.connect()
        
    def add2Polygon(self,polygon):
        # Adds the point to a polygon
        self.masterPoly = polygon
        self.masterPoly.addPoint(self)
    
    def connect(self):
        # Connects to the required events
        self.cidpress = self.figure.canvas.mpl_connect('button_press_event',self.on_pressed)
        self.cidrelease = self.figure.canvas.mpl_connect('button_release_event',self.on_released)
        self.cidmotion = self.figure.canvas.mpl_connect('motion_notify_event',self.on_moved)
        
    def on_pressed(self,event):
        # When point is clicked
        if (event.inaxes == self.axes):
            if (DragPoint.lock==None):
                contains, attr = self.contains(event)
                if contains:
                    self.pressed = self.center, event.xdata, event.ydata
                    DragPoint.lock = self


    def on_released(self, event):
        # When point is released
        if (DragPoint.lock == self):
            self.pressed = False
            DragPoint.lock = None

            
    def on_moved(self,event):
        # Point is in motion
        if (DragPoint.lock == self):
            if (event.inaxes == self.axes):
                self.center = self.pressed[0]
                # Get center location
                xpress = self.pressed[1]
                ypress = self.pressed[2]
                # Get click location
                dx = event.xdata - xpress
                dy = event.ydata - ypress
                # Set new center
                self.center = (self.center[0]+dx,self.center[1]+dy)
                # Put old background back
                self.figure.canvas.restore_region(self.background)
                # Redraw Polygon
                if self.masterPoly is not None:
                    self.masterPoly.updatePoints() 
                    self.masterPoly.fig.canvas.draw()
                    self.axes.draw_artist(self.masterPoly)
                # Redraw all points
                if self.masterPoly is not None:
                    for pt in self.masterPoly.pointList:
                        print pt
                        pt.axes.draw_artist(pt)
                self.axes.draw_artist(self)
                # Move stored point position
                self.x = self.center[0]
                self.y = self.center[1]
                # Blit area
                self.figure.canvas.blit(self.axes.bbox)
    
    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cidpress)
        self.figure.canvas.mpl_disconnect(self.cidrelease)
        self.figure.canvas.mpl_disconnect(self.cidmotion)
        