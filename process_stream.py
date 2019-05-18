#!/usr/bin/env python3

import sys
import getopt
import argparse
import requests
import cv2
import numpy as np
import read_stream
import features
# import chessboard
from util import log, error, warning, info, success
from Layer import Layer, RelativeLayer, AbsoluteLayer, Layer2
from Client import ClientMQTT


stage = -1


def prepare_arguments():
    parser = argparse.ArgumentParser(description='Process video stream')
    parser.add_argument('-s','--source', type=str, default=None,
                        help="""Source of video stream. Can be either ip address with port or file path.
                                \033[1mDefault: 127.0.0.1:8080.\033[0m""")
    parser.add_argument('-r', "--reference", type=str, default=None,
                        help="""Path to image that acts as reference.""")
    parser.add_argument('-t', "--type", type=str, default="cam", choices=["remote", "file", "cam"],
                        help="""Type of source. \033[1mDefault: file\033[0m""")

    return parser.parse_args()

def on_connect(*args):
    global stage
    stage = 0
    return true

def prepare_mqtt_client():
    client = ClientMQTT()
    client.set_on_connect(on_connect)
    client.connect()

    client.set_default_parameters({"LED": "OFF"})
    client.register_handler(
        "arduino/button",
        lambda params, payload: {**params, "LED": payload}
    )
    client.set_default_parameters({"Ohm": "0"})
    client.register_handler(
        "arduino/ohm",
        lambda params, payload: {**params, "Ohm": payload}
    )

    return client


def draaaw(parameters, layer, matrix=None):
    if not ("connected" in parameters and parameters["connected"]):
        layer.draw_rectangle((10,10), (100, 300), (255,255,255))
        layer.draw_text("Loading...", (40, 20), color=(0,0,255), fontSize=.75)
    else:
        parameters = parameters.copy()
        del parameters["connected"]
        layer.draw_rectangle((10,10), ((len(parameters))*20+50, 300), (255,255,255))
        layer.draw_text("Parameters:", (35, 20), color=(15, 15, 15), fontSize=.5)
        layer.draw_text("LED: " +parameters["LED"], (60, 20), color=(15, 15, 15), fontSize=.5)
        layer.draw_text("Ohm: " +parameters["Ohm"], (80, 20), color=(15, 15, 15), fontSize=.5)
    return layer

def draaaw3(parameters, layer):
    layer.draw_titled_area("Author", (10, 100), (70, 210), (0,0,255), thickness=1)
    layer.draw_titled_area("Title", ("13%", 10), (180, "90%"), (0,0,255), thickness=1)
    layer.draw_titled_area("Publishers", ("85%", "50%"), ("13%", "50%"), (0,0,255), thickness=1)
    layer.draw_titled_area("Art", ("45%", "-10%"), ("55%", "110%"), (0,0,255), thickness=1)
    return layer


def draaaw2(parameters, layer):
    layer.draw_rectangle((20,20), (180, 70), (255,255,255))
    layer.draw_text("LED STATE", (50, 30), color=(255, 0, 0), fontSize=.5)
    layer.draw_text(parameters["LED"], (70, 30), color=(255, 0, 0), fontSize=.5)
    return layer

img = cv2.imread("img/original.jpg")
img = cv2.resize(img, (50, 50))

def draw_img(parameters, layer):
    layer.draw_image(img, (20, 20), ("100%", "100%"))
    return layer

def presentation(parameters, layer, matrix=None):
    global stage

    # print(parameters)

    if stage is 0 and parameters["LED"] == "ON":
        stage = 1
    elif stage is 1 and float(parameters["Ohm"]) > 1000:
        stage = 2

    print(stage)
    
    layer.draw_rectangle((10,10), (160, 300), (255,255,255))
    
    layer.draw_text("Parameters:", (35, 20), color=(15, 15, 15), fontSize=.5)
    layer.draw_text("LED: " +parameters["LED"], (60, 20), color=(15, 15, 15), fontSize=.5)
    layer.draw_text("Ohm: " +parameters["Ohm"], (80, 20), color=(15, 15, 15), fontSize=.5)

    if stage is -1:
        layer.draw_text("Turn on the device", (120, 20), fontSize= 0.5, color=(15, 15, 225))
    elif stage is 0:
        layer.draw_text("Turn on the LED", (120, 20), fontSize= 0.5, color=(15, 15, 225))
    elif stage is 1:
        layer.draw_text("Set resistance over 1k OHM", (120, 20), fontSize= 0.5, color=(15, 15, 225))
    elif stage is 2:
        layer.draw_text("Device is ready to go!", (120, 20), fontSize= 0.5, color=(15, 15, 225))

    return layer


if __name__ == "__main__":
    args = prepare_arguments()
    info("Initial arguments: ", args)

    if args.type == "cam":
        try:
            int(args.source)
        except Exception as e:
            error("With cam type source must be an int", err=e)
            log("Exit")
            exit()

    if not args.reference:
        reference_image = "/home/rafcio/Mgr/img/base.jpg"

    log("Prepare stream object")
    stream = read_stream.Stream(args.source, args.type)

    log("Start processing")
    proc = features.ImageProcessor(stream, reference_image=reference_image)
    proc.enable_object_follow()

    client = prepare_mqtt_client()
    proc.set_client(client=client)


    proc.create_layer(name="Test", draw=presentation, transform=False, follow=False)
    # proc.create_layer(name="Test", draw=draw_img, follow=True)
    # proc.create_layer(name="Test", draw=draw_img, transform=True)

    proc.start()