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

def prepare_mqtt_client():
    client = ClientMQTT()
    client.connect()

    client.set_default_parameters({"LED": "OFF"})
    client.register_handler(
        "arduino/button",
        lambda params, payload: {**params, "LED": payload}
    )

    return client


# def draaaw(parameters, layer, matrix=None):
#     layer.draw_rectangle((0,70), (100, 37), (255,255,255), coords_unit="pixel")
#     layer.draw_text("LED STATE", (20, 150), color=(255, 0, 0), fontSize=1, coords_unit="pixel")
#     layer.draw_text(parameters["LED"], (20, 180), color=(255, 0, 0), fontSize=1, coords_unit="pixel")
#     return layer

def draaaw(parameters, layer):
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

def draw_img(parameters, layer):
    layer.draw_image(img, (10, 5), ("100%", "100%"))
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
    # proc.enable_object_follow()

    client = prepare_mqtt_client()
    proc.set_client(client=client)

    proc.create_layer(name="Test", draw=draaaw, transform=False, follow=True)
    # proc.create_layer(name="Test", draw=draaaw2, follow=True)
    # proc.create_layer(name="Test", draw=draw_img, transform=False, follow=True)

    proc.start()