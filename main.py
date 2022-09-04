
import os
from pyvista import examples
import numpy as np

import pyvista as pv
import json
import time

#asdasd
DIR = os.path.dirname(os.path.realpath(__file__))
SETTINGS = json.load(open(f"{DIR}\\settings\\settings.json"))

p = pv.Plotter()
legno = pv.Box()
pezzo = pv.PolyData()
punta = pv.Cylinder()

def initializePlotter():
    global p
    if SETTINGS['Plotter']['show_axes']:
        p.show_axes()
    if SETTINGS['Plotter']['show_grid']:
        p.show_grid()


def initializeLegno():
    global legno
    global p
    bounds = [
        SETTINGS['Legno']['Starting point']['x'], 
        SETTINGS['Legno']['Starting point']['x']+SETTINGS['Legno']['Dimensions']['x'],
        SETTINGS['Legno']['Starting point']['y'], 
        SETTINGS['Legno']['Starting point']['y']+SETTINGS['Legno']['Dimensions']['y'],
        SETTINGS['Legno']['Starting point']['z'], 
        SETTINGS['Legno']['Starting point']['z']+SETTINGS['Legno']['Dimensions']['z'],
        ]
    legno = pv.Box(bounds=bounds).triangulate()
    
    dimensioni = [round(abs(bounds[0])+abs(bounds[1]),2),round(abs(bounds[2])+abs(bounds[3]),2),round(abs(bounds[4])+abs(bounds[5]),2)]
    p.add_text(f'Dimensioni Legno: \n x {dimensioni[0]}\ny {dimensioni[1]}\nz {dimensioni[2]}', 
                    position='upper_right', 
                    color='black',
                    font_size=10)
    
    Alegno = p.add_mesh(legno,name=SETTINGS['Legno']['Name'], style=SETTINGS['Legno']['Style'], line_width=3, color="brown")
    return Alegno

def initializePezzo(src):
    global p
    global legno
    global pezzo

    pezzo = pv.read(src).triangulate()
    pezzo.rotate_z(-90)
    pezzo.translate([-pezzo.bounds[0],-pezzo.bounds[2],-pezzo.bounds[4]])
    dimensioni = [round(abs(pezzo.bounds[0])+abs(pezzo.bounds[1]),2),round(abs(pezzo.bounds[2])+abs(pezzo.bounds[3]),2),round(abs(pezzo.bounds[4])+abs(pezzo.bounds[5]),2)]
    pezzo.scale(
        [
            0.0625,
            0.0347,
            0.034])
    dimensioni = [round(abs(pezzo.bounds[0])+abs(pezzo.bounds[1]),2),round(abs(pezzo.bounds[2])+abs(pezzo.bounds[3]),2),round(abs(pezzo.bounds[4])+abs(pezzo.bounds[5]),2)]
    pezzo['collision'] = np.zeros(pezzo.n_cells, dtype=bool)
    Apezzo = p.add_mesh(pezzo, style='')
    p.add_text(f'Dimensioni Pezzo: \n x {dimensioni[0]}\ny {dimensioni[1]}\nz {dimensioni[2]}', 
                    position='upper_left', 
                    color='black',
                    font_size=10)
    return Apezzo

def initializePunta():
    global p
    global punta
    global legno
    
    punta = pv.Cylinder(radius=SETTINGS['Punta']['Radius'], direction=(0,0,1), center=(0,0,SETTINGS['Legno']['Dimensions']['z']+1)).triangulate()
    print(punta.center)
    Apunta = p.add_mesh(punta, color="grey", style='')
    
    return Apunta

def movement():
    global p
    global punta
    global legno
    global pezzo

    radius = SETTINGS['Punta']['Radius']
    direction = (0,1,0)
    
    while True:
        print(f"can {direction}?")
        time.sleep(0.5)
        punta.translate([x *radius for x in direction],inplace=True)
        n_contacts = pezzo.collision(punta)[1]
        if n_contacts:
            print(not n_contacts)
            punta.translate([x *-radius for x in direction],inplace=True)
            p.update()
            time.sleep(5)
        else:
            print(n_contacts)
        time.sleep(0.5)
        p.update()

        '''if punta.center[0]+radius > legno.bounds[1] and direction == (1,0,0): #arrived at end of X
            direction = (0,1,0)
            print("turn on z axis")
        if punta.center[1]+radius > legno.bounds[3] and direction == (0,1,0): #arrived at end of Z
            direction = (-1,0,0)
            print("turn on -x axis")
        if punta.center[0]-radius < legno.bounds[0] and direction == (-1,0,0):
            direction = (0,-1,0)
            print("turn on -z axis")
        if punta.center[1]-radius < legno.bounds[0] and direction == (0,-1,0):
            #one level down
            print("Down and down into the deep")
            punta.translate((0,0,-1),inplace=True)
            time.sleep(0.1)
            p.update()
            direction = (1,0,0)
        #print(punta.collision(pezzo))

        punta.translate([x *radius for x in direction],inplace=True)
        n_contacts = pezzo.collision(punta)[1]
        if n_contacts:
            print("collision")
        time.sleep(0.1)
        p.update()'''


def main():
    global p
    global legno
    global pezzo
    global punta

    initializePlotter()
    Alegno = initializeLegno()
    Apezzo = initializePezzo(src=f"{DIR}\\Pezzo.obj")
    Apunta = initializePunta()
    legno = legno.boolean_intersection(pv.Box(bounds=pezzo.bounds).triangulate())
    p.remove_actor(Alegno)
    Alegno = p.add_mesh(legno, style = 'Wireframe')
    punta.translate((0,0,-1))
    
    p.show(interactive_update=True)
    movement()
    p.show()



if __name__ == "__main__":
    main()