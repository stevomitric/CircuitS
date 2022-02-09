from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import showwarning, askyesno
import tkinter as tk

from utils import loadImage
from elements import Elements
from simulator import Simulate

class Main:
    def __init__(self):
        self.images = []

    def drawGui(self):
        self.root = Tk()
        self.root.geometry("700x500")
        self.root.title("CircuitS GUI")

        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.createNew)
        filemenu.add_command(label="Open", command=self.importElements)
        filemenu.add_command(label="Save as...",command=self.exportElements)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Line")
        editmenu.add_separator()
        editmenu.add_command(label="Resistor")
        editmenu.add_command(label="Capacitor")
        editmenu.add_command(label="Inductor")
        editmenu.add_command(label="Voltage")
        editmenu.add_command(label="Current")
        menubar.add_cascade(label="Edit", menu=editmenu)
        
        simulatemenu = Menu(menubar, tearoff=0)
        simulatemenu.add_command(label="Run")
        menubar.add_cascade(label="Simulate", menu=simulatemenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Documentation")
        helpmenu.add_command(label="About...")
        menubar.add_cascade(label="Help", menu=helpmenu)

        f1 = tk.Frame(self.root, bg='ghostwhite')

        Button(f1, image=loadImage('gui/icons/new.png'), command=self.createNew).pack(side='left')
        Button(f1, image=loadImage('gui/icons/save.png'), command=self.exportElements).pack(side='left')
        Button(f1, image=loadImage('gui/icons/load.png'), command=self.importElements).pack(side='left', padx=(0,20))
        Button(f1, image=loadImage('gui/icons/run.png'), command=self.simulate).pack(side='left')
        Button(f1, image=loadImage('gui/icons/help.png')).pack(side='left', padx=(0,20))
        Button(f1, image=loadImage('gui/icons/pen.png'), command=self.drawLine).pack(side='left')
        Button(f1, image=loadImage('gui/icons/erase.png'),  command=self.erase).pack(side='left', padx=(0,20))
        Button(f1, image=loadImage('gui/icons/resistor.png'), command= lambda : self.addElement("R") ).pack(side='left')
        Button(f1, image=loadImage('gui/icons/capacitor.png'), command= lambda : self.addElement("C")).pack(side='left')
        Button(f1, image=loadImage('gui/icons/inductor.png'), command= lambda : self.addElement("L")).pack(side='left')
        Button(f1, image=loadImage('gui/icons/impedance.png'), command= lambda : self.addElement("Z")).pack(side='left')
        Button(f1, image=loadImage('gui/icons/admitance.png'), command= lambda : self.addElement("Y")).pack(side='left')
        Button(f1, image=loadImage('gui/icons/voltage.png'), command= lambda : self.addElement("V")).pack(side='left')
        Button(f1, image=loadImage('gui/icons/current.png'), command= lambda : self.addElement("I")).pack(side='left')
        Button(f1, image=loadImage('gui/icons/ground.png'), command= lambda : self.addElement("G")).pack(side='left', padx=(20,0))
        f1.pack(side='top', fill='x')

        f2 = Frame(self.root)
        self.canv = Canvas(f2, bg='white')
        self.canv.pack(fill='both', expand="yes")
        f2.pack(fill='both', expand="yes")

        self.root.config(menu=menubar)

        self.canv.bind("<ButtonPress-1>", self.B1Press)
        self.canv.bind("<ButtonPress-3>", self.B2Press)
        self.canv.bind("<ButtonRelease-1>", self.B1Release)
        self.canv.bind("<B1-Motion>", self.B1Motion)
        self.canv.bind("<Motion>", self.MMotion)

        self.root.bind('<Key>', self.keypress)

        self.elements = Elements(self.canv)
        self.simulator = Simulate(self)

        # try to find circuitS
        self.circuitS = ''
        self.circuitSfn = ''
        FILEPATHS = ['CircuitS.jl', '../CircuitS.jl', '../../CircuitS.jl']
        for fl in FILEPATHS:
            try:
                f = open(fl, 'r')
                self.circuitS = f.read()
                self.circuitSfn = fl
                f.close()
            except:
                pass

        self.root.mainloop()

    def createNew(self):
        if (self.elements.elements == []):
            return

        r = askyesno("Are you sure?", "There appears to be some elements on the existing scheme. Creating a new scheme will clear the canvas. Are you sure you want to continue?")
        if (not r):
            return
        for elem in self.elements.elements:
            elem.erase()
        self.elements.elements == []

    def exportElements(self):
        fl = asksaveasfilename(defaultextension=".circS", filetypes=(("CircuitS files", "*.circS"),("All Files", "*.*")) )
        if not fl: return
        self.elements.export_elements(fl)

    def importElements(self):
        fl = askopenfilename(defaultextension=".circS", filetypes=(("CircuitS files", "*.circS"),("All Files", "*.*")) )
        if not fl: return
        self.elements.import_elements(fl)

    def keypress(self,event):
        if (event.keycode == 27): #Escape
            self.elements.clearState()

        if (event.keycode == 82): #R
            self.elements.rotate()
        if (event.char == 'a'):
            self.elements.juliaCircuit()

    def erase(self):
        self.elements.clearState()
        self.elements.erase()

    def drawLine(self):
        self.elements.clearState()
        self.elements.drawLine()

    def addElement(self, elem):
        self.elements.clearState()
        self.elements.addElement(elem)

    def B1Press(self, event):
        self.elements.B1Press(event)

    def B2Press(self, event):
        self.elements.clearState()

    def B1Release(self, event):
        self.elements.B1Release(event)

    def B1Motion(self, event):
        self.elements.B1Motion(event)

    def MMotion(self, event):
        self.elements.MMotion(event)

    def simulate(self):
        tp = Toplevel(self.root)
        x = tp.master.winfo_x()+tp.master.winfo_width()//2-300//2
        y = tp.master.winfo_y()+tp.master.winfo_height()//2-120//2
        tp.geometry(f"+{x}+{y}")

        f1 = Frame(tp)
        tp.e1 = Entry(f1, width=40)
        tp.e1.insert(0, self.circuitSfn)
        tp.e1['state'] = 'disabled'
        b1 = Button(f1, text="...", width=5, command=lambda:self.locateCircuitS(tp))
        tp.e1.pack(side='left', fill='x')
        b1.pack(side='right')
        f1.pack(side='top', fill='x', padx=5, pady=5)

        tp.l1 = Label(tp, text="Ready to simulate!")
        tp.l1.pack(side='top', pady=5)
        f2 = Frame(tp)
        tp.b1 = Button(f2, width=15, text = "Simulate", command=lambda:self.beginSimulate(tp))
        tp.b2 = Button(f2, width=15, text = "Stop", state='disabled', command=lambda:self.stopSimulation(tp))
        f2.pack(side='top', pady=5)
        tp.b1.pack(side='left')
        tp.b2.pack(side='left', padx=(5,0))
        tp.l2 = Label(tp)
        tp.l2.pack(side='top')

        tp.sim = False
        tp.after(100, lambda : self.simulateLoop(tp) )

        if (self.circuitS == ''):
            tp.b1['state'] = 'disabled'
            showwarning("No CircuitS.jl", "It appears i can't find CircuitS.jl library. CircuitS.jl is needed as it runs the simulations. Please find it using '...' button. You can also copy it in the same directory as this program and restart the GUI.", parent=tp)

    def locateCircuitS(self, tp):
        fn = askopenfilename(parent=tp)
        try:
            f = open(fn, "r")
            self.circuitS = f.read()
            f.close()
            tp.b1['state'] = 'normal'
            tp.e1['state'] = 'normal'
            tp.e1.delete(0, 'end')
            tp.e1.insert(0, fn)
            tp.e1['state'] = 'disabled'
        except:
            showwarning("Error", "I cant open this file.",parent=tp)

    def beginSimulate(self, tp):
        tp.b1['state'] = 'disabled'
        tp.b2['state'] = 'normal'

        tp.p, tp.q = self.simulator.createProcess(self.circuitS)
        tp.sim = True
        tp.l1['text'] = "Simulating..."

    def stopSimulation(self, tp):
        try:
            tp.p.terminate()
            tp.sim = False
            tp.b1['state'] = 'normal'
            tp.b2['state'] = 'disabled'
            tp.l1['text'] = "Simulation Stopped!"
        except:
            pass

    def simulateLoop(self, tp):
        if (tp.sim):
            if (not tp.q.empty()):
                data = tp.q.get()
                print (data)
                
                if (data[0:2] == "S "):
                    tp.b1['state'] = 'normal'
                    tp.b2['state'] = 'disabled'
                    tp.l1['text'] = "Simulation Successfull!"
                    tp.l2['text'] = data[2:]
                elif (data[0:2] == "F "):
                    tp.b1['state'] = 'normal'
                    tp.b2['state'] = 'disabled'
                    tp.l1['text'] = "Simulation Failed!"
                    tp.l2['text'] = ''
                else:
                    tp.l1['text'] = data

        tp.after(100, lambda : self.simulateLoop(tp) )

if __name__ == '__main__':
    prog = Main()
    prog.drawGui()