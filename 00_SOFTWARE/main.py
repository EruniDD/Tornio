
import os
from tkinter import W
from turtle import color, width
from pyvista import examples
import numpy as np

import pyvista as pv
import json
import time

DIR = os.path.dirname(os.path.realpath(__file__))
SETTINGS = json.load(open(f"{DIR}\\settings\\settings.json"))

p = pv.Plotter()
legno = pv.Box()
pezzo = pv.PolyData()
punta = pv.Cylinder()
points = []

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
    AtestoLegno = p.add_text(f'Dimensioni Legno: \n x {dimensioni[0]}\ny {dimensioni[1]}\nz {dimensioni[2]}', 
                    position='upper_right', 
                    color='black',
                    font_size=10,
                )
    
    Alegno = p.add_mesh(legno,name=SETTINGS['Legno']['Name'], style=SETTINGS['Legno']['Style'], line_width=3, color="brown")
    return [Alegno,AtestoLegno]

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
            0.0625, #SONO DI PROVA
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
    global points

    punta = pv.Cylinder(radius=SETTINGS['Punta']['Radius'], direction=(0,0,1), center=(0,0,SETTINGS['Legno']['Dimensions']['z']+SETTINGS["Punta"]["Height"]),height=SETTINGS["Punta"]["Height"]).triangulate()
    Apunta = p.add_mesh(punta, color="grey", style='Wireframe')
    #AtestoPunta = p.add_text(text=GenerateTestoPunta(),position="left_edge",font_size=10)
    points.append([round(punta.center[0],2),round(punta.center[1],2),round((punta.center[2]-abs(SETTINGS['Punta']['Height']/2)),2)])
    return [Apunta,0]

def CanGo(direction, quality):
    global punta
    global pezzo
    punta.translate([x * quality for x in direction], inplace=True)
    collisions = pezzo.collision(punta)[1]
    if collisions:
        #torna indietro
        punta.translate([x * -quality for x in direction], inplace=True)
        return False
    else:
        return True

def GoUp(direction,quality):
    global legno
    global punta
    global pezzo
    global p

    punta.translate([x * quality for x in direction], inplace=True)
    collisions = pezzo.collision(punta)[1]
    height = 0
    while punta.center[2] <  legno.bounds[5]+SETTINGS["Punta"]["Height"]:
        collisions = pezzo.collision(punta)[1]
        if collisions:
            height += quality
            punta.translate([0,0,quality], inplace=True)
            #time.sleep(0.1)
            p.update()
        else:
            return height

def CanDown(quality):
    global punta
    global pezzo
    global p
    punta.translate([0,0,-quality], inplace=True)
    collisions = pezzo.collision(punta)[1]
    punta.translate([0,0,quality], inplace=True)
    if collisions:
        #torna indietro     
        return False
    else:
        return True

def ResetPositionPunta():
    global punta
    global p
    global pezzo
    
    punta.translate([-round(punta.center[0],2),-round(punta.center[1],2),-abs(round(punta.center[2]-pezzo.bounds[5],2)+SETTINGS['Punta']['Height'])])
    p.update()

def GoNextLevel(livello):
    global pezzo
    global p
    ResetPositionPunta()
    punta.translate([0,0,-SETTINGS['Punta']['Height']*livello])
    pass


def movement(AtestoPunta):
    global p
    global punta
    global legno
    global pezzo
    global points 

    quality = SETTINGS['General']['Quality']
    giri = 1
    livello = 1

    direction = (0,1,0)
    #abbasso la punta
    punta.translate((0,0,-SETTINGS['Punta']["Height"]),inplace=True)

    points.append([round(punta.center[0],2),round(punta.center[1],2),round(punta.center[2]-abs(SETTINGS['Punta']['Height']/2),2)])
    #p.add_lines(np.array([points[-2],points[-1]]),color = 'yellow', width = 3)
    #print(points)
    p.update()

    height = 0
    while True:
        #print(height)
        while height > 0:
            if CanDown(quality):
                punta.translate([0,0,-quality])
                height -= quality
            else:
                break

        if CanGo(direction,quality):
            #posso andarci
            pass

        else:
            #non posso andarci
            #provo ad alzarmi
            height += GoUp(direction,quality)
            #print(f"devo alzarmi di {round(height,1)}")
        if direction == (0,1,0) and punta.center[1] > pezzo.bounds[3]-(quality+(giri*quality)):
            print("Giro a +X")
            direction = (1,0,0)
        if direction == (1,0,0) and punta.center[0] > pezzo.bounds[1]-(quality+(giri*quality)):
            print("Giro a -Y")
            direction = (0,-1,0)
        if direction == (0,-1,0) and punta.center[1] < pezzo.bounds[2]+(quality+(giri*quality)):
            print("Giro a -X")
            direction = (-1,0,0)

        if direction == (-1,0,0) and punta.center[0] < pezzo.bounds[0]+(quality+(giri*quality)):
            print("Ho fatto un giro e vado a +Y")
            #ha fatto un giro
            giri+=1
            direction = (0,1,0)

        if [round(punta.center[0],2), round(punta.center[1],2),round(punta.center[2]-SETTINGS['Punta']['Height']/2,2)] in points:
            livello+=1
            height = 0
            GoNextLevel(livello)
            #p.add_mesh(pv.MultipleLines(points=points),color='Yellow')
            #p.show()     
        
        #time.sleep(0.2)
        #p.remove_actor(AtestoPunta)
        #AtestoPunta = p.add_text(text=GenerateTestoPunta(),position="left_edge",font_size=10)
        
        points.append([round(punta.center[0],2), round(punta.center[1],2),round(punta.center[2]-SETTINGS['Punta']['Height']/2,2)])
        #p.add_lines(np.array([points[-2],points[-1]]),color = 'yellow', width = 3)
        p.update()
        #n_contacts = pezzo.collision(punta)[1]
        #if n_contacts:
        #    pass

def GenerateTestoPunta():
    global punta
    return f"Posizione punta:\nx {round(punta.center[0],2)}\ny {round(punta.center[1]+(SETTINGS['Punta']['Height']/2),2)}\nz {round(punta.center[2],2)}"

def main():
    global p
    global legno
    global pezzo
    global punta

    initializePlotter()
    Alegno, AtestoLegno = initializeLegno()
    Apezzo = initializePezzo(src=f"{DIR}\\Pezzo.obj")
    Apunta, AtestoPunta = initializePunta()
    legno = legno.boolean_intersection(pv.Box(bounds=pezzo.bounds).triangulate())
    p.remove_actor(Alegno)
    Alegno = p.add_mesh(legno, style = 'Wireframe')
    
    p.show(interactive_update=True)
    movement(AtestoPunta)
    p.show()



if __name__ == "__main__":
    main()