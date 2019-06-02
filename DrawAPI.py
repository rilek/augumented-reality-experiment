import cv2
import numpy as np


def draw_rectangle(frame, coords, size, color=(255, 255, 255)):
    frame = frame.copy()
    x, y = coords
    w, h = size
    frame[y:y+h, x:x+w] = color

    return frame

def draw_polylines(frame, dst_arr, color=(0, 0, 255), thickness=3):
    frame = frame.copy()
    return cv2.polylines(frame, dst_arr, True, color, thickness)

def draw_text(frame, text, coords, font=cv2.FONT_HERSHEY_SIMPLEX, size=0.35, color=(0,0,0), weight=1, aa=cv2.LINE_AA):
    frame = frame.copy()
    cv2.putText(frame, text, coords, font, size, color, weight, aa)
    return frame


class T:
    """Transform types"""
    FOLLOW=0
    FOLLOW_WITH_ROTATION=1
    PERSPECTIVE=2


class Frame:
    def __init__(self, img, matrix=None, mask=None, ref_size=None):
        self.__img = img
        self.__matrix = matrix
        self.__mask = mask
        self.__ref_size = ref_size

    def draw_rectangle(self, coords, size, color=(255, 255, 255), transform=None):
        frame = self.__img
        w, h = size

        if transform is not None:
            if transform is T.FOLLOW:
                x, y = list(map(int, cv2.perspectiveTransform(np.float32([[coords]]), self.__matrix)[0][0]))            
            else:
                x, y = coords
        else:
            x, y = coords

        frame[y:y+h, x:x+w] = color
        return self


    def draw_polylines(self, dst_arr, color=(0, 0, 255), thickness=3):
        frame = self.__img
        cv2.polylines(frame, dst_arr, True, color, thickness)
        return self


    def draw_text(self, text, coords, font=cv2.FONT_HERSHEY_SIMPLEX, size=0.35, color=(0,0,0), weight=1, aa=cv2.LINE_AA, transform=None):
        frame = self.__img

        if transform is not None:
            if transform is T.FOLLOW:
                coords = tuple(map(int, cv2.perspectiveTransform(np.float32([[coords]]), self.__matrix)[0][0]))

        cv2.putText(frame, text, coords, font, size, color, weight, aa)
        return self
    

    def draw_image(self, img, coords=(0,0), size=None, transform=None):
        img = img if type(img) is not str else cv2.imread(img)

        current = self.__img
        max_y, max_x, _ = current.shape
        if size is not None:
            img = cv2.resize(img, size)
        rows, cols, _ = img.shape

        if transform is T.FOLLOW:
            x, y = tuple(map(int, cv2.perspectiveTransform(np.float32([[coords]]), self.__matrix)[0][0]))
            roi = current[y-rows:y, x:cols+x]
        elif transform is T.PERSPECTIVE:
            img = cv2.warpPerspective(img, self.__matrix, self.__ref_size[::-1])
            y, x = coords
            rows, cols, _ = img.shape
            roi = current[0:rows, 0:cols]
        else:
            y, x = coords
            roi = current[y-rows:y, x:cols+x]

        fin_y = y+rows
        fin_x = x+cols

        print(roi.shape)

        imggray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        ret, mask = cv2.threshold(imggray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        current_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
        img_fg = cv2.bitwise_and(img,img,mask = mask)
        dst = cv2.addWeighted(current_bg,1,img_fg,1,gamma=0)


        if transform is not T.PERSPECTIVE:
            # Crop image if exceeds image size
            if y < 0:
                dst = dst[abs(y):]
            if x < 0:
                dst = dst[:, abs(x):]
            if fin_y > max_y:
                dst = dst[:max_y-fin_y]
            if fin_x > max_x :
                dst = dst[:, :max_x-fin_x]

            self.__img[max(y-rows, 0):min(y, max_y), max(x, 0):min(fin_x, max_x)] = dst
        else:
            self.__img = dst


        return self

    def get_image(self):
        return self.__img
