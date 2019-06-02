#!/usr/bin/env python3

import cv2
import zmq
import socket
import base64
import sys
import getopt
import numpy as np
import re
from util import log, error, warning, info



class Stream(object):
    def __init__(self, source=None, source_type="cam"):
        info("Reading from ", source_type, "!")

        if source_type == "cam":
            source = int(source) or 0
            try:
                self.cap = cv2.VideoCapture(source)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720)
                self.release = self.cap.release
                self.read = self.cap.read
            except Exception as e:
                error("Cannot read from ", source_type , "!", err=e)
                print(Exception)

        elif source_type == "file":
            try:
                self.cap = cv2.VideoCapture(source)
                self.release = self.cap.release
                self.read = self.read_from_file
            except Exception as e:
                error("Cannot read from ", source_type ,"!", err=e)
                exit()

        elif source_type == "remote":
            log("Connecting to socket: {}".format(source))
            try:
                # self.context = zmq.Context()
                # self.footage_socket = self.context.socket(zmq.SUB)
                # self.footage_socket.connect(source)
                # self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
                # self.read = self.read_from_stream
                # self.release = lambda: None
                self.cap = cv2.VideoCapture(source)
                self.release = self.cap.release
                self.read = self.cap.read
            except Exception as e:
                error("Cannot connect to socket!", err=e)
                exit()

        elif source_type == "image":
            try:
                self.cap = None
                self.release = lambda *a: None
                self.read = lambda: (True, cv2.imread(source))
            except Exception as e:
                error("Cannot connect to socket!", err=e)
                exit()
        else:
            error("Unknown type of source")

    def read_from_stream(self):
        try:
            frame = self.footage_socket.recv_string()
            img = base64.b64decode(frame)
            npimg = np.fromstring(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            return True, source
        except Exception:
            print("Something is not working")
            return False, None

    def read_from_file(self):
        ret, frame = self.cap.read()

        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        return ret, frame

    def __exit__(self, exec_type, exc_value, traceback):
        self.release()


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


    s = Stream(**kwargs)
    while True:
        try:
            cv2.imshow("Stream", s.read()[1])
            cv2.waitKey(1)
        
        except KeyboardInterrupt:
            cv2.destroyAllWindows()
            break

