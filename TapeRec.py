import numpy as np
import cv2
import math
from enum import Enum

class GripPipeline:
    """
    An OpenCV pipeline generated by GRIP.
    """

    def __init__(self):
        """initializes all values to presets or None if need to be set
        """

        self.__hsv_threshold_hue = [0.0, 180.0]
        self.__hsv_threshold_saturation = [0.0, 130.5050505050505]
        self.__hsv_threshold_value = [249.95503597122303, 255.0]

        self.hsv_threshold_output = None

        self.__find_contours_input = self.hsv_threshold_output
        self.__find_contours_external_only = False

        self.find_contours_output = None

        self.__filter_contours_contours = self.find_contours_output
        self.__filter_contours_min_area = 100.0
        self.__filter_contours_min_perimeter = 200.0
        self.__filter_contours_min_width = 50.0
        self.__filter_contours_max_width = 100.0
        self.__filter_contours_min_height = 0.0
        self.__filter_contours_max_height = 200.0
        self.__filter_contours_solidity = [0, 100]
        self.__filter_contours_max_vertices = 1000000.0
        self.__filter_contours_min_vertices = 0.0
        self.__filter_contours_min_ratio = 0.0
        self.__filter_contours_max_ratio = 1000.0

        self.filter_contours_output = None

        self.__convex_hulls_contours = self.filter_contours_output

        self.convex_hulls_output = None


    def process(self, source0):
        """
        Runs the pipeline and sets all outputs to new values.
        """
        # Step HSV_Threshold0:
        self.__hsv_threshold_input = source0
        (self.hsv_threshold_output) = self.__hsv_threshold(self.__hsv_threshold_input, self.__hsv_threshold_hue, self.__hsv_threshold_saturation, self.__hsv_threshold_value)

        # Step Find_Contours0:
        self.__find_contours_input = self.hsv_threshold_output
        (self.find_contours_output) = self.__find_contours(self.__find_contours_input, self.__find_contours_external_only)

        # Step Filter_Contours0:
        self.__filter_contours_contours = self.find_contours_output
        (self.filter_contours_output) = self.__filter_contours(self.__filter_contours_contours, self.__filter_contours_min_area, self.__filter_contours_min_perimeter, self.__filter_contours_min_width, self.__filter_contours_max_width, self.__filter_contours_min_height, self.__filter_contours_max_height, self.__filter_contours_solidity, self.__filter_contours_max_vertices, self.__filter_contours_min_vertices, self.__filter_contours_min_ratio, self.__filter_contours_max_ratio)

        # Step Convex_Hulls0:
        self.__convex_hulls_contours = self.filter_contours_output
        (self.convex_hulls_output) = self.__convex_hulls(self.__convex_hulls_contours)


    @staticmethod
    def __hsv_threshold(input, hue, sat, val):
        """Segment an image based on hue, saturation, and value ranges.
        Args:
            input: A BGR numpy.ndarray.
            hue: A list of two numbers the are the min and max hue.
            sat: A list of two numbers the are the min and max saturation.
            lum: A list of two numbers the are the min and max value.
        Returns:
            A black and white numpy.ndarray.
        """
        out = cv2.cvtColor(input, cv2.COLOR_BGR2HSV)
        return cv2.inRange(out, (hue[0], sat[0], val[0]),  (hue[1], sat[1], val[1]))

    @staticmethod
    def __find_contours(input, external_only):
        """Sets the values of pixels in a binary image to their distance to the nearest black pixel.
        Args:
            input: A numpy.ndarray.
            external_only: A boolean. If true only external contours are found.
        Return:
            A list of numpy.ndarray where each one represents a contour.
        """
        if(external_only):
            mode = cv2.RETR_EXTERNAL
        else:
            mode = cv2.RETR_LIST
        method = cv2.CHAIN_APPROX_SIMPLE
        contours, hierarchy =cv2.findContours(input, mode=mode, method=method)
        return contours

    @staticmethod
    def __filter_contours(input_contours, min_area, min_perimeter, min_width, max_width,
                        min_height, max_height, solidity, max_vertex_count, min_vertex_count,
                        min_ratio, max_ratio):
        """Filters out contours that do not meet certain criteria.
        Args:
            input_contours: Contours as a list of numpy.ndarray.
            min_area: The minimum area of a contour that will be kept.
            min_perimeter: The minimum perimeter of a contour that will be kept.
            min_width: Minimum width of a contour.
            max_width: MaxWidth maximum width.
            min_height: Minimum height.
            max_height: Maximimum height.
            solidity: The minimum and maximum solidity of a contour.
            min_vertex_count: Minimum vertex Count of the contours.
            max_vertex_count: Maximum vertex Count.
            min_ratio: Minimum ratio of width to height.
            max_ratio: Maximum ratio of width to height.
        Returns:
            Contours as a list of numpy.ndarray.
        """
        output = []
        for contour in input_contours:
            x,y,w,h = cv2.boundingRect(contour)
            if (w < min_width or w > max_width):
                continue
            if (h < min_height or h > max_height):
                continue
            area = cv2.contourArea(contour)
            if (area < min_area):
                continue
            if (cv2.arcLength(contour, True) < min_perimeter):
                continue
            hull = cv2.convexHull(contour)
            solid = 100 * area / cv2.contourArea(hull)
            if (solid < solidity[0] or solid > solidity[1]):
                continue
            if (len(contour) < min_vertex_count or len(contour) > max_vertex_count):
                continue
            ratio = (float)(w) / h
            if (ratio < min_ratio or ratio > max_ratio):
                continue
            output.append(contour)
        return output

    @staticmethod
    def __convex_hulls(input_contours):
        """Computes the convex hulls of contours.
        Args:
            input_contours: A list of numpy.ndarray that each represent a contour.
        Returns:
            A list of numpy.ndarray that each represent a contour.
        """
        output = []
        for contour in input_contours:
            output.append(cv2.convexHull(contour))
        return output


# Self written code
cap = cv2.VideoCapture(0)
eyes = GripPipeline()

class Tape:
    def __init__(self, cnt):
        self.center = None
        self.angle = None
        self.area = None
        self.vertices =  np.int0(cv2.boxPoints(cv2.minAreaRect(cnt)))
        self.sortedVerticesX = []
        self.sortedVerticesY = []
        self.contour = cnt

    def getCenter(self):
        M = cv2.moments(self.contour)
        self.center = (int(M['m10']/M['m00']), int(M['m01']/M['m00']))
        return self.center

    def getArea(self):
        M = cv2.moments(self.contour)
        self.area = M['m00']
        return self.area

    def getSortedVerticesX(self):
        def x(list):
            return list[1]
        self.sortedVerticesX = list(sorted(self.vertices, key = x))
        return self.sortedVerticesX

    def getSortedVerticesY(self):
        def Y(list):
            return list[1]
        self.sortedVerticesY = sorted(self.vertices, key = Y)
        return self.sortedVerticesY

    def getAngle(self):
        self.angle = math.degrees(math.atan2(self.getSortedVerticesX()[1][0]-self.getSortedVerticesX()[0][0], self.getSortedVerticesX()[1][1]-self.getSortedVerticesX()[0][1]))
        return self.angle

    def getVertices(self):
        return self.vertices

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    uselessThing, shape = cap.read()
    unneeded, boundedImg = cap.read()

    # access the generated code
    eyes.process(frame)

    tapeNum = 0
    numOftape = len(eyes.filter_contours_output)
    font = cv2.FONT_HERSHEY_SIMPLEX
    boundedImg = cv2.putText(boundedImg,'# of tapes: '+str(numOftape),(10,12), font, 0.5,(255,255,255),1,cv2.LINE_AA)
    tapes = []
    sortedTapes = []
    groups = []

    if numOftape >0:
        for borders in eyes.filter_contours_output:
            tape = Tape(borders)
            tapes.append(tape)
            tapeNum += 1
            boundedImg = cv2.drawContours(boundedImg,[tape.vertices],0,(0,0,255),2)
                # Gets statistics on the rectangle
            boundedImg=cv2.circle(boundedImg, tape.getCenter(), 5, (0,255,0), thickness=-1, lineType=8, shift=0)
            boundedImg = cv2.putText(boundedImg,'Tape#: '+str(tapeNum)+', Center at: '+str(tape.getCenter()[0])+','+str(tape.getCenter()[1])+'Angle: '+str(math.floor(tape.getAngle())),(tape.vertices[0][0],tape.vertices[0][1]), font, 0.4,(255,255,255),1,cv2.LINE_AA)

            def getLeftCorner(list):
                return list.getSortedVerticesX()[0][1]
            sortedTapes = sorted(tapes, key = getLeftCorner)

            # Grouping

            for i in range(len(tapes)):
                for j in range(len(tapes)):
                    if sortedTapes[i].getAngle()-sortedTapes[j].getAngle() > 0 :
                        groups.append([sortedTapes[i], sortedTapes[j]])
                        break
            list(set(tapes))

            # Finding the middle point only if there are 2 tapes (will be updated later)
            for target in groups:
                M1 = cv2.moments(target[0].contour)
                M2 = cv2.moments(target[1].contour)
                c1x, c1y = int(M1['m10']/M1['m00']), int(M1['m01']/M1['m00'])
                c2x, c2y = int(M2['m10']/M2['m00']), int(M2['m01']/M2['m00'])
                centerX = int((c1x + c2x)/2)
                centerY = int((c1y + c2y)/2)
                area1, area2 = M1['m00'], M2['m00']
                boundedImg=cv2.circle(boundedImg, (centerX,centerY), 5, (0,255,255), thickness=-1, lineType=8, shift=0)
                boundedImg = cv2.putText(boundedImg,str(centerX)+','+str(centerY),(centerX, centerY), font, 0.5,(0,255,255),1,cv2.LINE_AA)
                boundedImg = cv2.putText(boundedImg,'Area tape 1: '+str(area1)+', Area tape 2: '+str(area2),(10, 30), font, 0.5,(255,255,255),1,cv2.LINE_AA)
                boundedImg =  cv2.rectangle(boundedImg,(target[0].getSortedVerticesX()[2][0],target[0].getSortedVerticesX()[0][1]),(target[1].getSortedVerticesY()[2][0],target[1].getSortedVerticesY()[3][1]),(0,255,0),3)

            # This draws the contour of the tape
            # shape = cv2.drawContours(shape, eyes.filter_contours_output, -1, (255,255,255), 3)
            #
            # # Draws the bounding rectangle, the reason for it to be in if statement is because the tape is not always detected
            # if len(eyes.filter_contours_output) > 0:
            #     # Creates rectangle
            #     tapeNum = 0
            #     numOftape = len(eyes.filter_contours_output)
            #     font = cv2.FONT_HERSHEY_SIMPLEX
            #     boundedImg = cv2.putText(boundedImg,'# of tapes: '+str(numOftapes),(10,12), font, 0.5,(255,255,255),1,cv2.LINE_AA)
            #     for borders in eyes.filter_contours_output:
            #         tapeNum += 1
            #         cnt = borders
            #         rect = cv2.minAreaRect(cnt)
            #         box = cv2.boxPoints(rect)
            #         box = np.int0(box)
            #         boundedImg = cv2.drawContours(boundedImg,[box],0,(0,0,255),2)
            #
            #         # Gets statistics on the rectangle
            #         M = cv2.moments(cnt)
            #
            #         # Creates the center point
            #         cx = int(M['m10']/M['m00'])
            #         cy = int(M['m01']/M['m00'])
            #         boundedImg=cv2.circle(boundedImg, (cx,cy), 5, (0,255,0), thickness=-1, lineType=8, shift=0)
            #         boundedImg = cv2.putText(boundedImg,'Tape#: '+str(tapeNum)+', Center at: '+str(cx)+','+str(cy),(box[0][0],box[0][1]), font, 0.35,(255,255,255),1,cv2.LINE_AA)
            #     # Finding the middle point only if there are 2 tapes (will be updated later)
            #     if len(eyes.filter_contours_output) == 2:
            #         M1 = cv2.moments(eyes.filter_contours_output[0])
            #         M2 = cv2.moments(eyes.filter_contours_output[1])
            #         c1x, c1y = int(M1['m10']/M1['m00']), int(M1['m01']/M1['m00'])
            #         c2x, c2y = int(M2['m10']/M2['m00']), int(M2['m01']/M2['m00'])
            #         centerX = int((c1x + c2x)/2)
            #         centerY = int((c1y + c2y)/2)
            #         area1, area2 = M1['m00'], M2['m00']
            #         boundedImg=cv2.circle(boundedImg, (centerX,centerY), 5, (0,255,255), thickness=-1, lineType=8, shift=0)
            #         boundedImg = cv2.putText(boundedImg,str(centerX)+','+str(centerY),(centerX, centerY), font, 0.5,(0,255,255),1,cv2.LINE_AA)
            #         boundedImg = cv2.putText(boundedImg,'Area tape 1: '+str(area1)+', Area tape 2: '+str(area2),(10, 30), font, 0.5,(255,255,255),1,cv2.LINE_AA)

    # multiple image to compare effect
    cv2.imshow('frame',frame)
    cv2.imshow('frame2',shape)
    cv2.imshow('frame3',boundedImg)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
