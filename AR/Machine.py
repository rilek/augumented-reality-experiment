import cv2

class Machine(object):
    all = []

    def __init__(self, machine):
        self.__name = machine["name"]
        self.__ref_image = cv2.imread(machine["ref"])
        self.__areas = machine["areas"]

        Machine.all.append(self)

    @property
    def name(self):
        return self.__name

    @property
    def areas(self):
        return self.__areas

    @property
    def ref_image(self):
        return self.__ref_image

    def get_area(self, label):
        areas = self.__areas
        if not label in areas:
            raise ValueError("No area named " + label)

        return areas[label]
