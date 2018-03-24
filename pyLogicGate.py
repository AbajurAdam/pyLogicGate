#/usr/bin/env python
# -*- coding: cp1252 -*-
"""
Logic Gate Simulator
    - Bir kapı oluşturmak için, ekranın sol tarafından istediğiniz kapıyı sürükleyin. Gates, uygun soketlere tıklayarak bağlanır.
    - Giriş soketlerini sadece çıkış soketlerine bağlayabileceğinizi ve bunun tersini de unutmayın.
    - Kapıları ekranın sol tarafına geri sürükleyerek silin.
    - Giriş soketlerinden teller tekrar tıklanarak çıkarılabilir.
    - Bir çıkış soketine birçok kablo takılabilir, giriş soketleri de sadece bir tane olabilir.
    - Çıkış soketlerinden gelen kablolar, sadece bittikleri giriş soketinden çıkarılabilir.

"""

import pygame
import pygame.gfxdraw
import os
import time
import sys

from load_image import load_image
from gateCreator import gateCreator
from cable import cable
from Socket import Socket
from gate import gate
from switch import switch
from bulb import bulb
from button import button

green = (50, 210, 50)
white = (255, 255, 255)
black = (0, 0, 0)
blue = (70, 190, 255)
grey = (220, 220, 220)
midgrey = (150, 150, 150)
darkgrey = (80, 80, 80)


def main():
    # updates all the gates (and this also sockets and cables), then draws them to the screen.
    def drawScreen():
        pygame.draw.line(screen, black, (100, 0), (100, screensize[1]), 2)
        for Gate in gates:
            Gate.update()
        for creator in creators:
            15
            creator.draw()
    pygame.init()
    screensize = (1200, 800)
    screen = pygame.display.set_mode(screensize)
    pygame.display.set_caption('Logic Gate Sim -> Erkan Ercan')

    # The FPS the simulation will run at.
    FPS = 30
    sleeptime = 1/float(FPS)  # default sleep time

    creatorTypes = ["and", "or", "xor", "nand",
                    "nor", "xnor", "not", "switch", "bulb"]

    # in a sense, this is LIFO when it comes to drawing: the last element will be drawn on top.
    gates = []
    cables = []
    creators = [gateCreator() for x in range(len(creatorTypes))]

    for index, creator in enumerate(creators):
        creator.setType(creatorTypes[index])
        creator.setCords(0, index*50)  # creator.rect.height)
        creator.setScreen(screen)

    compile_button = button()
    compile_button.setType("compile")
    compile_button.setCords(0, 50)  # under the creators
    compile_button.setScreen(screen)

    running = True

    # each iteration of this is one frame, unless gates are clicked (framerate will remain the same however)
    while running:
        time.sleep(sleeptime)  # wait a little on each frame
        events = pygame.event.get()
        screen.fill(white)
        drawScreen()
        pygame.display.flip()
        for g in gates:  # check if any gates should be deleted
            if g.rect.center[0] < 100:
                g.SHUTDOWNEVERYTHING()
                gates.remove(g)

        for event in events:  # handle events
            if event.type == 2 and event.key == 27:  # escape key pressed? -> quit
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:  # mouse pressed?
                mouse = pygame.mouse.get_pos()
                mousePressed = True
                # check if creators have been pressed  -  if so, create gate.
                for gC in creators:
                    if gC.pressed(mouse):
                        if gC.type == "bulb":
                            Gate = bulb()
                            cOffset = (
                                gC.rect.topleft[0] - mouse[0], gC.rect.topleft[1]-mouse[1])
                            Gate.create(
                                gC.type, (mouse[0]+cOffset[0], mouse[1]+cOffset[1]), screen)
                            gates.append(Gate)
                        elif gC.type == "switch":
                            Gate = switch()  # HAHA! It's not actually a gate!
                            # mouse offset - we want to be able to drag the gate from wherever we press it
                            cOffset = (
                                gC.rect.topleft[0] - mouse[0], gC.rect.topleft[1]-mouse[1])
                            Gate.create(
                                gC.type, (mouse[0]+cOffset[0], mouse[1]+cOffset[1]), screen)
                            gates.append(Gate)
                        else:
                            Gate = gate()
                            # mouse offset - we want to be able to drag the gate from wherever we press it
                            cOffset = (
                                gC.rect.topleft[0] - mouse[0], gC.rect.topleft[1]-mouse[1])
                            Gate.create(
                                gC.type, (mouse[0]+cOffset[0], mouse[1]+cOffset[1]), screen)
                            gates.append(Gate)

                        offset = (
                            Gate.rect.topleft[0] - mouse[0], Gate.rect.topleft[1]-mouse[1])

                        while pygame.MOUSEBUTTONDOWN not in [ev.type for ev in pygame.event.get()]:
                            mouse = pygame.mouse.get_pos()
                            screen.fill(white)
                            Gate.setCords(mouse[0]+offset[0],
                                          mouse[1]+offset[1])
                            drawScreen()
                            pygame.display.flip()

                #### FOR THE LOVE OF ALL THAT IS HOLY DO NOT TOUCH THIS NEXT PART #####
                for Gate in gates:  # check if gate was clicked
                    ev = pygame.event.get()
                    mouse = pygame.mouse.get_pos()
                    p = Gate.pressed(mouse)
                    if p:
                        if p == "main":  # gate was clicked "on body", not sockets so we dont need to worry about cable stuff here.
                            # dragging offset again
                            offset = (
                                Gate.rect.topleft[0] - mouse[0], Gate.rect.topleft[1]-mouse[1])
                            while pygame.MOUSEBUTTONUP not in [ev.type for ev in ev]:
                                time.sleep(sleeptime)
                                mouse = pygame.mouse.get_pos()
                                Gate.setCords(
                                    mouse[0]+offset[0], mouse[1]+offset[1])
                                screen.fill(white)
                                drawScreen()
                                ev = pygame.event.get()
                                pygame.display.flip()

                        # oh boy, someone clicked an input socket, now what do we do
                        elif p[:2] == "in":

                            # Disconnect logic - only inputs can be disconnected
                            # great, the socket already had a connection on it. lets change that..
                            if Gate.inSockets[int(p[2:])].connected:
                                print("disconnecting")
                                Cable = Gate.inSockets[int(
                                    p[2:])].attachedCables[0]
                                Cable.disconnect("in")
                                mousePressed = False
                                gatePressed = False
                                while not mousePressed:  # loop for dragging the loose cable around. also yes, I should probably have called them wires
                                    time.sleep(sleeptime)
                                    mouse = pygame.mouse.get_pos()
                                    screen.fill(white)
                                    drawScreen()
                                    Cable.drawCable(
                                        Cable.startSocket.rect.center, mouse)
                                    if pygame.MOUSEBUTTONDOWN in [ev.type for ev in pygame.event.get()]:
                                        print("mousedown")
                                        for g in gates:
                                            # a socket was clicked, lets attach the cable here
                                            press = g.pressed(mouse)
                                            if press:
                                                print("#############")
                                                mousePressed = True
                                                # only worry about input sockets
                                                if press[:2] == "in":
                                                    print("connecting to ", g)
                                                    # saving the socket for connecting to later
                                                    inSock = g.inSockets[int(
                                                        press[2:])]
                                                    gatePressed = True
                                                    break
                                        # none of the gates were clicked, but the mouse was -> delete the cable.
                                        if not gatePressed:
                                            print(
                                                "no gate pressed, deleting cable")
                                            mousePressed = True
                                            break

                                    pygame.display.flip()
                                    if gatePressed:  # this part could have probably gone where we check if a gate was pressed
                                        print(
                                            "gate pressed after disconnect, should be reconnecting")
                                        if inSock.connect(Cable):
                                            Cable.setEndSocket(inSock)
                                            print(
                                                "connected", Cable.endSocket, " to ", Cable.startSocket, " with ", Cable)
                                        break
                                    if mousePressed:  # here we delete the cable
                                        Cable.startSocket.attachedCables.remove(
                                            Cable)
                                        Cable.endSocket.attachedCables = []
                                        Cable.startSocket = None
                                        Cable.endSocket = None
                                        break

                            # connect logic for input -> outpout
                            else:  # whew, long if statement there
                                print("cable from in")
                                Cable = cable()
                                Cable.setScreen(screen)
                                Cable.setEndSocket(Gate.inSockets[int(p[2:])])
                                # this whole thing pretty much runs analog to the disconnect logic, just in reverse
                                if Gate.inSockets[int(p[2:])].connect(Cable):
                                    mousePressed = False
                                    gatePressed = False
                                    # (pygame.MOUSEBUTTONDOWN not in [ev.type for ev in pygame.event.get()]):
                                    while not mousePressed:
                                        time.sleep(sleeptime)
                                        mouse = pygame.mouse.get_pos()
                                        screen.fill(white)
                                        drawScreen()
                                        Cable.drawCable(
                                            mouse, Cable.endSocket.rect.center)
                                        if pygame.MOUSEBUTTONDOWN in [ev.type for ev in pygame.event.get()]:
                                            print("mousedown")
                                            for g in gates:
                                                # only connect if an output socket was clicked
                                                if g.pressed(mouse) == "out":
                                                    print(
                                                        "connecting to output")
                                                    outSock = g.outSocket
                                                    gatePressed = True
                                                    break
                                                mousePressed = True
                                            if not gatePressed:
                                                print(
                                                    "mouse pressed, gates iterated, none pressed, disconnecting cable.")
                                                Gate.inSockets[int(p[2:])].disconnect(
                                                    Cable)

                                        pygame.display.flip()
                                        if gatePressed:
                                            if outSock.connect(Cable):
                                                Gate.inSockets[int(p[2:])].connect(
                                                    Cable)
                                                Cable.setStartSocket(outSock)
                                                print(
                                                    "connected", Cable.startSocket, " to ", Cable.endSocket, " with ", Cable)
                                            else:
                                                Gate.inSockets[int(p[2:])].disconnect(
                                                    Cable)
                                            break
                        # connect logic for output -> input
                        else:
                            print("cable from out")
                            Cable = cable()
                            Cable.setScreen(screen)
                            Cable.setStartSocket(Gate.outSocket)
                            if Gate.outSocket.connect(Cable):
                                mousePressed = False
                                gatePressed = False
                                # (pygame.MOUSEBUTTONDOWN not in [ev.type for ev in pygame.event.get()]):
                                while not mousePressed:
                                    time.sleep(sleeptime)
                                    mouse = pygame.mouse.get_pos()
                                    screen.fill(white)
                                    drawScreen()
                                    Cable.drawCable(
                                        mouse, Cable.startSocket.rect.center)
                                    # little different here: we need to specify which input socket to connect to
                                    if pygame.MOUSEBUTTONDOWN in [ev.type for ev in pygame.event.get()]:
                                        print("mousedown")
                                        for g in gates:
                                            # this returns "in0" and "in1" depending on which socket was clicked
                                            press = g.pressed(mouse)
                                            print(press)
                                            # (("in0" in [g.pressed(mouse) for g in gates])):
                                            if press == "in0":
                                                print("connecting to input0")
                                                inSock = g.inSockets[0]
                                                gatePressed = True
                                                break
                                            # ("in1" in [g.pressed(mouse) for g in gates]):
                                            elif press == "in1":
                                                print("connecting to input1")
                                                inSock = g.inSockets[1]
                                                gatePressed = True
                                                break
                                            mousePressed = True
                                        if not gatePressed:
                                            print("not connecting.")
                                            Gate.outSocket.disconnect(Cable)
                                            break

                                    pygame.display.flip()
                                    if gatePressed:
                                        if inSock.connect(Cable):
                                            Cable.setEndSocket(inSock)
                                            print(
                                                "connected", Cable.endSocket, " to ", Cable.startSocket, " with ", Cable)
                                        break
                        break
                ########################################
    pygame.quit()


if __name__ == '__main__':
    main()
