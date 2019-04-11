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
    proc.set_parameters({"LED": "ON"})
    # proc.set_handler(
    #     "arduino/button",
    #     lambda parameters:
    #         error("ERRROR")
    # )
    proc.start()
