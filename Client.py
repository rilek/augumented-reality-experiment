import sys
import cv2
import paho.mqtt.client as mqtt
from util import log, error, warning, info, success as u
from functools import partial

class ClientMQTT(object):
    def __init__(self, host="localhost", port=1883):
        client = mqtt.Client()
        self.client = client
        self.host = host
        self.port = port
        self.handlers = dict()
        self.parameters = {"connected": False}
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.user_on_connect = None

    def connect(self):
        try:
            self.client.connect(self.host)
        except Exception as e:
            error("MQTT Connect exception", err=e)

        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        if self.user_on_connect is not None and callable(self.user_on_connect):
            self.user_on_connect(self, client, userdata, flags, rc)
        
        self.default_on_connect(client, userdata, flags, rc)

    def default_on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            info("Successully connected with broker")
            self.parameters = {**self.parameters, "connected": True}
        else:
            error("Bad connection. Returned code=", rc)

    def on_disconnect(self):
        warning("Disconnected from MQTT")

    def on_message(self, client, userdata, msg):
        for event, handlers in self.handlers.items():
            if event == msg.topic:
                payload = msg.payload

                for fn in handlers:
                    try:
                        self.parameters = fn(self.parameters, payload.decode("utf-8"))
                    except Exception as e:
                        error(err=e)
                break

    # SETTERS AND REGISTERS
    def set_on_connect(self, fun):
        self.user_on_connect = fun

    def set_default_parameters(self, params):
        if not isinstance(params, dict):
            raise Exception("Parameters must be a dictionary!")
        
        self.parameters = {**self.parameters, **params}

    def register_handler(self, event, handler):
        if not callable(handler):
            raise Exception("MQTT Client handler must be function!")

        if event in self.handlers:
            self.handlers[event].append(handler)
        else:
            self.client.subscribe(event)
            self.handlers[event] = [handler]

    ## GETTERS
    def get_parameters(self):
        return self.parameters
