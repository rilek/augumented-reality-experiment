from util import find_first


class Store(object):
    def __init__(self, topics):
        self.__state = dict()
        self.__topics = topics

    def set_state(self, param, value):
        self.__state = {**self.__state, param: value}
        print("STATE CHANGED (" + param, ": ", str(value) +"). NEW STATE:")
        print(self.__state)

    def get_state(self):
        return self.__state

    def set_default_parameters(self, params):
        if not isinstance(params, dict):
            raise Exception("Parameters must be a dictionary!")
        
        self.__state = {**self.__state, **params}

    def translate_event(self, event):
        result = find_first(
            lambda item: "topic" in item and item["topic"] == event,
            self.__topics
        )

        if result:    
            result = result["name"]
            return result
        else:
            raise ValueError("No such topic name")
            return