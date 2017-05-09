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
        fig, axes = plt.subplots()  
        fig.tight_layout()
        fig.set_figheight(4)
        fig.set_figwidth(5.23)
        axes.axis('off')
        plt.subplots_adjust(left=0.0,right=1.0,bottom=0.0,top=1.0)
        x = [1,2,3,4]
        y = [1,4,9,16]

        axes.plot(x,y,'o-')

        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=0,row=1,columnspan=4)

        