import os
import time
from random import randint, choice
from math import sqrt

import pygame as pg
from pygame import color

pg.init()

#-------- Window settings
# Get the monitor size
monitor_w = pg.display.Info().current_w  # Monitor width
monitor_h = pg.display.Info().current_h  # Monitor height
fullscreen = False

# Scaling the window size
if fullscreen:
    win_width = monitor_w
    win_height = monitor_h
else:
    win_width = int(monitor_w / 2)
    win_height = int(monitor_h / 1.5)

# Centering the window
# center_x = (monitor_w/2) - (win_width/2)
# center_y = (monitor_h/2) - (win_height/2)
# os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (center_x,center_y)
os.environ['SDL_VIDEO_CENTERED'] = '1'

win_res = win_width * win_height
win = pg.display.set_mode((win_width, win_height))  # Surface
pg.display.set_caption("Bouncing Cube")  # Window title

#--------  Info text settings
infoDisplay = True  # Show info or not
font = pg.font.Font(None, 20)  # Default font, size 20

#-------- Background settings
back = pg.image.load("back.png").convert()  # Charging image
back = pg.transform.scale(back, (win_width, win_height))  # Resize
back.set_alpha(100)  # Opacity

#--------  Object settings
"""All the proportion values were obtained from a window size of 1024x768"""
# Central obstacle settings
obst_width = win_width
obst_height = int(win_height / 15.36)  # The obstacle height is proportional to the window height
obst_x = int((win_width / 2) - (obst_width / 2))  # Centering x
obst_y = int((win_height / 2) - (obst_height / 2))  # Centering y
obst_min_width = int(win_width / 20.48)  # The obstacle min width is proportional to the window width
obst_contraction = int(obst_width / obst_min_width)
obst_contraction = -obst_contraction  # Contraction level
obst = pg.Rect(obst_x, obst_y, obst_width, obst_height)

# Moving cube settings
cube_x = 5  # Initial cube x axis
cube_y = 5  # Initial cube y axis
cube_size = int(win_res / 1966.08)  # The cube area is proportional to the window area
cube_size = int(sqrt(cube_size))  # The square root of the cube area gives the value of his side
cube = pg.Rect(cube_x, cube_y, cube_size, cube_size)
vector = [14, 18]  # Cube vector direction

#--------  Color settings
# Color pallet
colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255),
          "white": (255, 255, 255), "pink": (255, 0, 255), "cyan": (0, 255, 255),
          "yellow": (255, 255, 0), "orange": (255, 143, 87), "black": (0, 0, 0)}

cube_color = colors["white"]  # Cube color

# 'obst' color gradient
obst_G_color = 255  # Green color modulation
obst_G_color_init = obst_G_color  # Color benchmark
color_steps = obst[2] - obst_min_width  # Difference between 'obst' max width & min width
color_steps = int(color_steps / abs(obst_contraction))  # Steps to reach 'obst' min width
color_steps = int(obst_G_color / color_steps)  # Decrementation value of green color gradient

#--------  Collision control
edge_collision = 0
obst_collision = 0
total_collision = 0
collision_bug = 0  # Collision bug counter
b = 5  # coordinate bias (Adjustment of the hitbox)
speed_limit = 0.05  # Minimum time allowed between collisions
time_after_bug = 1
tooFast = False  # Collision bug flag
time_ctrl = []  # Stores the time of each collision on the central obstacle

#--------  Animation control
clock = pg.time.Clock()
fps_val = 40  # Frame per second value
fps_val_init = fps_val

#--------  Function
def witchSide(rect1, rect2):
    """ Return a relative position
    Position of rect2 in relation to rect1 """
    if rect1.midtop[1] > rect2.midtop[1]:
        return "top"
    elif rect1.midleft[0] > rect2.midleft[0]:
        return "left"
    elif rect1.midright[0] < rect2.midright[0]:
        return "right"
    else:
        return "bottom"

#----------------------  Animation loop ----------------------
run = True
while run:
    clock.tick(fps_val)  # Frame per second

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False

    #-------- Key event
    keys = pg.key.get_pressed()

    if keys[pg.K_ESCAPE]:
        run = False  # Quit the program

    if keys[pg.K_UP] and fps_val <= fps_val_init + 20:
        fps_val += 1  # Increase fps

    if keys[pg.K_DOWN] and fps_val >= 0:
        fps_val -= 1  # Decrease fps

    if keys[pg.K_SPACE]:
        fps_val = fps_val_init  # Back fps to default value

    #-------- Vectorial direction
    cube_x += vector[0]
    cube_y += vector[1]

    #-------- The cube is in contact with the central obstacle
    side = witchSide(obst, cube)  # Position of cube in relation to obst

    if side == "top" or side == "bottom":  # cube is up or down obst
        if cube.colliderect(obst):  # Collision detected
            time_ctrl.append(time.time())  # Time collision recording
            obst_collision += 1
            if side == "top":
                cube_color = colors["pink"]
            else:
                cube_color = colors["cyan"]
            vector[1] = -vector[1]  # Inverting the y vector

    if side == "left" or side == "right":  # cube is to the left or right of obst
        if cube.colliderect(obst):
            time_ctrl.append(time.time())  # Time collision recording
            obst_collision += 1
            if side == "top":
                cube_color = colors["red"]
            else:
                cube_color = colors["green"]
            vector[0] = -vector[0]  # Inverting the x vector

    #-------- The cube is in contact with an edge of the surface
    """ Each time the cube comes into contact with an edge of the surface,
    "obst" contracts to a minimum before returning to its initial size."""

    # Left side or right side
    if cube_x < 0 + b * 2 or cube_x > win_width + b - cube_size:  # Side edges of the window
        # time_ctrl.append(time.time())
        edge_collision += 1
        cube_color = colors["white"]
        vector[0] = -vector[0]  # Inverting x vector

        if obst[2] > obst_min_width:  # While 'obst' width is greater than 'obst_min_width'
            obst.inflate_ip(obst_contraction, 0)  # 'obst' width contraction (-x)
            obst_G_color -= color_steps  # Decrement the G value of the RGB of 'obst'
            if obst_G_color < 0:  # Avoid negative number in RGB
                obst_G_color = 0

        else:  # 'obst' width is smaller or equal than 'obst_min_width'
            obst.inflate_ip(win_width - obst[2], 0)  # 'obst' returns to its original width (+x)
            obst_G_color = obst_G_color_init  # 'obst' returns to its original color

    # Up side or down side
    if cube_y < 0 + b * 2 or cube_y > win_height + b - cube_size:
        # time_ctrl.append(time.time())
        edge_collision += 1
        cube_color = colors["yellow"]
        vector[1] = -vector[1]  # Inverting y vector

        if obst[2] > obst_min_width:
            obst.inflate_ip(obst_contraction, 0)
            obst_G_color -= color_steps
            if obst_G_color < 0:  # Avoid negative number in RGB
                obst_G_color = 0

        else:
            obst.inflate_ip(win_width - obst[2], 0)
            obst_G_color = obst_G_color_init

    total_collision = obst_collision + edge_collision

    #----------------------  Info display ----------------------
    if infoDisplay:
        #-------- General info
        # Window size
        win_size_text = "Win. size : ({}x{})".format(win_width, win_height)
        win_size_text = font.render(win_size_text, True, (colors["white"]))
        win_size_text_rect = win_size_text.get_rect()

        # Frame per second
        fps_text = "FPS : {}".format(round(clock.get_fps(), 2))
        fps_text = font.render(fps_text, True, (colors["white"]))
        fps_text_rect = fps_text.get_rect()

        #-------- Cube info
        # Cube position (x,y)
        cube_pos_text = "Cube pos. : (x:{}, y:{})".format(cube_x, cube_y)
        cube_pos_text = font.render(cube_pos_text,
                                    True,
                                    (colors["white"]))
        cube_pos_text_rect = cube_pos_text.get_rect()

        # Cube vector
        vect_text = "Cube vector : [{}, {}]".format(vector[0], vector[1])
        vect_text = font.render(vect_text,
                               True,
                               (colors["white"]))
        vect_text_rect = vect_text.get_rect()

        # Cube relative position
        side_text = "Cube relat. pos. : {}".format(side)
        side_text = font.render(side_text,
                               True,
                               (colors["white"]))
        side_text_rect = side_text.get_rect()

        # Cube size
        cube_size_text = "Cube size : {}".format(cube_size)
        cube_size_text = font.render(cube_size_text,
                                    True,
                                    (colors["white"]))
        cube_size_text_rect = cube_size_text.get_rect()

        # Cube color
        cube_color_text = "Cube color : {}".format(cube_color)
        cube_color_text = font.render(cube_color_text,
                                     True,
                                     (colors["white"]))
        cube_color_text_rect = cube_color_text.get_rect()

        #-------- Obstacle info
        # Central obstacle width
        obst_width_text = "Obst. width/min : {}/{}".format(obst[2],
                                                          obst_min_width)
        obst_width_text = font.render(obst_width_text,
                                     True,
                                     (colors["white"]))
        obst_width_text_rect = obst_width_text.get_rect()

        # Central obstacle height
        obst_height_text = "Obst. height : {}".format(obst_height)
        obst_height_text = font.render(obst_height_text,
                                      True,
                                      (colors["white"]))
        obst_height_text_rect = obst_height_text.get_rect()

        # Central obstacle color
        obst_color_text = "Obst color : (255,{},0)".format(obst_G_color)
        obst_color_text = font.render(obst_color_text,
                                     True,
                                     (colors["white"]))
        obst_color_text_rect = obst_color_text.get_rect()

        #-------- Collisions info
        # Edge collision
        edge_collisions_text = "Edge collision : {}".format(edge_collision)
        edge_collisions_text = font.render(edge_collisions_text,
                                          True,
                                          (colors["white"]))
        edge_collisions_text_rect = edge_collisions_text.get_rect()

        # Obstacle collision
        obst_collisions_text = "Obst. collision : {}".format(obst_collision)
        obst_collisions_text = font.render(obst_collisions_text,
                                          True,
                                          (colors["white"]))
        obst_collisions_text_rect = obst_collisions_text.get_rect()

        # Total collision
        total_collisions_text = "Total collision : {}".format(total_collision)
        total_collisions_text = font.render(total_collisions_text,
                                           True,
                                           (colors["white"]))
        total_collisions_text_rect = total_collisions_text.get_rect()

        # Collision bug
        collision_bug_text = "Collision bug : {}".format(collision_bug)
        if collision_bug == 0:
            collision_bug_text = font.render(collision_bug_text,
                                            True,
                                            (colors["green"]))
        else:
            collision_bug_text = font.render(collision_bug_text,
                                            True,
                                            (colors["red"]))
        collision_bug_text_rect = collision_bug_text.get_rect()

    #-------- Drawing
    win.fill(colors["black"])

    win.blit(back, (0, 0))  # Background
    pg.draw.rect(win, (255, obst_G_color, 0), obst)
    pg.draw.rect(win, cube_color, cube)
    cube.move_ip(vector[0], vector[1])

    # Info texts drawing
    if infoDisplay:
        win.blit(win_size_text, (0, 0), win_size_text_rect)
        win.blit(fps_text, (0, 15), fps_text_rect)

        win.blit(cube_pos_text, (0, 45), cube_pos_text_rect)
        win.blit(vect_text, (0, 60), vect_text_rect)
        win.blit(side_text, (0, 75), side_text_rect)
        win.blit(cube_size_text, (0, 90), cube_size_text_rect)
        win.blit(cube_color_text, (0, 105), cube_color_text_rect)

        win.blit(obst_width_text, (0, 135), obst_width_text_rect)
        win.blit(obst_height_text, (0, 150), obst_height_text_rect)
        win.blit(obst_color_text, (0, 165), obst_color_text_rect)

        win.blit(edge_collisions_text, (0, 195), edge_collisions_text_rect)
        win.blit(obst_collisions_text, (0, 210), obst_collisions_text_rect)
        win.blit(total_collisions_text, (0, 225), total_collisions_text_rect)
        win.blit(collision_bug_text, (0, 240), collision_bug_text_rect)

    if len(time_ctrl) >= 2 and tooFast == False:
        laps = time_ctrl[len(time_ctrl) - 1] - time_ctrl[len(time_ctrl) - 2]
        if laps < speed_limit:
            bug_time = time.time()
            collision_bug += 1
            cube_x = (randint(5, 25))  # Cube x axis teleportation
            cube_y = (randint(5, 25))  # Cube y axis teleportation
            cube = pg.Rect(cube_x, cube_y, cube_size, cube_size)  # Creating a new cube
            pg.draw.rect(win, cube_color, cube)  # Draw the cube
            vector[0] = abs(vector[0])
            vector[1] = abs(vector[1])

            tooFast = True

    if tooFast:
        """ After a collision bug, the cube randomly changes color for 
        'time_after_bug' second """
        cube_color = choice(list(colors.values()))

    if tooFast and time.time() > bug_time + time_after_bug:  # 1sec after bug_time
        """In order to prevent the program from oscillating in tooFast mode, 
        we mark a time so that the next time value of time_ctrl is more spaced"""
        tooFast = False
        time_ctrl.append(time.time())

    #-------- Updating the image
    pg.display.update()

pg.quit()
