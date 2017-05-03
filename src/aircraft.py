''' Created by Trevor Batty
    Date: April 28th 2017
   
    Creates the display section of the GUI.
'''

import tkinter as tk
from tkinter import ttk, filedialog
import tkMessageBox


class Aircraft(ttk.Frame):   
    def __init__(self,root,mainFrame):
        # Create Aircraft frame
        ttk.Frame.__init__(self,mainFrame,padding="3 3 3 3")
        # Create AIRCRAFT label
        self.dispLabel = ttk.Label(self, text="AIRCRAFT", font=(None,16)).grid(column=0, row=0, sticky=tk.W)
        # Create Table titles label
        self.monLabel = ttk.Label(self, text="Aircraft Name").grid(column=0, row=1, sticky=tk.W, padx=5)
        self.pathLabel = ttk.Label(self, text="Model Path").grid(column=1,row=1, sticky=tk.W, padx=5)
        self.ipLabel = ttk.Label(self, text="Socket IP").grid(column=2,row=1, sticky=tk.W, padx=5)
        self.portLabel = ttk.Label(self, text="Socket Port").grid(column=3,row=1, sticky=tk.W, padx=5)
	# Create Add/Remove buttons
	self.addRemoveFrame = tk.Frame(self)
	self.addRemoveFrame.grid(column=3,row=0)
	self.addButton = tk.Button(self.addRemoveFrame,bg="green",text="+",command=self.on_add_row)
	self.addButton.grid(column=0,row=0)
	self.removeButton = tk.Button(self.addRemoveFrame,bg="red",text="-",command=self.on_remove_row)
	self.removeButton.grid(column=1,row=0)        
        # Create Row(s)
	self.name = []
	self.nameEntry = []
	self.button = []
	self.filename = []
	self.fileLabel = []
	self.ip = []
	self.ipEntry = []
	self.port = []
	self.portEntry = []
        row=2
	self.addRow()


    def addRow(self):
	# Adds a row at the bottom of the current rows
        # Create Aircraft Name Entry
        self.name.append(tk.StringVar())
	row = len(self.name)-1
        self.nameEntry.append(tk.Entry(self,textvariable=self.name[row],width=10))
        self.nameEntry[row].grid(column=0,row=row+1,sticky=tk.W, padx=5)
        # Create Model path selection
        self.button.append(ttk.Button(self, text="Select file", command= lambda: self.loadFile(row)))
        self.button[row].grid(column=1,row=row+1,sticky=tk.W, padx=5)
	self.filename.append("")
	self.fileLabel.append("")
        # Create Socket IP Entry
        self.ip.append(tk.StringVar())
        self.ipEntry.append(tk.Entry(self,textvariable=self.ip[row],width=10))
        self.ipEntry[row].grid(column=2,row=row+1,sticky=tk.W, padx=5)
        # Create Port Entry
        self.port.append(tk.StringVar())
        self.portEntry.append(tk.Entry(self,textvariable=self.port[row],width=10))
        self.portEntry[row].grid(column=3,row=row+1,sticky=tk.W, padx=5)
	# Set initial values
        self.name[row].set('Aircraft_'+str(row))
        self.ip[row].set("192.168.1."+str(row))
        self.port[row].set(str(14550+row))

    def removeRow(self):
	# Removes the last row
	if len(self.name) > 1:
	    del self.name[-1]
	    self.nameEntry[-1].destroy()
	    del self.nameEntry[-1]
	    self.button[-1].destroy()
	    del self.button[-1]
	    del self.filename[-1]
	    del self.fileLabel[-1]
	    del self.ip[-1]
	    self.ipEntry[-1].destroy()
	    del self.ipEntry[-1]
	    del self.port[-1]
	    self.portEntry[-1].destroy()
	    del self.portEntry[-1]

    def loadFile(self,row):
        # Opens the file load dialog window
        self.filename[row] = filedialog.askopenfilename(filetypes=(("Object files","*.obj"),("All files","*.*")),initialdir="../../Models/")
        
        # Cut filename if in models folder
        if "/Models/" in self.filename[row]:
            pos = self.filename[row].find("/Models/")
            self.fileLabel[row] = self.filename[row][pos:]
        else:
            self.fileLabel[row] = self.filename[row]
        
        # Set Button Label
        self.button[row].config(text=self.fileLabel[row])
        
    def on_add_row(self):
        self.addRow()

    def on_remove_row(self):
	self.removeRow()
        
    def writeConfig(self,f,row):
	# Writes single aircraft information to file
	# Check aircraft	
	okay = True
	if (len(self.name[row].get())<1):
		okay = False
	 	tkMessageBox.showerror(message="Aircraft name is empty!: Row %i" % (row+1))
	if (self.fileLabel[row] == ""):
		okay = False
		tkMessageBox.showerror(message="No file selected for aircraft!: Row %i" % (row+1))
	if not self.checkIP(self.ip[row].get()):
		okay = False
		tkMessageBox.showerror(message="Invalid IP Address for aircraft!: Row %i" % (row+1))
	port = self.portEntry[row].get()
	if not port.isdigit():
		okay = False
		tkMessageBox.showerror(message="Invalid port number! Aircraft row: %i\nPort number must be from 1024 to 49151." % (row+1))			
	else:
		portInt = int(port)
		if (portInt<1024) or (portInt>49151):
			okay = False
			tkMessageBox.showerror(message="Invalid port number! Aircraft row: %i\nPort number must be from 1024 to 49151" % (row+1))
	
	if not okay:
		tkMessageBox.showerror(message="Skipped aircraft row: %i" % (row+1))	


    def writeAllConfig(self,f):
	# Writes all aircraft to file
	for i in range(0,len(self.name)):
		self.writeConfig(f,i)
        
    def checkIP(self,ipStr):
	# Checks if string is a valid IPV4 address
	splt = ipStr.split(".")
	good = True
	if len(splt) != 4:
		good = False
	else:
		for i in splt:
			if not i.isdigit():
				good = False
			else:
				j = int(i)
				if (j < 0) or (j > 255):
					good = False
	
	return good

# TO ADD
# AIRCRAFT +/- buttons for multiple aircraft
# Set world origin in lat, lon, alt
# Skybox folder selection
# Plot toggle
# Timing checks - check for new tiles time
#               - aircraft mavlink delay time
# Display fps
# Display telemetry overlay toggle (more options to come, possibly aircraft name overlay)
# Select terrain data
        
