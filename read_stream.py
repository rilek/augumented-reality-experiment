#!/usr/bin/env python3

import cv2
import zmq
import socket
import base64
import sys
import getopt
import numpy as np


class Stream(object):
    def __init__(self, host="127.0.0.1", port=5555):
        addr = "tcp://{}:{}".format(host, port)
        print("Connecting to socket: {}".format(addr))
        try:
            self.context = zmq.Context()
            self.footage_socket = self.context.socket(zmq.SUB)
            self.footage_socket.connect(addr)
            self.footage_socket.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))
        except Exception:
            print("Cannot connect to socket!")

    def read(self):
        try:
            frame = self.footage_socket.recv_string()
            img = base64.b64decode(frame)
            npimg = np.fromstring(img, dtype=np.uint8)
            source = cv2.imdecode(npimg, 1)
            return True, source
        except Exception:
            print("Something is not working")
            return False, None

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

