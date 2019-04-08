#!/usr/bin/env python3

import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import paho.mqtt.client as mqtt
from util import log, error, warning, info, success as u

LED_STATE = "ON"

class Layer(object):
    def __init__(self, name, image):
        self.name = name
        self.__image__ = image

    def __setitem__(self, key, value):
        self.__image__[key] = value

    def __getitem__(self, key):
        return self.__image__[key]

class RelativeLayer(Layer):
    pass

class AbsoluteLayer(Layer):
    pass

def on_message(client, userdata, message):
    global LED_STATE
    log("ON MESSAGE")
    if message.topic == "arduino/button":
        data = str(message.payload.decode("utf-8"))
        print(data)
        LED_STATE = data

def prepareMQTT():
    broker_address="localhost" 

    try:
        log("Connecting to MQTT broker")
        client = mqtt.Client()
        client.connect(broker_address, keepalive=180)
        client.subscribe("arduino/button")
    except Exception as e:
        error("Cannot connect to broker", err=e)
        exit()

    client.on_message=on_message 
    client.loop_start()

def draw_polylines(frame, dst_arr, color=(0, 0, 255), thickness=3):
    return cv2.polylines(frame, dst_arr, True, color, thickness)

### TODO: exctract adding reference img to method
class ImageProcessor(object):
    def __init__(self, cap, reference_image, opts=dict()):                
        if not isinstance(opts, dict):
            error("Options must be an dictionary")
            exit()

        reference_image = cv2.imread(reference_image)
        gray_reference_image = cv2.cvtColor(reference_image, cv2.COLOR_BGR2GRAY)

        global LED_STATE
        self.cap = cap
        self.max_width = 960
        self.max_height = 960
        self.mqtt_client = None
        self.reference_image = reference_image
        self.gray_reference_image = gray_reference_image
        self.fps = int(1000/1000)
        self.descritor_algorithm = "ORB"
        self.matcher_algorithm = "FLANN"
        self.homography = None
        self.follow_object = lambda frame, *a: frame
        self.window_name = "Homography"
        self.layers = []
        self.run = False

        ## Prepare communication with MQTT broker
        ## TODO: Handle lack of communication
        prepareMQTT()

        ## Create descriptor
        self.create_descriptor(self.descritor_algorithm)
        ## Generate keypoints and descriptors for reference image
        self.prepare_reference()
        ## Create keypoints matcher
        self.create_matcher(self.matcher_algorithm)

        self.layer1 = self.create_layer()
       
    def start(self):
        h = self.ref_height
        w = self.ref_width
        self.run = True

        while self.run:
            ret, frame = self.cap.read()
            frame, height, width = \
                ImageProcessor.resize_image(frame, self.max_width, self.max_height)
            kp, desc = self.detect_frame(frame)

            if desc is None:
                self.show_img(homography or frame)
                key = cv2.waitKey(fps)
                if key==27:
                    self.stop()
                continue

            good_points = self.calc_good_points(desc)

            if len(good_points) > 10:
                matrix, mask = self.find_homography(kp, good_points)
                matches_mask = mask.ravel().tolist()

                # Perspective transform
                pts = np.float32([[0, 0], [0, h], [w, h], [w,0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, matrix)
                dst_arr = [np.int32(dst)]

                homography = self.follow_object(frame, dst_arr)

                self.layer1 = self.draw_rectangle(self.layer1, (0,70), (100, 37), (255,255,255), coords_unit="pixel")
                self.layer1 = self.draw_text(self.layer1, "LED STATE", (20, 150), color=(255, 0, 0), fontSize=.5, coords_unit="pixel")
                self.layer1 = self.draw_text(self.layer1, LED_STATE, (20, 180), color=(255, 0, 0), fontSize=.5, coords_unit="pixel")  

                homography = self.draw_layers(homography, matrix, mask, width, height)
                # homography = cv2.resize(homography, (1280, 960))
                self.show_img(homography)
            else:
                self.show_img(frame)

            key = cv2.waitKey(self.fps)
            if key==27:
                self.stop()

        self.cap.release()

    def stop(self):
        self.run = False

    def create_descriptor(self, algorithm):
        if algorithm == "ORB":
            fn = cv2.ORB_create
        else:
            fn = cv2.ORB_create
        self.descriptor = fn()

    def prepare_reference(self):
        self.ref_height, self.ref_width = self.reference_image.shape[:2]
        self.ref_kp, self.ref_desc = self.descriptor.detectAndCompute(self.gray_reference_image, None)

    def create_matcher(self, matcher_algorithm, index_params=None, search_params=None):
        index_params = (index_params or
                        dict(algorithm =6,           # FLANN_INDEX_LSH
                             table_number = 6,       # 12
                             key_size = 12,          # 20
                             multi_probe_level = 1)) # 2
        search_params = search_params or dict(checks=50)
        if matcher_algorithm == "FLANN":
            matcher = cv2.FlannBasedMatcher
        else:
            matcher = cv2.FlannBasedMatcher
        
        self.matcher = matcher(index_params, search_params)

    def follow_object_fn(self, frame, dst_arr):
        return draw_polylines(frame, dst_arr)

    def enable_object_follow(self):
        self.follow_object = self.follow_object_fn

    def show_img(self, frame, name=None):
        cv2.imshow(name or self.window_name, frame)

    def detect_frame(self, frame):
        gframe = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return self.descriptor.detectAndCompute(gframe, None)

    def calc_good_points(self, desc):
        matches = self.matcher.knnMatch(self.ref_desc, desc, k=2)
        good_points = []
        for mn in matches:
                if len(mn) != 2: continue

                m, n = mn
                if m.distance < 0.65 * n.distance:
                    good_points.append(m)
        return good_points

    def find_homography(self, kp, good_points):
        qpts = np.float32([self.ref_kp[m.queryIdx].pt for m in good_points]).reshape(-1, 1, 2)
        tpts = np.float32([kp[m.trainIdx].pt for m in good_points]).reshape(-1, 1, 2)
        return cv2.findHomography(qpts, tpts, cv2.RANSAC, 5.0)

    def create_layer(self, name=None, type="relative"):
        if type == "absolute":
            layer = self.create_absolute_layer(name)
        else:
            layer = self.create_relative_layer(name)

        self.layers.append(layer)
        return layer

    def create_relative_layer(self, name=None):
        name = name if name else "Layer " + str(len(self.layers))
        empty_img = np.zeros([self.ref_height,self.ref_width,3], dtype=np.uint8)
        layer = Layer(name, empty_img)
        # layer = empty_img
        return layer

    def draw_rectangle(self, layer, coords=(0,0), size=(0,0), color=(255,255,255),
                       coords_unit="percentage", size_unit="percentage"):
        x, y = self.calc_coords(coords, coords_unit)
        width, height = self.calc_coords(size, size_unit)
        
        layer[y:y+height, x:width, 0] = color[0]
        layer[y:y+height, x:width, 1] = color[1]
        layer[y:y+height, x:width, 2] = color[2]
        return layer

    def draw_text(self, layer, text, coords, fontSize=1, color=(0,0,0), coords_unit="percentage"):
        coords = self.calc_coords(coords, coords_unit)
               
        cv2.putText(layer, text, coords, cv2.FONT_HERSHEY_SIMPLEX, fontSize, color, int(fontSize*2), cv2.LINE_AA)
        return layer

    def calc_coords(self, values, unit):
        x, y = values
        if unit == "percentage":
            x, y = values[0]*self.ref_width//100, values[1]*self.ref_height//100
        return x, y
    
    def draw_layers(self, homography, matrix, mask, width, height):
        for layer in self.layers: 
            layer1_persp = cv2.warpPerspective(layer, matrix, (width, height))
            
            r, c, ch = layer1_persp.shape
            roi = homography[0:r, 0:c]

            gray_layer1_persp = cv2.cvtColor(layer1_persp, cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(gray_layer1_persp, 10, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)

            homography_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
            img_fg = cv2.bitwise_and(layer1_persp, layer1_persp, mask=mask)

            homography = cv2.addWeighted(homography_bg, 1,  img_fg, 1, gamma=0)
        
        return homography

    @staticmethod
    def resize_image(frame, max_width=None, max_height=None):
        height, width = frame.shape[:2]
        if max_width and width > max_width:
            scale = max_width/width
            width = int(width*scale)
            height = int(height*scale)
        if max_height and height > max_height:
            scale = max_height/height
            width = int(width*scale)
            height = int(height*scale)
        frame = cv2.resize(frame, (width, height))
        return frame, height, width



################
## Brute force detection
################

# ## ORB DETECTOR
# orb = cv2.ORB_create()
# kp1, desc1 = orb.detectAndCompute(org, None)
# kp2, desc2 = orb.detectAndCompute(i1, None)

# ## Brute Force matching
# bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
# matches = bf.match(desc1, desc2)
# matches = sorted(matches, key=lambda x:x.distance)

# res = cv2.drawMatches(org, kp1, i1, kp2, matches[:50], None, flags=2)

# cv2.imshow("Match", res)

################


################
## DETECTIONS ONLY
################

# sift = cv2.xfeatures2d.SURF_create()
# orb = cv2.ORB_create()

# kp, _ = orb.detectAndCompute(org, None)

# org = cv2.drawKeypoints(org, kp, None)

# cv2.imshow("Original", org)

################

if __name__ == "__main__":

    # cap = cv2.VideoCapture(0)

    # processStream(cap)



    base = cv2.imread("/home/rafcio/Mgr/img/014.png")
    # base = cv2.resize(base, (240, 320))

    ## Features
    sift = cv2.xfeatures2d.SIFT_create()
    kp1, desc1 = sift.detectAndCompute(cv2.cvtColor(base, cv2.COLOR_BGR2GRAY), None)
    base = cv2.drawKeypoints(base, kp1, base)

    cv2.imshow("IMG", base)

    cv2.waitKey(0)
    cv2.destroyAllWindows()