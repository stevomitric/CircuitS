
from tkinter import *
from tkinter.ttk import *
import tkinter as tk
from PIL import Image
from PIL import ImageTk
from utils import *
import json

class Element:
    def __init__(self, canvas, type, pos, img, lab, angle=0):
        self.type = type
        self.canv = canvas
        self.pos = pos
        self.imgPath = img
        self.baseImg = loadImage(img, (60,60), angle)
        self.angle = angle
        self.lab_offsets_x, self.lab_offsets_y = offsetsByElement(type)
        self.lab_offset = [ self.lab_offsets_x[self.angle//90], self.lab_offsets_y[self.angle//90] ]
        self.label = lab if lab!='G' else ''
        self.node1, self.node2 = "/", "/"

        pos = snapPos(pos)
        self.img = self.canv.create_image( pos[0], pos[1], image=self.baseImg, anchor="center")
        self.lab = self.canv.create_text(pos[0]-self.lab_offset[0], pos[1]-self.lab_offset[1], text=self.label)

    def move(self, xGain, yGain):
        self.pos = (self.pos[0]+xGain, self.pos[1]+yGain)
        newpos = snapPos(self.pos)

        self.canv.coords(self.img, *newpos)
        self.canv.coords(self.lab, newpos[0]-self.lab_offset[0], newpos[1]-self.lab_offset[1])

    def distanceTo(self, pos):
        return ((self.pos[0]-pos[0])**2 + (self.pos[1]-pos[1])**2 )**0.5

    def erase(self):
        self.canv.delete(self.img)
        self.canv.delete(self.lab)

    def rotate(self):
        self.angle = (self.angle+90)%360
        self.lab_offset = [ self.lab_offsets_x[self.angle//90], self.lab_offsets_y[self.angle//90] ]

        self.baseImg = loadImage(self.imgPath, (60,60), self.angle)
        self.canv.itemconfig(self.img, image=self.baseImg)
        self.move(0,0)

    def getTerminals(self):
        pos = snapPos(self.pos)
        t1p1, t2p1 = (pos[0], pos[1]+30), (pos[0], pos[1]-30)
        t1p2, t2p2 = (pos[0]+30, pos[1]), (pos[0]-30, pos[1])
        if (self.angle == 0 or self.angle == 180):
            if (self.type == "V"): return [t1p1, t2p1] if (self.angle == 180) else [t2p1, t1p1]
            elif (self.type == "I"): return [t1p1, t2p1] if (self.angle == 0) else [t2p1, t1p1]
            elif (self.type == "G"): return [t2p1] if self.angle==0 else [t1p1]
            else: return [t1p2, t2p2]
        else:
            if (self.type == "V"): return [t1p2, t2p2] if (self.angle == 270) else [t2p2, t1p2]
            elif (self.type == "I"): return [t1p2, t2p2] if (self.angle == 90) else [t2p2, t1p2]
            elif (self.type == "G"): return [t2p2] if self.angle==0 else [t1p2]
            else: return [t1p1, t2p1]

    def changeLabel(self, new):
        self.label = new
        self.canv.itemconfig(self.lab, text=new)

    def openConfig(self):
        tp = Toplevel()
        x = tp.master.winfo_x()+tp.master.winfo_width()//2-200//2
        y = tp.master.winfo_y()+tp.master.winfo_height()//2-100//2
        tp.geometry(f"200x100+{x}+{y}")
        tp.e1 = Entry(tp)
        tp.e1.insert(0, str(self.label))
        tp.e1.pack(side='top', padx=5, pady=5, fill='x' )
        Label(tp, text=f"Node1: {self.node1}   Node2: {self.node2}").pack(side='top', pady=5)
        tp.b1 = Button(tp, text='Save', command= lambda:self.changeLabel( tp.e1.get() ) )
        tp.b1.pack(side='top', pady=5)

class LineElement:
    def __init__(self, canvas, pos1, pos2):
        self.canv = canvas
        self.pos1 = pos1
        self.pos2 = pos2
        self.type = "line"

        pos1, pos2 = snapPos(pos1), snapPos(pos2)
        self.line = self.canv.create_line( *pos1, *pos2 )

    def move(self, xGain, yGain):
        self.pos1 = (self.pos1[0]+xGain, self.pos1[1]+yGain)
        self.pos2 = (self.pos2[0]+xGain, self.pos2[1]+yGain)
        newpos1 = snapPos(self.pos1)
        newpos2 = snapPos(self.pos2)

        self.canv.coords(self.line, *newpos1, *newpos2)
    
    def erase(self):
        self.canv.delete(self.line)

    def openConfig(self):
        pass
        

    def distanceTo(self, pos):
        #return abs( (self.pos2[0]-self.pos1[0])*(self.pos1[1]-pos[1]) - (self.pos1[0]-pos[0])*(self.pos2[1]-self.pos1[1]) ) / ( (self.pos2[0]-self.pos1[0])**2 + (self.pos2[1]-self.pos1[1])**2 )**0.5
        N = 5
        advx, advy = (self.pos1[0]-self.pos2[0])/N, (self.pos1[1]-self.pos2[1])/N
        ps = [ (self.pos2[0]+i*advx, self.pos2[1]+i*advy) for i in range(N) ]
        return min( [pointDist(pos, self.pos1), pointDist(pos, self.pos2) ] + [pointDist(pos, p) for p in ps] )

    def rotate(self):
        pass

class Elements: 
    def __init__(self, canv):
        self.canv = canv

        conv_size = (60,60)

        self.IMGS = {
            'R': "gui/elements/resistor.png",
            'C': "gui/elements/capacitor.png",
            'L': "gui/elements/inductor.png",
            'V': "gui/elements/voltage.png",
            'I': "gui/elements/current.png",
            'Z': "gui/elements/impedance.png",
            'Y': "gui/elements/impedance.png",
            'G': "gui/elements/Ground.png",
        
            "erase": loadImage("gui/icons/erase.png", (30,30))
        }


        self.STATE = None
        self.selected = -1
        self.selectedBase = (-1, -1)
        self.lastMousePos = (0,0)
        self.lastPressMousePos = (0,0)

        self.elements = []

    def clearState(self):
        if (self.STATE == "drawLine"):
            self.STATE = None
            if (self.tmp[0]):
                self.canv.delete(self.tmp[0])
                self.canv.delete(self.tmp[1])
            if (self.tmp[4]):
                self.canv.delete(self.tmp[4])
        if (self.STATE == "erase"):
            self.STATE = None
            self.canv.delete(self.tmp[0])

    def drawLine(self):
        if (self.STATE == None):
            self.tmp = [0,0,(-1,-1), False, 0]
            self.STATE = "drawLine"
            self.tmp[0] = self.canv.create_line(0,0,0,1, dash=(5,1), fill='gray75')
            self.tmp[1] = self.canv.create_line(0,0,0,1, dash=(5,1), fill='gray75')

    def erase(self):
        if (self.STATE == None):
            self.STATE = "erase"
            self.tmp = [0]
            self.tmp[0] = self.canv.create_image( -10, -10, image=self.IMGS["erase"], anchor="center")

    def rotate(self):
        dist, best = self.closest(self.lastMousePos)

        if (dist < 32):
            self.elements[best].rotate()

    def closest(self, pos):
        dist, best = 9999999, -1
        for i, elem in enumerate(self.elements):
            if (dist > elem.distanceTo(pos) ):
                dist = elem.distanceTo(pos) 
                best = i
        return dist, best

    def addElement(self, type):
        elem = Element(self.canv, type, (150,100), self.IMGS[type], type)
        self.elements.append(elem)

    def B1Press(self, event):
        if (self.STATE == None): # moving elements
            dist, best = self.closest((event.x, event.y))
            if (dist < 32):
                self.selected = best
                self.selectedBase = (event.x, event.y)
        elif (self.STATE == "drawLine"):
            if (self.tmp[3]):
                pos = snapPos((event.x, event.y)) 
                pos1 = self.tmp[2]
                pos2 = (pos[0], self.tmp[2][1])
                if (abs(self.tmp[2][0]-event.x) < abs(self.tmp[2][1]-event.y) ): pos2 = (self.tmp[2][0], pos[1])
                elem = LineElement(self.canv, pos1, pos2)
                self.elements.append(elem)
                self.canv.coords(self.tmp[4], 0,0,0,0)
                self.tmp[2] = pos2
            else:
                self.tmp[2] = snapPos((event.x, event.y))
                self.tmp[3] = not self.tmp[3]
                self.tmp[4] = self.canv.create_line( *self.tmp[2], *self.tmp[2])
        elif (self.STATE == "erase"):
            dist, best = self.closest((event.x, event.y))
            if (dist < 32):
                self.elements[best].erase()
                self.elements.pop(best)

        self.lastPressMousePos = (event.x, event.y)

    def B1Release(self, event):
        self.selected = -1

        if (self.lastPressMousePos == self.lastMousePos and self.STATE == None):
            dist, best = self.closest((event.x, event.y))
            if (dist < 32):
                self.elements[best].openConfig()

    def MMotion(self, event):
        if (self.STATE == "drawLine"): # draw positioning lines and tmp line
            pos = snapPos((event.x, event.y))
            self.canv.coords(self.tmp[0], pos[0], 0, pos[0], 1080)
            self.canv.coords(self.tmp[1], 0, pos[1], 1920, pos[1])

            newpos = (pos[0], self.tmp[2][1])
            if (abs(self.tmp[2][0]-pos[0]) < abs(self.tmp[2][1]-pos[1]) ): newpos = (self.tmp[2][0], pos[1])
            self.canv.coords(self.tmp[4], *self.tmp[2], *newpos)

        if (self.STATE == "erase"):
            self.canv.coords(self.tmp[0], event.x, event.y)

        self.lastMousePos = (event.x, event.y)

    def B1Motion(self, event):
        if (self.selected != -1):
            self.elements[self.selected].move( -self.selectedBase[0] + event.x, -self.selectedBase[1] + event.y )
            self.selectedBase = (event.x, event.y)

        if (self.STATE == "erase"):
            dist, best = self.closest((event.x, event.y))
            if (dist < 32):
                self.elements[best].erase()
                self.elements.pop(best)

        self.lastMousePos = (event.x, event.y)

        self.MMotion(event)
        

    def export_elements(self, path):
        data = []
        for elem in self.elements:
            if (elem.type == "line"):
                data.append(['line', elem.pos1, elem.pos2])
            else:
                data.append([elem.type, elem.label, elem.pos, elem.angle, elem.imgPath])
        f = open(path, 'w')
        f.write(json.dumps(data))
        f.close()

    def import_elements(self, path):
        f = open(path)
        data = f.read()
        f.close()
        data = json.loads(data)

        for elem in data:
            if (elem[0] == "line"):
                tmp = LineElement(self.canv, elem[1], elem[2])
                self.elements.append(tmp)
            else:
                tmp = Element(self.canv, elem[0], elem[2], elem[4], elem[1], elem[3])
                self.elements.append(tmp)



    def __get_points(self, p1, p2):
        ln = [p1, p2]
        if (p1[0] == p2[0]):
            while (p1[1] < p2[1]):
                ln.append((p1[0], p1[1]))
                p1 = [p1[0], p1[1]+10]
            while (p1[1] > p2[1]):
                ln.append((p1[0], p1[1]))
                p1 = [p1[0], p1[1]-10]
        if (p1[1] == p2[1]):
            while (p1[0] < p2[0]):
                ln.append((p1[0], p1[1]))
                p1 = [p1[0]+10, p1[1]]
            while (p1[0] > p2[0]):
                ln.append((p1[0], p1[1]))
                p1 = [p1[0]-10, p1[1]]
        return ln
    
    def __check_connected(self, c, pos):
        for id in c:
            for p in c[id]:
                if (list(p) == list(pos)):
                    return id
        return False

    def juliaCircuit(self):
        data = 'circuit = create_circuit()\n'

        # nadji sve povezano
        connected, id_ = {0: []}, 1
        for elem in self.elements:
            if (elem.type == "line"):
                p1, p2 = snapPos(elem.pos1), snapPos(elem.pos2)
                ln = self.__get_points(p1, p2)
                ids = []
                for item in ln:
                    if (self.__check_connected(connected, item)) is not False:
                        ids.append(self.__check_connected(connected, item))

                if (not ids):
                    connected[id_] = ln
                    id_ += 1
                else:
                    master = ids[0]
                    connected[master] += ln
                    for id in ids[1:]:
                        connected[master] += connected.pop(id)
            elif elem.type != "G":
                t = elem.getTerminals()
                for p in t:
                    if (self.__check_connected(connected, p)) is not False:
                        connected[ self.__check_connected(connected, p) ].append(list(p))
                    else:
                        connected[id_] = [list(p)]
                        id_ += 1

        # dodaj sve ground-ove
        for elem in self.elements:
            if (elem.type == "G"):
                pos = snapPos(elem.getTerminals()[0])
                id = self.__check_connected(connected, pos)
                if (id is not False):
                    connected[0] += connected.pop(id)
                connected[0] += [pos]

        old = sorted(list(connected.keys()))
        connected_new = { i:connected[old[i]] for i in range(len(old))  }

        DATA_TYPES = {
            'R': "Resistor",
            "L": "Inductor",
            "C": "Capacitor",
            "Z": "Impedance",
            "Y": "Admitance",
            "I": "Current",
            "V": "Voltage",
        }

        # za R L C Z Y I V elemente
        for elem in self.elements:
            if (elem.type in "R L C Z Y I V"):
                t = elem.getTerminals()
                print(t)
                n1 = self.__check_connected(connected_new, t[0])
                elem.node1 = str(n1)
                n2 = self.__check_connected(connected_new, t[1])
                elem.node2 = str(n2)
                #print('elem ', elem.label, n1, n2)
                data += 'add_element(['+DATA_TYPES[elem.type]+', "'+elem.label+'", '+str(n1)+', '+str(n2)+'], circuit)\n'

        #print(data)

        return data
