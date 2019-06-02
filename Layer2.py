

class Layer(object):
    
    @staticmethod
    def draw_rectangle(frame, coords, size, color=(255, 255, 255)):
        frame = frame.copy()
        x, y = coords
        w, h = size
        
        frame[y:y+h, x:x+w, :] = color
        return frame

class Rectangle(object):
    def __init__(self):
        pass

    def draw(self, frame):
        pass