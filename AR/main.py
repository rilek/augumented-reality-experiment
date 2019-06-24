#!/usr/bin/env python3

import argparse
import json
import cv2
import numpy as np
from util import log, error, warning, info, success
from AugumentAPI import AugumentAPI
from Stream import Stream
from DrawAPI import draw_rectangle, draw_text, T

def prepare_arguments():
    parser = argparse.ArgumentParser(description='Process video stream')
    parser.add_argument('-s','--source', type=str, default=None,
                        help="""Source of video stream. Can be either ip address with port or file path.""")
    parser.add_argument('-t', "--type", type=str, default="cam", choices=["remote", "file", "cam", "image"],
                        help="""Type of source. \033[1mDefault: file\033[0m""")
    parser.add_argument('-c', "--config", type=str, default="config/config.json",
                        help="""Path to configuration file""")

    return parser.parse_args()

def get_mode_name(n):
    if n == 0:
        return "prezentacja"
    elif n == 1:
        return "limonkowy"
    elif n == 2:
        return "turkusowy"
    else:
        return "nieznany tryb"

def draw_arrow(frame, area):
    frame.draw_image("img/arr.png", tuple(area[:2][::-1]), (25, 25), transform=T.PERSPECTIVE)

def draw_rot_arrow(frame, area, ccw=False):
    size = 75
    path = "img/rot_arr_cw.png" if ccw else "img/rot_arr_ccw.png"
    frame.draw_image(path, (area[1], area[2]-size), (size, size), transform=T.PERSPECTIVE)

def draw_stats(frame, machine, params):
    mode = 1 or params["mode"]
    areas = machine["areas"]
    R = areas["R"]
    G = areas["G"]
    B = areas["B"]
    box_width = 170
    red = params["red"]
    green = params["green"]
    blue = params["blue"]

    # if not "connected" in params or params["connected"] == "OFF":
    if False:
        frame.draw_rectangle((10, 30), (box_width,37))
        frame.draw_text("Urzadzenie wylaczone", (20, 50))
    else:
        # frame.draw_text("Stan: {}".format(stage[state]), (20, 50))
        if mode == 0:
            bias = 0
            frame.draw_rectangle((10, 30), (box_width,90))
            frame.draw_text("Tryb: {}".format(get_mode_name(mode)), (20, 50))
        else:
            bias = 40
            frame.draw_rectangle((10, 30), (box_width,130))
            frame.draw_text("Tryb:", (20, 50))
            frame.draw_text(get_mode_name(mode), (20, 80), size=1)
        
        frame.draw_text("Czerwony: {}".format(red), (20, bias+70))
        frame.draw_text("Zielony: {}".format(green), (20, bias+90))
        frame.draw_text("Niebieski: {}".format(blue), (20, bias+110))

        if mode == 0:
            for name in areas:
                area = areas[name]
                frame.draw_image("img/arr.png", (area[1], area[2]), (25, 25), transform=T.PERSPECTIVE)
                frame.draw_text(name, (area[2], area[1]-30), color=(0, 0, 255), size=0.5, weight=2, transform=T.PERSPECTIVE)
        elif mode == 1:
            color = (100, 200, 0)

            if red - color[0] > 15:
                draw_rot_arrow(frame, R)
            elif red - color[0] < -15:
                draw_rot_arrow(frame, R, True)

            if green - color[1] > 15:
                draw_rot_arrow(frame, G)
            elif green - color[1] < -15:
                draw_rot_arrow(frame, G, True)

            if blue - color[2] > 15:
                draw_rot_arrow(frame, B)
            elif blue - color[2] < -15:
                draw_rot_arrow(frame, B, True)
        elif mode == 2:
            color = (5, 85, 35)

            if red - color[0] > 15:
                draw_rot_arrow(frame, R)
            elif red - color[0] < -15:
                draw_rot_arrow(frame, R, True)

            if green - color[1] > 15:
                draw_rot_arrow(frame, G)
            elif green - color[1] < -15:
                draw_rot_arrow(frame, G, True)

            if blue - color[2] > 15:
                draw_rot_arrow(frame, B)
            elif blue - color[2] < -15:
                draw_rot_arrow(frame, B, True)
            
    

    # if state is 0:
    # elif state is 1:
    #     frame.draw_image("img/arr.png", tuple(machine["areas"]["subtitle"][:2][::-1]), (25, 25), transform=T.PERSPECTIVE)
    # elif state is 2:
    #     frame.draw_image("img/arr.png", tuple(machine["areas"]["author"][:2][::-1]), (25, 25), transform=T.PERSPECTIVE)
    # elif state is 3:
    #     frame.draw_image("img/arr.png", tuple(machine["areas"]["art"][:2][::-1]), (25, 25), transform=T.PERSPECTIVE)
    # elif state is 4:
    #     frame.draw_image("img/arr.png", tuple(machine["areas"]["publishers"][:2][::-1]), (25, 25), transform=T.PERSPECTIVE)
    
    return frame


if __name__ == "__main__":
    # Parse CLI arguments
    args = prepare_arguments()

    # Setup VideoCapture
    cap = Stream(args.source, args.type)
    
    # Init AugumentAPI instance based on config
    augument = AugumentAPI(args.config)
    augument.outline_detection()
    augument.show_fps()
    # augument.add_layer(draw_stats)

    # Run 
    augument.run(cap)
