#!/usr/bin/env python3

import argparse
import json
import cv2
import numpy as np
from util import log, error, warning, info, success
from Machine import Machine
from AugumentAPI import AugumentAPI
from Detector import Detector
from read_stream import Stream
from Layer2 import Layer
from DrawAPI import draw_rectangle, draw_text, T

def prepare_arguments():
    parser = argparse.ArgumentParser(description='Process video stream')
    parser.add_argument('-s','--source', type=str, default=None,
                        help="""Source of video stream. Can be either ip address with port or file path.
                                \033[1mDefault: 127.0.0.1:8080.\033[0m""")
    parser.add_argument('-t', "--type", type=str, default="cam", choices=["remote", "file", "cam", "image"],
                        help="""Type of source. \033[1mDefault: file\033[0m""")
    parser.add_argument('-c', "--config", type=str, default="config/config.json",
                        help="""Path to configuration file""")
    parser.add_argument('-m', "--matricies", type=str, default="calibration",
                        help="""Path to camera matricies directory""")

    return parser.parse_args()


state = 0

def draw_stats(frame, machine, params):
    # print(params)
    title_coords = tuple(machine["areas"]["author"][:2])
    # frame.draw_rectangle((10, 30), (150, 50), transform=T.FOLLOW)
    # frame.draw_text("LED: {}".format(params["LED"]), (20, 50), transform=T.FOLLOW)
    # frame.draw_text("CONNECTION: {}".format(params["connected"]), (20, 70), transform=T.FOLLOW)
    frame.draw_image("img/arr.png", (200, 200), (25, 25), transform=T.PERSPECTIVE)
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
    augument.add_layer(draw_stats)

    # Run 
    augument.run(cap)
