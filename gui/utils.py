from PIL import Image
from PIL import ImageTk

IMAGES = [] # prevent garbage collecting

def loadImage(path, size = (20,20 ), rotate=0):
    img = Image.open(path)
    img = img.resize(size, Image.ANTIALIAS)
    if (rotate): img = img.rotate(rotate)
    img = ImageTk.PhotoImage(img)   
    IMAGES.append(img)
    return img

def snapPos(pos, snap = 10):
    pos = list(pos)[:]
    if (pos[0] % snap < snap//2):
        pos[0] -= pos[0]%snap
    else:
        pos[0] += snap - pos[0]%snap

    if (pos[1] % snap < snap//2):
        pos[1] -= pos[1]%snap
    else:
        pos[1] += snap - pos[1]%snap
    
    return pos

def pointDist(p1, p2):
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

def offsetsByElement(type):
    if (type == 'V' or type == "I"):
        return [20,20,-20,-20], [20,-20,20,-20]
    else:
        return [0,20,0,-20], [20,0,-20,0]