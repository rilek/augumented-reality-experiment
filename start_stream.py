#!/usr/bin/env python3

import base64
import cv2
import socket
import zmq

cap = cv2.VideoCapture(2)  # init the camera

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT,540)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,24)


context = zmq.Context()
footage_socket = context.socket(zmq.PUB)
footage_socket.bind('tcp://0.0.0.0:5555')


print("Starting stream")
while True:
    try:
        grabbed, frame = cap.read()  # grab the current frame
        # frame = cv2.resize(frame, (320, 240))  # resize the frame
        encoded, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)
        footage_socket.send(jpg_as_text)

    except KeyboardInterrupt:
        print("Exception raised! Exiting...")
        cap.release()
        cv2.destroyAllWindows()
        break