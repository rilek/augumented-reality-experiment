import cv2
import numpy as np

cam_matrix = np.loadtxt("mtx.txt")

class Layer2(object):
    """
    Acts as layer of final image. Can follow object and transform to match its perspective

    Attributes
    ----------
    name : str
        Name of layer
    image : array
        3-dimensional array of <0 ... 255> int values. Represents image.
    size : (int, int)
        Represents height and width of drawing area
    transform : bool
        Should the image be transformed to match object perspective
    follow : bool
        Should layer coordinates follow top left corner of an object
    ref_size : (int, int) : (height, width)
        Size of reference image. Neccessary to predict precentage size of following drawings
    """
    all_layers = []

    def __init__ (self, name, draw, image=None, size=None, transform=False, follow=False, ref_size=(1, 1)):
        self.__name = name
        
        # if image is not None:
        #     self.__image = image
        # else:
        self.__image = np.zeros([size[0], size[1], 3], dtype=np.uint8)
        self.__default_image = self.__image
        self.__draw = draw
        self.__size = size
        self.__default_size = size
        self.__perspective = (1, 1)
        self.__ref_size = ref_size if follow else size

        # Should the layer be transformed to object perspective
        self.__transform = transform
        # Should layer coordinates zero point follow top left corner of object
        self.__follow = follow
        self.matrix = None

        Layer2.all_layers.append(self)


    @property
    def size(self):
        return self.__size

    @size.setter
    def size(self, value):
        if len(value) is not 2:
            raise ValueError("Size must be 2 item list")
        elif not isinstance(value[0], int) or not isinstance(value[1], int):
            raise TypeError("Size values must be int")
        self.__size = value


    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if not isinstance(value, str):
            raise TypeError("Name must be string")
        self.__name = value


    @property
    def draw(self):
        return self.__draw

    @draw.setter
    def draw(self, value):
        if not callable(obj):
            raise TypeError("Draw property must be function")
        self.__draw = draw


    @property
    def image(self):
        return self.__image
    
    @image.setter
    def image(self, value):
        self.__image = value
        
    
    @property
    def transform(self):
        return self.__transform
    
    @transform.setter
    def transform(self, value):
        if not isinstance(value, bool):
            raise TypeError("Transform must be bool")
        self.__transform = value
        
    
    @property
    def follow(self):
        return self.__follow

    @follow.setter
    def follow(self, value):
        if not isinstance(value, bool):
            raise TypeError("Follow must be bool")
        self.__follow = value           


    @property
    def ref_size(self):
        return self.__ref_size

    @ref_size.setter
    def ref_size(self, value):
        self.__ref_size = value     


    @property
    def perspective(self):
        return self.__perspective

    @perspective.setter
    def perspective(self, value):
        if not (len(value) is 2):
            raise ValueError("Perspective must be 2 item list")

        self.__perspective = value

    @property
    def default_image(self):
        return self.__default_image

    def update_perspective(self, matrix):
        self.matrix = matrix
        if matrix is not None:
            perspective = cv2.perspectiveTransform(np.float32([[[0, 0]], [self.ref_size]]), matrix)
            coords = perspective[0][0]
            coords = [int(x) for x in coords]
            coords.reverse()
            perspective = (perspective[1][0][::-1] - coords)[::-1]
            perspective = [x/self.ref_size[i] for i, x in enumerate(perspective)]
            self.perspective = perspective
        else:
            coords = (0, 0)
            self.perspective = (1, 1)

    def parse_coordinate(self, coord, reference):
        if not isinstance(coord, int):
            if coord.endswith("%"):
                coord = (self.ref_size[reference] * int(coord[:-1]) // 100)
            elif coord.endswith("px"):
                coord = int(coord[:-2])
            else:
                raise ValueError("Unknown coordinate value")

        return coord

    def calc_coords(self, values):
        values = [self.parse_coordinate(coord, i) for i, coord in enumerate(values)]
        if self.follow:
            tmp = cv2.perspectiveTransform(np.float32([[values]]), self.matrix)
            values = tmp[0][0]
            ## perspectiveTransform returns coordinates in reversed order
            x, y = [int(x) for x in values]
        else:
            y, x = values
        return y, x

    def draw(self, matrix=None):
        self.image = self.default_image.copy()
        if matrix is not None:
            self.matrix = matrix
            self.update_perspective(matrix)

        self.__draw(self)
        # num, Rs, Ts, Ns = cv2.decomposeHomographyMat(self.matrix, cam_matrix)
        return self.image

    def draw_image(self, img, coords=(0,0), size=("100%", "100%")):
        if self.transform is False:
            current = self.image
            max_y, max_x, _ = current.shape
            rows, cols, _ = img.shape
            y, x = self.calc_coords(coords)
            fin_y = y+rows
            fin_x = x+cols
            height, width = self.calc_coords((rows,cols))
            roi = current[0:rows, 0:cols]

            imggray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            ret, mask = cv2.threshold(imggray, 10, 255, cv2.THRESH_BINARY)
            mask_inv = cv2.bitwise_not(mask)
            current_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
            img_fg = cv2.bitwise_and(img,img,mask = mask)
            dst = cv2.add(current_bg,img_fg)

            # Crop image its exceeds image size
            if y < 0:
                dst = dst[abs(y):]
            if x < 0:
                dst = dst[:, abs(x):]
            if fin_y > max_y:
                dst = dst[:max_y-fin_y]
            if fin_x > max_x :
                dst = dst[:, :max_x-fin_x]

            current[max(y, 0):min(fin_y, max_y), max(x, 0):min(fin_x, max_x)] = dst
            self.image = current
        else:
            self.image = img
        return self.image

    def draw_rectangle(self, coords=(0,0), size=(0,0), color=(255,255,255)):
        layer = self.image
        y, x = self.calc_coords(coords)
        height, width = self.calc_coords(size)
        
        layer[y:y+height, x:x+width, 0] = color[0]
        layer[y:y+height, x:x+width, 1] = color[1]
        layer[y:y+height, x:x+width, 2] = color[2]
        self.image = layer

    def draw_polylines(self, coords=(0,0), size=(0,0), color=(255,255,255), thickness=1):
        image = self.image
        y, x = self.calc_coords(coords)
        height, width = self.calc_coords(size)

        dst_arr = [np.array([[x, y], [x, y+height], [x+width, y+height], [x+width, y]], dtype=np.int32)]
        return cv2.polylines(image, dst_arr, True, color, thickness)

    def draw_text(self, text, coords, fontSize=1, color=(0,0,0)):
        y, x = self.calc_coords(coords)
        cv2.putText(self.image, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, fontSize, color, int(fontSize*2), cv2.LINE_AA)

    def draw_titled_area(self, title="", coords=(0,0), size=(0,0), color=(255,255,255), thickness=1):
        zpy, zpx = self.zero_point
        _y, _x = self.calc_coords(coords)
        y, x = _y + zpy, _x + zpx 
        size = self.calc_coords(size)
        r = lambda b, a: (_y+b, _x+a)

        self.draw_polylines(coords, size, (0,0,255), thickness=2)
        self.draw_rectangle(r(-15, 0), (15, len(title)*10), (0,0,255))
        self.draw_text(title,coords, color=(255,255,255), fontSize=.5)

        return self.image

















class Layer(object):
    all_layers = []

    def __init__(self, name, image, draw_fn=lambda:None, image_size=(0,0), transform=False):
        self.name = name
        self.image = image
        self.fn = draw_fn
        self.img_width, self.img_height = image_size
        self.transform = transform

        Layer.all_layers.append(self)

    def __setitem__(self, key, value):
        self.image[key] = value

    def __getitem__(self, key):
        return self.image[key]

    def draw_fn(self, matrix=None):
        self[:] = 0
        if matrix is not None:
            return self.fn(self, matrix).image
        else:
            return self.fn(self).image

    def set_draw_function(self, draw_fn):
        self.draw_fn = lambda: draw_fn(self).image

    def should_transform(self):
        return self.transform

    def draw_rectangle(self, coords=(0,0), size=(0,0), color=(255,255,255),
                       coords_unit="percentage", size_unit="percentage", matrix=None, zero_coords=None,
                       max_size=None):
        layer = self.image
        x, y = self.calc_coords(coords, coords_unit)
        width, height = self.calc_coords(size, size_unit, max_size=max_size)

        if matrix is not None:
            zero_x, zero_y = cv2.perspectiveTransform(np.float32([[[0, 0]]]), matrix)[0][0] if matrix is not None else (0, 0)
        elif zero_coords is not None:
            zero_x, zero_y = zero_coords
        else:
            zero_x, zero_y = 0, 0
        x, y = int(zero_x + x), int(zero_y + y)
        
        layer[y:y+height, x:x+width, 0] = color[0]
        layer[y:y+height, x:x+width, 1] = color[1]
        layer[y:y+height, x:x+width, 2] = color[2]
        return layer

    def draw_text(self, text, coords, fontSize=1, color=(0,0,0), coords_unit="percentage", matrix=None, zero_coords=None):
        x, y = self.calc_coords(coords, coords_unit)
        
        if matrix is not None:
            zero_x, zero_y = cv2.perspectiveTransform(np.float32([[[0, 0]]]), matrix)[0][0] if matrix is not None else (0, 0)
        elif zero_coords is not None:
            zero_x, zero_y = zero_coords
        else:
            zero_x, zero_y = 0, 0

        x, y = int(zero_x + x), int(zero_y + y)
        cv2.putText(self.image, text, (x,y), cv2.FONT_HERSHEY_SIMPLEX, fontSize, color, int(fontSize*2), cv2.LINE_AA)

    def draw_image(self, img, coords=(0,0), size=(100, 100),
                   coords_unit="percentage", size_unit="percentage"):
        self.image = img

    def draw_polylines(self, coords=(0,0), size=(0,0), color=(255,255,255),
                       coords_unit="percentage", size_unit="percentage", thickness=1,
                       matrix=None, zero_coords=None, max_size=None):
        image = self.image
        x, y = self.calc_coords(coords, coords_unit)
        width, height = self.calc_coords(size, size_unit, max_size=max_size)

        if matrix is not None:
            zero_x, zero_y = cv2.perspectiveTransform(np.float32([[[0, 0]]]), matrix)[0][0] if matrix is not None else (0, 0)
        elif zero_coords is not None:
            zero_x, zero_y = zero_coords
        else:
            zero_x, zero_y = 0, 0

        x, y = int(zero_x + x), int(zero_y + y)

        dst_arr = [np.array([[x,y], [x+width,y], [x+width,y+height], [x,y+height]], dtype=np.int32)]

        return cv2.polylines(image, dst_arr, True, color, thickness)

    def draw_titled_area(self, coords=(0,0), size=(0,0), color=(255,255,255),
                         coords_unit="percentage", size_unit="percentage", thickness=1,
                         matrix=None, title=""):
        x, y = self.calc_coords(coords, coords_unit)
        width, height = size
        perspective = cv2.perspectiveTransform(np.float32([[[x, y]], [[width, height]]]), matrix)
        zero_coords = perspective[0][0] if matrix is not None else (0, 0)
        max_size = np.array(perspective[1][0], np.int32) if matrix is not None else None

        zero_x, zero_y = zero_coords
        x, y = int(zero_x + x), int(zero_y + y)

        self.draw_polylines((0, 0), size, (0,0,255), matrix=matrix, thickness=2, size_unit=size_unit)
        # self.draw_rectangle((0, 0), (100, 100), zero_coords=zero_coords, max_size=max_size, size_unit="percentage")

        self.draw_rectangle((0, -20), (70, 20), (0,0,255), size_unit="pixel", coords_unit="pixel", zero_coords=zero_coords)
        self.draw_text(title,(0, -5), color=(255,255,255), fontSize=.5, zero_coords=zero_coords, coords_unit="pixel")

        return self.image


    def calc_coords(self, values, unit, max_size=None):
        x, y = values
        if unit == "percentage":
            img_width, img_height = max_size if max_size is not None else (self.img_width, self.img_height)
            x, y = values[0]*img_width//100, values[1]*img_height//100

        return x, y

class RelativeLayer(Layer):
    def __init__(self, name, image, draw_fn=lambda: None, image_size=(0,0),transform=False):
        Layer.__init__(self, name, image, draw_fn, image_size, transform)

class AbsoluteLayer(Layer):
    def __init__(self, name, image, draw_fn=lambda: None, image_size=(0,0),transform=False):
        Layer.__init__(self, name, image, draw_fn, image_size, transform)
