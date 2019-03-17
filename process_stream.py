#!/usr/bin/env python3

import sys
import getopt
import requests
import cv2
import numpy as np
import read_stream
import features
import chessboard


def help_print():
    print('./read_stream.py -i <ip> -p <port>')
    sys.exit()


if __name__ == "__main__":
    kwargs = {}

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hi:p:", ["ip=", "port="])
    except getopt.GetoptError:
        help_print()
    
    for opt, arg in opts:
        if opt == '-h':
            help_print()
        elif opt in ("-i", "--ip"):
            kwargs["host"] = arg
        elif opt in ("-p", "--port"):
            kwargs["port"] = arg


    s = read_stream.Stream(**kwargs)
    # chessboard.process_img(s)
    features.process_img(s)
