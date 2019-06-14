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
        self.__handlers = dict()
        self.__connected = False
        self.__subscribed = False
        self.client.on_message = self.on_message
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.user_on_connect = None
        self.__subscribe_queue = set([])

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
            self.__connected = True
            for ev in self.__subscribe_queue:
                self.client.subscribe(ev)
            for handler in self.__handlers["on_connect"]:
                handler("on_connect", True)
        else:
            error("Bad connection. Returned code=", rc)

    def on_disconnect(self):
        warning("Disconnected from MQTT")

        for handler in self.__handlers["on_disconnect"]:
            handler("on_disconnect", False)

    def on_message(self, client, userdata, msg):
        for event, handlers in self.__handlers.items():
            if event == msg.topic:
                payload = msg.payload

                for fn in handlers:
                    try:
                        fn(event, payload.decode("utf-8"))
                    except Exception as e:
                        error(err=e)
                break

    # SETTERS AND REGISTERS
    def set_on_connect(self, fun):
        self.user_on_connect = fun

    def register_handler(self, event, handler):
        if not callable(handler):
            raise Exception("MQTT Client handler must be function!")

        if event in self.__handlers:
            self.__handlers[event].append(handler)
        else:
            if event is not "on_connect" and event is not "on_disconnect":
                if self.__connected:
                    self.client.subscribe(event)
                else:
                    self.__subscribe_queue.add(event)
            self.__handlers[event] = [handler]
