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

from scipy.misc import imread
import matplotlib.cbook as cbook

import os, math, time

from threading import Thread
import urllib


def latLon2TileNum(lat, lon, zoom):
    # Converts a lat and lon to tile number
    lat_rad = math.radians(lat)
    n = math.pow(2, zoom)
    x = n * (lon + 180.0) / 360.0
    y = n * (1 - (math.log(math.tan(lat_rad) + 1.0/math.cos(lat_rad)) / math.pi)) / 2.0
    
    return [x,y]
            
def tileNum2LatLon(x, y, zoom):
    # Convert tile number to lat, lon
    n = math.pow(2,zoom)
    lat = math.atan(math.sinh(math.pi - (y*2*math.pi/n)))*180.0/math.pi
    lon = (x/n)*360.0 - 180.0
    
    return [lat,lon]


class Volume(ttk.Frame):
    def __init__(self,root,mainFrame,originFrame):
        # Create Volume frame
        ttk.Frame.__init__(self,mainFrame,padding="3 0 0 0")
        self.mainFrame = mainFrame
        self.originFrame = originFrame
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
        
    def on_download_button(self):
        pass
        
    def close(self):
        # On Close window, stop thread
        self.downloadRunning = False
        self.showRunning = False
        self.downThread.join(1)
        self.showThread.join(1)

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
        
        # Move Map Callbacks
        self.cid = self.fig.canvas.mpl_connect('key_press_event',self.on_key_pressed)
        
        # Get origin
        lat = self.originFrame.latVar.get()
        lon = self.originFrame.lonVar.get()
        alt = self.originFrame.altVar.get()
        head = self.originFrame.headVar.get()
        self.origin = [lat, lon, alt, head]
        
        # Set Axes Limits
        scale = self.latLonScale(self.origin[0])
        diff = (2*0.0025)*scale/2.0
        self.axes.set_xlim(self.origin[1]-0.0025-diff,self.origin[1]+0.0025+diff)
        self.axes.set_ylim(self.origin[0]-0.0025,self.origin[0]+0.0025)

        # Setup Maps 
        self.zoom = 18
        self.mapTiles = []
        self.loadedTiles = []
        self.downloadQueue = []
        self.toShow = []
        self.downloadSwitch = False
        self.imageFolder = "../../SatTiles/"
        
        # Load required tiles
        self.checkRequiredTiles()
        
        # Download tiles thread
        self.downloadRunning = True
        self.downThread = Thread(target=self.downloadTiles,args=())
        self.downThread.start()
        
        # Show tiles thread
        self.showRunning = True
        self.showThread = Thread(target=self.showTiles,args=())
        self.showThread.start()
        
        # Create Points
        self.points = []
        self.points.append(DragPoint(self.fig,self.origin[1]-0.0005,self.origin[0]-0.0005,colStr='b'))
        self.points.append(DragPoint(self.fig,self.origin[1]+0.0005,self.origin[0]+0.0005,colStr='b'))
        self.points.append(DragPoint(self.fig,self.origin[1]+0.0005,self.origin[0]-0.0005,colStr='b'))        
         
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
        
        # Setup callback for click-point adding
        self.fig.canvas.mpl_connect('button_press_event',self.on_canvas_pressed)
        self.fig.canvas.mpl_connect('scroll_event',self.on_scroll_wheel)
 
    def latLonScale(self,latitude):
        # Calculates the ratio of lat to lon at a given latitude
        return 110.574/(111.320*math.cos(math.radians(latitude)))
        
 
    def on_key_pressed(self,event):
        # Clear Download Queue
        self.downloadQueue = []
        self.downloadSwitch = True
        # Change axes limits
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        xdiff = (xlim[1]-xlim[0])/8.0
        ydiff = (ylim[1]-ylim[0])/8.0
        if (event.key == 'left'):
            self.axes.set_xlim(xlim-xdiff)
        elif (event.key == 'right'):
            self.axes.set_xlim(xlim+xdiff)
        elif (event.key == 'up'):
            self.axes.set_ylim(ylim+ydiff)
        elif (event.key == 'down'):
            self.axes.set_ylim(ylim-ydiff)
        elif (event.key == '-'):
            self.axes.set_xlim(xlim[0]-xdiff,xlim[1]+xdiff)
            self.axes.set_ylim(ylim[0]-ydiff,ylim[1]+ydiff)
        elif (event.key == '+'):
            self.axes.set_xlim(xlim[0]+xdiff,xlim[1]-xdiff)
            self.axes.set_ylim(ylim[0]+ydiff,ylim[1]-ydiff)
            
        # Adjust Limits
        self.checkLimits()
        
        # Check Tiles
        self.checkRequiredTiles()
            
        # Redraw
        self.polygon[0].reDrawPolyPoints()
            
    def on_scroll_wheel(self,event):
        # Clear Download Queue
        self.downloadQueue = []
        self.downloadSwitch = True
        # Change axes zoom level
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        xdiff = (xlim[1]-xlim[0])/8.0
        ydiff = (ylim[1]-ylim[0])/8.0
        if (event.button == 'up'):
            self.axes.set_xlim(xlim[0]+xdiff,xlim[1]-xdiff)
            self.axes.set_ylim(ylim[0]+ydiff,ylim[1]-ydiff)
        elif (event.button == 'down'):
            self.axes.set_xlim(xlim[0]-xdiff,xlim[1]+xdiff)
            self.axes.set_ylim(ylim[0]-ydiff,ylim[1]+ydiff)
            
        # Adjust Limits
        self.checkLimits()
        
        # Check Tiles
        self.checkRequiredTiles()
        
        # Redraw
        self.polygon[0].reDrawPolyPoints()
 
    def checkLimits(self):
        # Checks if the axes limits are bound to the correct range for lat, lon
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        xmin = xlim[0]
        xmax = xlim[1]
        ymin = ylim[0]
        ymax = ylim[1]
        if (xmin < -180):
            xmin = 180
        if (xmax > 180):
            xmax = 180
        if (ymin < -90):
            ymin = -90
        if (ymax > 90):
            ymax = 90
        self.axes.set_xlim(xmin,xmax)
        self.axes.set_ylim(ymin,ymax)
 
    def on_canvas_pressed(self,event):
        # Check to add or remove new points
        if (event.inaxes == self.axes):
            # Check for left/right click
            if (event.button == 1):
                # Left Mouse Button
                # Check if over a point
                onPoint = False
                for pt in self.polygon[0].pointList:
                    contains, attr = pt.contains(event)
                    if contains:
                        onPoint = True
                if not onPoint:
                    # Get current location
                    x = event.xdata
                    y = event.ydata
                    # Add new point and redaw
                    self.polygon[0].addNewPoint(DragPoint(self.fig,x,y,colStr='b'))

            elif (event.button == 3):
                    # Right mouse button
                    # Find current point index
                    if (len(self.polygon[0].pointList)>3):
                        onPoint = None
                        for i in range(0,len(self.polygon[0].pointList)):
                            contains, attr = self.polygon[0].pointList[i].contains(event)
                            if contains:
                                onPoint = i
                        # Remove current point
                        if (onPoint is not None):
                            self.polygon[0].removePoint(onPoint)
                    else:
                        tkMessageBox.showerror(message='Cannot remove point. Minimum number of points for polygon: 3')
    
    def downloadTiles(self):
        # Function to be threaded to download tiles
        while self.downloadRunning:
            for tile in reversed(self.downloadQueue):
                if not self.downloadSwitch:
                    if tile not in self.loadedTiles:
                        # Download tile
                        mapTile = MapTile(self,self.imageFolder,self.axes,tile[0],tile[1],tile[2])
                        mapTile.downloadTile()
                        self.loadedTiles.append(tile)
                        self.mapTiles.append(mapTile)
                        if tile in self.downloadQueue:
                            self.downloadQueue.remove(tile)
                            
                        # Redraw Canvas
                        self.fig.canvas.draw()
                else:            
                    self.downloadSwitch = False
                
                
            time.sleep(0.5)
        
    def showTiles(self):
        # Function to be threaded to show tiles
        loaded = []
        while self.showRunning:
            for tile in self.toShow:
                if tile not in loaded:
                    tile.showTile()
                    loaded.append(tile)
            time.sleep(1.0)
    
    def checkRequiredTiles(self):
        # Checks if the required tiles are loaded, if not, loads them
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        # Lower bounds
        [x1,y1] = latLon2TileNum(ylim[0], xlim[0], self.zoom)
        [x2,y2] = latLon2TileNum(ylim[1], xlim[1], self.zoom)
        xmin = int(math.floor(min(x1,x2)))
        xmax = int(math.ceil(max(x1,x2)))
        ymin = int(math.floor(min(y1,y2)))
        ymax = int(math.ceil(max(y1,y2)))
        x = range(xmin,xmax)
        y = range(ymin,ymax)
        # Load required tiles if they are on disk and not yet loaded
        for i in x:
            for j in y:
                # Check if already loaded or downloaded
                if (i,j,self.zoom) not in self.downloadQueue:
                    if (i,j,self.zoom) not in self.loadedTiles:
                        # If file exists, load it
                        imagePath = "%s%i-%i-%i.png" % (self.imageFolder,self.zoom,i,j)
                        if os.path.isfile(imagePath):
                            # Load tile
                            self.loadedTiles.append((i,j,self.zoom))
                            self.mapTiles.append(MapTile(self,self.imageFolder,self.axes,i,j,self.zoom))
                        else:
                            if (i,j,self.zoom) not in self.downloadQueue:
                                self.downloadQueue.append((i,j,self.zoom))             
    
    
        
class MapTile():
    # The image for a map tile
    def __init__(self,master,imageFolder,axes,x,y,zoom):
        self.master = master
        self.imageFolder = imageFolder      # Requires trailing slash
        self.axes = axes
        self.x = x
        self.y = y
        self.zoom = zoom
        self.tileID = (self.x,self.y,self.zoom)
        self.imagePath = "%s%i-%i-%i.png" % (self.imageFolder,self.zoom,self.x,self.y)
        self.loaded = False
        # Calculate Top Left and Bottom Right lat, lons
        [self.latTL, self.lonTL] = tileNum2LatLon(self.x, self.y, self.zoom)
        [self.latBR, self.lonBR] = tileNum2LatLon(self.x+1, self.y+1, self.zoom)
        
        # Load image data
        if os.path.isfile(self.imagePath):
            self.showTile()
            self.loaded = True
        else:
            self.loaded = False
        
    def showTile(self):
        # Calculates the extent for the current window
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        self.extents = [self.lonTL,self.lonBR,self.latBR,self.latTL]
        # Plot Tile
        while 1:
            try:
                self.img = plt.imread(self.imagePath)
                break
            except RuntimeError:
                time.sleep(0.2)
        self.axes.imshow(self.img,zorder=0,extent=self.extents,aspect='auto')
        # Reset axes limits
        self.axes.set_xlim(xlim)
        self.axes.set_ylim(ylim)
        
    def downloadTile(self):
        # Function to download a tile 
        url = "http://maptile.maps.svc.ovi.com/maptiler/v2/maptile/newest/hybrid.day/%i/%i/%i/256/png8" % (self.zoom,math.floor(self.x),math.floor(self.y))
        filename = "../../SatTiles/%i-%i-%i.png" % (self.zoom,math.floor(self.x),math.floor(self.y))
        print filename
        urllib.urlretrieve(url, filename)
        # Show Tile
        self.master.loadedTiles.append((self.x,self.y,self.zoom))
        self.master.toShow.append(self)
        

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
        Polygon.__init__(self,self.pts,alpha=0.5,closed=True)
        
        # Add poly to axes
        self.fig.axes[0].add_patch(self)

    def ptsFromDragPointList(self):
        # Generates the list of points from the drag points list
        self.pts = []
        for drgPt in self.pointList:
            if drgPt != []:
                self.pts.append([drgPt.x,drgPt.y])
            
    def addNewPoint(self,dragPoint):
        # Adds a drag point to the polygon
        self.pointList.append(dragPoint)
        self.pointList[-1].masterPoly = self
        # Sort points to create non-intersecting polygon
        self.resortPts()
            
        # Redraw
        self.reDrawPolyPoints()
        
    def removePoint(self,ind):
        # Removes a point given the index in self.pointList
        self.pointList[ind].remove()
        del self.pointList[ind]
        # Redraw
        self.reDrawPolyPoints()
            
    def reDrawPolyPoints(self):
        # Redraw Polygon
        self.updatePoints() 
        # Put old background back
        self.background = self.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.figure.canvas.restore_region(self.background)
        self.axes.draw_artist(self)
        # Redraw all points
        for pt in self.pointList:
                pt.axes.draw_artist(pt)
        # Redraw Canvas
        self.figure.canvas.draw()

        
    def updatePoints(self):
        # Reparses the DragPoints and updates the polygon
        self.ptsFromDragPointList()
        self.set_xy(self.pts)

    def resortPts(self):
        # Resorts points to create a non-intersecting polygon
        # Calculate center
        center = [sum([pt.x for pt in self.pointList])/len(self.pointList),sum([pt.y for pt in self.pointList])/len(self.pointList)]
        # Use polar angle to sort points
        angle = []
        for pt in self.pointList:
            angle.append(math.atan2(pt.y-center[1],pt.x-center[0]))
        sortedInd = sorted(enumerate(angle), key=lambda x:x[1])
        # Reorder 
        oldPts = self.pointList
        self.pointList = []
        for i in range(0,len(oldPts)):
            self.pointList.append(oldPts[sortedInd[i][0]])
        

    def calcAngle(self,x1,y1,x2,y2,x3,y3):
        # Calculates the angle between the lines joining pt3 to the other two points.
        # Calculate distances
        a = math.sqrt((x2-x3)**2 + (y2-y3)**2)
        b = math.sqrt((x1-x3)**2 + (y1-y3)**2)
        c = math.sqrt((x1-x2)**2 + (y1-y2)**2)
        # Apply cosine rule
        C = math.acos((a**2 + b**2 - c**2)/(2*a*b))
        return C 

class DragPoint(patches.Ellipse):
    # Create lock that only one instance can hold at a time
    lock = None
    # A point that can be dragged with the mouse
    def __init__(self,fig,x,y,colStr='b',masterPolygon=None):
        patches.Ellipse.__init__(self,(x,y),0.00015,0.00015,fc=colStr,alpha=0.75,edgecolor='k')
        self.fig = fig
        self.x = x
        self.y = y
        self.masterPoly = masterPolygon

        # Setup Plot
        self.fig.axes[0].add_patch(self)
        self.pressed = False
        self.background = self.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.connect()
        
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
                # Move stored point position
                self.x = self.center[0]
                self.y = self.center[1]
                # Resort points
                self.masterPoly.resortPts()
                # Redraw Polygon
                if self.masterPoly is not None:
                    self.masterPoly.updatePoints() 
                    self.masterPoly.fig.canvas.draw()
                    self.axes.draw_artist(self.masterPoly)
                # Redraw all points
                if self.masterPoly is not None:
                    for pt in self.masterPoly.pointList:
                        pt.axes.draw_artist(pt)
                self.axes.draw_artist(self)

    
    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cidpress)
        self.figure.canvas.mpl_disconnect(self.cidrelease)
        self.figure.canvas.mpl_disconnect(self.cidmotion)
        