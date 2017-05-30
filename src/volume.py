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

import editPoints, tools

import os, math, time

import defcolours

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
        self.root = root
        self.mainFrame = mainFrame
        self.originFrame = originFrame
        # Create Volume label
        self.volLabel = ttk.Label(self, text='VOLUMES', font=(None,16)).grid(column=0, row=0, columnspan=2, sticky=tk.W)
        # Create Add/Remove buttons
        self.addRemoveFrame = tk.Frame(self)
        self.addRemoveFrame.grid(column=7,row=0,sticky='e')
        self.addButton = tk.Button(self.addRemoveFrame,bg="green",text="+",command=self.on_add_row)
        self.addButton.grid(column=0,row=0)
        self.removeButton = tk.Button(self.addRemoveFrame,bg="red",text="-",command=self.on_remove_row)
        self.removeButton.grid(column=1,row=0) 
        # Create Polygon Name Label
        self.polyName = ttk.Label(self,text="Name").grid(column=0,row=1,sticky=tk.W)     
        # Create RGB Label
        self.rgbLabel = ttk.Label(self,text="RGB (0-255)").grid(column=1,row=1,columnspan=3)
        # Alpha Label
        self.alphaLabel = ttk.Label(self,text='Alpha (0-1)').grid(column=4,row=1)
                
        # Create Figure
        self.createFigure(root)
        
        # Create point selection radio button
        self.addPtRadio = tk.IntVar()
                
        # Polygon Rows
        self.polygonRows = [PolygonLine(self.root,self,2)] 
        
    def on_download_button(self):
        pass
        
    def close(self):
        # On Close window, stop thread
        self.downloadRunning = False
        self.showRunning = False
        self.downThread.join(0.1)
        self.showThread.join(0.1)

    def on_add_row(self):
        # Adds a row at the bottom of the current rows
        self.polygonRows.append(PolygonLine(self.root,self,len(self.polygonRows)+2))

    def on_remove_row(self):
        # Removes the last row
        if (len(self.polygonRows) > 0):
            # Remove entry information
            rowInd = self.addPtRadio.get()
            self.polygonRows[rowInd].editPointsButton.destroy()
            self.polygonRows[rowInd].radioButton.destroy()
            if (self.addPtRadio.get()==rowInd):
                if (len(self.polygonRows)>1):
                    self.addPtRadio.set(0)
            self.polygonRows[rowInd].alphaEntry.destroy()
            self.polygonRows[rowInd].bEntry.destroy()
            self.polygonRows[rowInd].gEntry.destroy()
            self.polygonRows[rowInd].rEntry.destroy()
            self.polygonRows[rowInd].nameEntry.destroy()
            # Remove Points from Polygon
            for pt in self.polygonRows[rowInd].polygon.pointList:
                pt.ptAnn.remove()
                pt.remove()
            # Remove Edit Points window if open
            if self.polygonRows[rowInd].newWindow is not None:
                self.polygonRows[rowInd].closeExitButton()

            # Remove Polygon from figure
            self.polygonRows[rowInd].polygon.set_visible(False)
            del self.polygonRows[rowInd]
            # Renumber other rows
            i = -1
            for row in self.polygonRows:
                i += 1
                row.moveRow(i+2)

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
        lat = float(self.originFrame.latVar.get())
        lon = float(self.originFrame.lonVar.get())
        alt = float(self.originFrame.altVar.get())
        head = float(self.originFrame.headVar.get())
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
                        
        # Show Canvas
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=0,row=100,columnspan=8)

        # Put old background back
        self.background = self.fig.canvas.copy_from_bbox(self.axes.bbox)
        self.fig.canvas.restore_region(self.background)
        
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
        for polyRow in self.polygonRows:
            polyRow.polygon.reDrawPolyPoints()
            
        # Redraw Canvas
        self.canvas.draw()
            
            
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
        if hasattr(self,'polygon'):
            for poly in self.polygon:
                poly.reDrawPolyPoints()
                
        # Redraw Canvas
        self.canvas.draw()
 
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
        # Take focus
        self.canvas._tkcanvas.focus_set()
        # Check to add or remove new points
        if (event.inaxes == self.axes):
            # Check for left/right click
            if (event.button == 1):
                # Left Mouse Button
                # Check if over a point
                onPoint = False
                inPoly = None
                for polyRow in self.polygonRows:
                    for pt in polyRow.polygon.pointList:
                        contains, attr = pt.contains(event)
                        if contains:
                            onPoint = True
                            inPoly = polyRow.polygon
                if (not onPoint) and (inPoly is None) :
                    if len(self.polygonRows)>0:
                        # Get current location
                        x = event.xdata
                        y = event.ydata
                        # Add new point and redaw
                        poly = self.polygonRows[self.addPtRadio.get()].polygon
                        poly.addNewPoint(DragPoint(self,self.fig,x,y,len(poly.pointList),colTuple=poly.polygonLine.colour))
                        # Add Row to Edit Points dialog if open
                        editPointsWind = poly.polygonLine.newWindow
                        if editPointsWind is not None:
                            # Add Entry Row
                            i = editPointsWind.entryRow[-1].num + 1
                            editPointsWind.entryRow.append(editPoints.EntryRow(editPointsWind,editPointsWind.frame,editPointsWind.polygonLine,i+2,i))
                            # Renumber pts
                            i = -1
                            for pt in editPointsWind.entryRow:
                                i += 1
                                pt.num = i
                                pt.labelVar.set(str(i))
                            # Update Values
                            for row in editPointsWind.entryRow:
                                row.updateFromPolygon()

            elif (event.button == 3):
                    # Right mouse button
                    # Get points mouse is over
                    pts = []
                    for polyRow in self.polygonRows:
                        for pt in polyRow.polygon.pointList:
                            contains, attr = pt.contains(event)
                            if contains:
                                pts.append([pt,polyRow])
                                                   
                    # Find current point index
                    pt = None
                    if len(pts) > 1:
                        radioVal = self.addPtRadio.get()
                        for entry in pts:
                            if (entry[1] == radioVal):
                                pt = entry
                                break
                        if (pt is None):
                            pt = pts[0]
                    elif (len(pts) == 1):
                        pt = pts[0]
                    
                    if (pt is not None):
                        poly = pt[1].polygon
                        if (len(poly.pointList)>3):
                            onPoint = None
                            for i in range(0,len(poly.pointList)):
                                contains, attr = poly.pointList[i].contains(event)
                                if contains:
                                    onPoint = i
                            # Remove current point
                            if (onPoint is not None):
                                if poly.polygonLine.newWindow is not None:
                                    entryRow = poly.polygonLine.newWindow.entryRow[onPoint]
                                    entryRow.on_remove_row()
                                    # Renumber points and move rows
                                    editPointsWind = poly.polygonLine.newWindow
                                    i = -1
                                    for row in editPointsWind.entryRow:
                                        i += 1
                                        row.move_row(i+2)
                                else:
                                    poly.removePoint(onPoint)
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
        
    def writeConfig(self,f,row,errorMsg):
        # Writes single aircraft information to file
        # Check name
        okay = True
        polygonLine = self.polygonRows[row]
        if (len(polygonLine.nameVar.get())==0):
            okay = False
            errorMsg.append("Volume name for row %i is empty!" % (row+1))
        
        if not okay:
            errorMsg.append("Skipped volume row: %i" % (row+1))
        else:
            # Write Data
            name   = polygonLine.nameVar.get()
            red    = polygonLine.rVar.get()
            green  = polygonLine.gVar.get()
            blue   = polygonLine.bVar.get()
            alpha  = polygonLine.alphaVar.get()
            numPts = len(polygonLine.polygon.pointList)
            f.write('volume "%s" %s %s %s %s %i ' % (name,red,green,blue,alpha,numPts))
            for pt in polygonLine.polygon.pointList:
                lat = pt.y
                lon = pt.x
                lowAlt  = pt.lowHeight
                highAlt = pt.highHeight
                f.write('(%f,%f,%f,%f) ' % (lat,lon,lowAlt,highAlt))
            f.write('\n')
            
        return errorMsg
        
    def writeAllConfig(self,f):
        # Writes all volume information to file
        errorMsg = []
        f.write('# Volumes\n')
        for i in range(0,len(self.polygonRows)):
            errorMsg = self.writeConfig(f,i,errorMsg)
        f.write('\n')
    
        return errorMsg
    
    
    
        
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
    def __init__(self,fig,pointList,polygonLine,colTuple):
        self.fig = fig
        self.pointList = pointList # List of drag points
        self.polygonLine = polygonLine
        self.pts = [] # [[x1,y1],[x2,y2],...[xn,yn]]
        self.polyCreated = False
        
        # Initialise first points
        self.ptsFromDragPointList()
        for pt in self.pointList:
            # Set Point connected polygon
            pt.masterPoly = self
            
        # Initialise polygon
        Polygon.__init__(self,self.pts,alpha=0.3,fc=colTuple,closed=True)
        
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
        self.pointList[ind].ptAnn.remove()
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
            oldPts[sortedInd[i][0]].id = i
            oldPts[sortedInd[i][0]].ptAnn.set_text(i)
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
    def __init__(self,masterFrame,fig,x,y,id,colTuple,masterPolygon=None):
        patches.Ellipse.__init__(self,(x,y),0.00015,0.00015,fc=colTuple,alpha=0.75,edgecolor='k')
        self.masterFrame = masterFrame
        self.fig = fig
        self.x = x
        self.y = y
        self.id = id
        self.masterPoly = masterPolygon

        # Setup Plot
        self.fig.axes[0].add_patch(self)
        self.pressed = False
        self.background = self.figure.canvas.copy_from_bbox(self.axes.bbox)
        self.connect()
        
        # Add Annotation
        self.lowHeight = 0
        self.highHeight = 10
        self.ptAnn = self.axes.annotate(str(self.id),xy=(self.x,self.y),horizontalalignment='center',verticalalignment='center',color='white')
        
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
                # Set annotation position
                self.ptAnn.set_position((self.center[0],self.center[1]))
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
                # Update Edit Points Window if open
                editFrame = self.masterPoly.polygonLine.newWindow
                if editFrame is not None:
                    ind = self.masterPoly.pointList.index(self)
                    entryRow = editFrame.entryRow[ind]
                    entryRow.moving = True
                    entryRow.latVar.set(self.y)
                    entryRow.lonVar.set(self.x)
                    entryRow.lowAltVar.set(self.lowHeight)
                    entryRow.highAltVar.set(self.highHeight)
                    entryRow.moving = False

    
    def disconnect(self):
        self.figure.canvas.mpl_disconnect(self.cidpress)
        self.figure.canvas.mpl_disconnect(self.cidrelease)
        self.figure.canvas.mpl_disconnect(self.cidmotion)
        
class PolygonLine():
    # Creates a polygon line for adjust polygon properties
    def __init__(self,root,masterFrame,row):
        self.root = root
        self.masterFrame = masterFrame
        self.row = row
        self.newWindow = None
        # Create polygon name entry box
        self.nameVar = tk.StringVar()
        self.nameEntry = tk.Entry(self.masterFrame,textvariable=self.nameVar,width=12)
        self.nameVar.set("Polygon %i" % (row-1))
        self.nameVar.trace('w',self.on_name_change)
        self.nameEntry.grid(column=0,row=row,sticky=tk.W)
        # Colour Generation
        self.colInt = row - 2
        self.origRow = self.colInt
        while (self.colInt > len(defcolours.allColours)-1):
            self.colInt -= len(defcolours.allColours)
        # RGB Entry
        self.rVar = tk.StringVar()
        self.rVar.set(defcolours.allColours[self.colInt][0])
        self.rVar.trace('w', self.on_rVar_change)
        self.rEntry = tk.Entry(self.masterFrame,textvariable=self.rVar,width=4)
        self.rEntry.grid(column=1,row=row)
        self.gVar = tk.StringVar()
        self.gVar.set(defcolours.allColours[self.colInt][1])
        self.gVar.trace('w', self.on_gVar_change)
        self.gEntry = tk.Entry(self.masterFrame,textvariable=self.gVar,width=4)
        self.gEntry.grid(column=2,row=row)
        self.bVar = tk.StringVar()
        self.bVar.set(defcolours.allColours[self.colInt][2])
        self.bVar.trace('w', self.on_bVar_change)
        self.bEntry = tk.Entry(self.masterFrame,textvariable=self.bVar,width=4)
        self.bEntry.grid(column=3,row=row)
        # Alpha Entry
        self.alphaVar = tk.StringVar()
        self.alphaVar.set(0.3)
        self.alphaVar.trace('w', self.on_alphaVar_change)
        self.alphaEntry = tk.Entry(self.masterFrame,textvariable=self.alphaVar,width=8)
        self.alphaEntry.grid(column=4,row=row)
        # Create radio button - determines which polygon a point is added to
        self.radioButton = tk.Radiobutton(self.masterFrame,text="",variable=self.masterFrame.addPtRadio,value=self.origRow)
        self.radioButton.grid(column=5,row=row)
        # Create edit points button (launches window to manually adjust points
        tkColour = '#%02x%02x%02x' % (int(self.rVar.get()),int(self.gVar.get()),int(self.bVar.get()))
        self.editPointsButton = tk.Button(self.masterFrame,text='Edit Points',bg=tkColour,command=self.on_edit_points)
        self.editPointsButton.grid(column=7,row=row,sticky=tk.E)
        
        # Create Polygon
        self.createPolygon()
        
    
    def createPolygon(self):
        # Creates a polygon for the current polygon line and adds it to the canvas
        # Create Points
        points = []
        fig = self.masterFrame.fig
        origin = self.masterFrame.origin
        self.colour = [x / 255 for x in defcolours.allColours[self.colInt]]
        points.append(DragPoint(self.masterFrame,fig,origin[1]-0.0005,origin[0]-0.0005,0,colTuple=self.colour))
        points.append(DragPoint(self.masterFrame,fig,origin[1]+0.0005,origin[0]+0.0005,1,colTuple=self.colour))
        points.append(DragPoint(self.masterFrame,fig,origin[1]+0.0005,origin[0]-0.0005,2,colTuple=self.colour))        
         
        # Create Polygon
        self.polygon = PolyArea(self.masterFrame.fig, points, self, colTuple=self.colour)
        self.polygon.set_zorder(1)
        self.masterFrame.axes.add_artist(self.polygon)

    def moveRow(self,newRow):
        # Moves the polygon line to a new row
        self.row = newRow
        # Colour Generation
        self.colInt = newRow - 2
        self.origRow = self.colInt
        while (self.colInt > len(defcolours.allColours)-1):
            self.colInt -= len(defcolours.allColours)
        # Recreate new radio button
        self.radioButton.destroy()
        self.radioButton = tk.Radiobutton(self.masterFrame,text="",variable=self.masterFrame.addPtRadio,value=self.origRow)
        self.radioButton.grid(column=5,row=newRow)
        # Move entries
        self.nameEntry.grid(column=0,row=newRow,sticky=tk.W)
        self.rEntry.grid(column=1,row=newRow)
        self.gEntry.grid(column=2,row=newRow)
        self.bEntry.grid(column=3,row=newRow)
        self.alphaEntry.grid(column=4,row=newRow)
        self.radioButton.grid(column=5,row=newRow)
        self.editPointsButton.grid(column=7,row=newRow,sticky=tk.E)

    def on_rVar_change(self,*args):
        # Red entry text box changes
        self.rgb_change(self.rVar)
       
    def on_gVar_change(self,*args):
        # Green entry text box changes
        self.rgb_change(self.gVar)

    def on_bVar_change(self,*args):
        # Blue entry text box changes
        self.rgb_change(self.bVar)
        
    def changeAlpha(self,val):
        # Change Colour
        self.polygon.set_alpha(val)
        for pt in self.polygon.pointList:
            pt.set_alpha(val)
        # Redraw
        self.polygon.reDrawPolyPoints()
        
    def on_alphaVar_change(self,*args):
        # Alpha entry text box changes
        string = self.alphaVar.get()
        if (len(string)>0):
            try:
                val = float(string)
                if (val>=0.0 and val<=1.0):
                    self.changeAlpha(val)
                else:
                    tkMessageBox.showerror(message="Alpha value must be float between 0.0 and 1.0")
                    self.alphaVar.set('0.5')
                    self.changeAlpha(0.5)

            except ValueError:
                tkMessageBox.showerror(message="Alpha value must be float between 0.0 and 1.0")
                self.alphaVar.set('0.5')
                self.changeAlpha(0.5)
                
    def changeRGB(self):
        # Change Colour
        colVec = [int(self.rVar.get())/255.0,int(self.gVar.get())/255.0,int(self.bVar.get())/255.0]
        self.polygon.set_facecolor(colVec)
        tkColour = '#%02x%02x%02x' % (int(self.rVar.get()),int(self.gVar.get()),int(self.bVar.get()))
        self.editPointsButton.configure(bg=tkColour)
        for pt in self.polygon.pointList:
            pt.set_facecolor(colVec)
        # Redraw
        self.polygon.reDrawPolyPoints()

    def rgb_change(self,var):
        # Any RGB Entry Box Changes
        # Check if entry is valid
        if (len(var.get()) > 0):
            rCheck = tools.valid_0255(self.rVar.get())
            gCheck = tools.valid_0255(self.gVar.get())
            bCheck = tools.valid_0255(self.bVar.get()) 
            if (rCheck and gCheck and bCheck):
                self.changeRGB()
            else:
                tkMessageBox.showerror(message="RGB Values must be an integer from 0 to 255!")
                var.set('0')
                self.changeRGB()
 

    def on_edit_points(self,*args):
        # Edit points manually
        self.editWindow = tk.Toplevel()
        self.editWindow.title("Edit Points: %s" % self.nameVar.get())
        self.newWindow = editPoints.EditPointsFrame(self.editWindow,self)
        # Close on Escape
        self.editWindow.bind('<Key-Escape>',self.closeEditPoints)
        # Change close function
        self.editWindow.protocol("WM_DELETE_WINDOW", self.closeExitButton)
        
    def on_name_change(self,*args):
        # On Polygon name change
        if self.newWindow is not None:
            self.editWindow.wm_title("Edit Points: %s" % self.nameVar.get())
        
    def closeEditPoints(self,event):
        # Close edit points window
        self.newWindow = None
        self.editWindow.destroy()
        
    def closeExitButton(self):
        # Close edit points window
        self.newWindow = None
        self.editWindow.destroy()
        
        