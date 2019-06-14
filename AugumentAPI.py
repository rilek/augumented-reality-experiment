
import time
import cv2
import numpy as np
from Detector import Detector
from Machine import Machine
from Client import ClientMQTT
from Store import Store
from read_stream import Stream
from util import read_json, resize_to_max
from DrawAPI import draw_polylines, draw_text, Frame

class AugumentAPI(object):
    def __init__(self, config_path):

        # Load config
        config = read_json(config_path)
        server_config = config["server"]

        self.__config = config

        # Set detector for only machine 
        self.__machine = config["machines"][0]
        self.__ref_image = cv2.imread(self.__machine["ref"])
        self.__detector = Detector(self.__machine)
        self.__pts = self.__detector.get_pts()
        self.__run = False
        self.__outline_detection = False
        self.__show_fps = False
        self.__last_timestamp = None

        self.__delay = 1000 // config["fps"]
        self.__frame_name = "Homography"
        self.__layers = []
        self.__statics = []
        
        self.__topics = server_config["topics"] if "topics" in server_config else None

        self.__store = self.setup_store(self.__topics) 
        self.__client = self.setup_client(server_config)

    def run(self, cap):
        self.__run = True

        while self.__run:
            ret, frame = cap.read()
            if not ret:
                self.stop()
                break

            result = resize_to_max(frame, (1000, 1000))

            # Detect matchine
            found, matrix, mask = self.__detector.detect(result)

            # If machine was found, parse frame
            if found:
                result = self.parse_frame(result, matrix, mask)

            # Show final frame
            cv2.imshow(self.__frame_name, result)
            
            # Wait for another frame, or break if Q button was pressed
            if cv2.waitKey(self.__delay) & 0xFF == ord('q'):
                self.stop()

    def stop(self):
        self.__run = False

    def outline_detection(self):
        self.__outline_detection = True

    def show_fps(self):
        self.__show_fps = True

    def parse_frame(self, frame, matrix, mask):
        result = Frame(frame, matrix=matrix, mask=mask, ref_size=self.__ref_image.shape)
        params = self.__store.get_state()

        # Perspective transform
        if self.__outline_detection:
            dst = cv2.perspectiveTransform(self.__pts, matrix)
            dst_arr = [np.int32(dst)]
            result.draw_polylines(dst_arr)

        for draw_function in self.__layers:
            result = draw_function(result, self.__machine, params)

        for draw_function in self.__statics:
            result = draw_function(result, self.__machine, params)

        if self.__show_fps:
            new_timestamp = time.time()
            if self.__last_timestamp is not None:
                old_timestamp = self.__last_timestamp
                fps = 1 / (new_timestamp - old_timestamp)
                result.draw_text("FPS: {:0.0f}".format(fps), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,0,0), 2, cv2.LINE_AA)
                result.draw_text("FPS: {:0.0f}".format(fps), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0,255,255), 1, cv2.LINE_AA)
            self.__last_timestamp = new_timestamp

        return result.get_image()

    def setup_store(self, topics=None):
        store = Store(topics)

        if topics:
            self.__topics = topics
        
        return store

    def setup_client(self, server_config):
        store = self.__store

        client = ClientMQTT(host=server_config["host"], port=server_config["port"])

        # For each topic in configuration register handler and set optional default value
        if self.__topics:
            for topic in self.__topics:
                
                # Set default value if exists
                if "default" in topic:
                    store.set_default_parameters({topic["name"]: topic["default"]})
                client.register_handler(topic["topic"], self.handle_message)
        
        client.connect()

        return client

    def handle_message(self, event, payload):
        param_name = self.__store.translate_event(event)
        param_type = self.__store.event_type(event)
        
        if param_type == "int":
            payload = int(payload)

        self.__store.set_state(param_name, payload)
        return None

    def add_layer(self, draw_function):
        self.__layers.append(draw_function)

    def add_static(self, draw_function):
        self.__statics.append(draw_function)
