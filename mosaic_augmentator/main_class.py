from random import randint
from os.path import join, splitext
from typing import Tuple
from PIL import Image
from tqdm import tqdm
import logging
import os
import numpy as np
import time

def line_intersect(first_line: list, second_line: list) -> bool:
    """ 
    This method check intersection of two lines
        
    :param first_line - first line
    :param second_line - second line
    
    :return bool 

    """
   
    d = (second_line[3] - second_line[1]) * (first_line[2] - first_line[0]) \
         - (second_line[2] - second_line[0]) * (first_line[3] - first_line[1])
    if d:
        u_a = ((second_line[2] - second_line[0]) * (first_line[1] - second_line[1]) - \
             (second_line[3] - second_line[1]) * (first_line[0] - second_line[0])) / d
        u_b = ((first_line[2] - first_line[0]) * (first_line[1] - second_line[1]) - \
             (first_line[3] - first_line[1]) * (first_line[0] - second_line[0])) / d
    else:
        return False

    return (0 <= u_a <= 1 and 0 <= u_b <= 1)


def point_intersection(rect: list, x: int, y: int) -> bool:
    """
    This method check intersection of point and rectangle
        
    :param rect - first rectangle
    :param x - x coordinate of point
    :param y - y coordinate of point
    
    :return bool 
    """
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]
      


def rectangles_intersection(rectangle_1: list, rectangle_2: list) -> bool:
    """
    This method check intersection of two rectangles
    :param rectangle_1 - first rectangle
    :param rectangle_2 - second rectangle
    
    :return bool 
    """
    rec1_x1, rec1_y1, rec1_x2, rec1_y2 = rectangle_1
    rec2_x1, rec2_y1, rec2_x2, rec2_y2 = rectangle_2

    x_y_match = (rec1_x1 < rec2_x2 < rec1_x2 or rec1_x1 < rec2_x1 < rec2_x2) and \
        (rec2_y2 > rec1_y1 > rec2_y2 or rec1_y1 < rec2_y1 < rec1_y2)
        


    in_match = rec1_x1 < rec2_x1 and rec1_y1 < rec2_y1 and rec1_x2 > rec2_x2 and rec1_y2 > rec2_y2

    # x1, y1
    # x1, y2
    # x2, y1
    # x2, vertical_line_match

    angle_match = ((rec1_x1 < rec2_x1 < rec1_x2) and (rec1_y1 < rec2_y1 < rec1_y2)) or \
            ((rec1_x1 < rec2_x1 < rec1_x2) and (rec1_y1 < rec2_y2 < rec1_y2)) or \
            ((rec1_x1 < rec2_x2 < rec1_x2) and (rec1_y1 < rec2_y1 < rec1_y2)) or \
            ((rec1_x1 < rec2_x2 < rec1_x2) and (rec1_y1 < rec2_y2 < rec1_y2))


    out_match = (rec1_x1 < rec2_x1 and rec1_y1 > rec2_y1 and rec1_x2 > rec2_x2 and rec1_y2 < rec2_y2) or \
            (rec1_x1 > rec2_x1 and rec1_y1 < rec2_y1 and rec1_x2 > rec2_x2 and rec1_y2 > rec2_y2)

    point_match = False
    rect = [rec1_x1, rec1_y1, rec1_x2, rec1_y2]
    if point_intersection(rect, rec2_x1, rec2_y1):
        point_match = True
    if point_intersection(rect, rec2_x2, rec2_y2):
        point_match = True
    rect = [rec2_x1, rec2_y1, rec2_x2, rec2_y2]
    if point_intersection(rect, rec1_x1, rec1_y1):
        point_match = True
    if point_intersection(rect, rec1_x2, rec1_y2):
        point_match = True

    vertical_line_match = line_intersect([rec1_x1, rec1_y1, rec1_x1, rec1_y2], [rec2_x1, rec2_y1, rec2_x2, rec2_y1]) or \
            line_intersect([rec1_x1, rec1_y1, rec1_x1, rec1_y2], [rec2_x1, rec2_y2, rec2_x2, rec2_y2]) or \
            line_intersect([rec1_x2, rec1_y1, rec1_x2, rec1_y2], [rec2_x1, rec2_y1, rec2_x2, rec2_y1]) or \
            line_intersect([rec1_x2, rec1_y2, rec1_x1, rec1_y2], [rec2_x1, rec2_y2, rec2_x2, rec2_y2])

    horizontal_line_match = False
    horizontal_line_match = line_intersect([rec1_x1, rec1_y1, rec1_x2, rec1_y1], [rec2_x1, rec2_y1, rec2_x1, rec2_y2]) or \
            line_intersect([rec1_x1, rec1_y1, rec1_x2, rec1_y1], [rec2_x2, rec2_y1, rec2_x2, rec2_y2]) or \
            line_intersect([rec1_x1, rec1_y2, rec1_x2, rec1_y2], [rec2_x1, rec2_y1, rec2_x1, rec2_y2]) or \
            line_intersect([rec1_x1, rec1_y2, rec1_x2, rec1_y2], [rec2_x2, rec2_y1, rec2_x2, rec2_y2])

    return  x_y_match or in_match or angle_match or out_match or point_match or horizontal_line_match or vertical_line_match


class DataPair:
    """
    Class-container for data pairs(image-annotation), that contains all information about
    images and txt-annotations.

    """
    image_folder: str
    text_folder: str
    image_name: str
    txt_name: str
    yolo_objects_list: list
    rec_objects_list: list
    img_width: int
    img_height: int
    people_number: int
    objects_classes: list

    def __init__(self, image_folder: str, text_folder: str,
                 image_name: str, txt_name: str) -> None:
        """
        Constructor
        :param image_folder - image folder
        :param text_folder - annotation folder
        :param image_name - name of image file
        :param txt_name - annotation file folder
        """
        self.image_folder = image_folder
        self.text_folder = text_folder
        self.image_name = image_name
        self.txt_name = txt_name
        self.objects_classes = []
        self.yolo_objects_list = []
        self.rec_objects_list = []
        image = Image.open(join(self.image_folder, self.image_name))
        self.img_width, self.img_height = image.size
        self.create_obj_list()

    def create_obj_list(self) -> None:
        """
        This method reads annotation file and turns this data to list of lists of float
        """
        with open(join(self.text_folder, self.txt_name)) as f:
            lines = f.readlines()
            for line in lines:
                line1 = line.strip('\n').split(' ')
                float_line = list(np.float_(line1))
                self.objects_classes.append(int(float_line[0]))
                float_line.pop(0)
                self.yolo_objects_list.append(float_line)
            for i in range(len(self.yolo_objects_list)):
                self.rec_objects_list.append(self.from_cross_to_rec(i))
            self.people_number = len(self.rec_objects_list)

    def from_cross_to_rec(self, number: int) -> list:
        """
        This method turns annotations in YOLO format into rectangle coordinates
        """
        box_w = int(self.yolo_objects_list[number][2] * self.img_width)
        box_h = int(self.yolo_objects_list[number][3] * self.img_height)
        x_mid = int(self.yolo_objects_list[number][0] * self.img_width + 1)
        y_mid = int(self.yolo_objects_list[number][1] * self.img_height + 1)
        x_min = int(x_mid - box_w / 2) + 1
        x_max = int(x_mid + box_w / 2) - 1
        y_min = int(y_mid - box_h / 2) + 1
        y_max = int(y_mid + box_h / 2) - 1
        return [x_min, y_min, x_max, y_max]

    def get_free_space_on_image(self, width: int, height: int) -> Tuple[bool, list]:
        """
        This method returns image part without any objects and four coordinates of this piece
        
        :param width
        :param height

        :return Image - returns Image or False
        :return out_list - coordinates of image part
        """
        out_list = []
        if self.people_number == 0:
            if self.img_width == width:
                out_x1 = 0
                out_x2 = width
            elif self.img_width > width:
                out_x1 = randint(0, int(self.img_width - width))
                out_x2 = out_x1 + width
            else:
                return False, out_list
            if self.img_height == height:
                out_y1 = 0
                out_y2 = width
            elif self.img_height > height:
                out_y1 = randint(0, int(self.img_height - height))
                out_y2 = out_y1 + height
            else:
                return False, out_list
            return self.get_image().crop((out_x1, out_y1, out_x2, out_y2)), out_list
        else:
            areas = []
            x, y = 0, 0
            for n in range(15):
                stop = False
                while not stop:
                    x = randint(0, self.img_width - 1)
                    y = randint(0, self.img_height - 1)
                    stop = True
                    for line in self.rec_objects_list:
                        if point_intersection([line[0], line[1], line[2], line[3]], x, y):
                            stop = False

                out_x1 = x - randint(0, x)
                out_y1 = y - randint(0, y)
                out_x2 = randint(x, self.img_width - 1)
                out_y2 = randint(y, self.img_height - 1)

                for i in range(len(self.rec_objects_list)):
                    if rectangles_intersection([out_x1, out_y1, out_x2, out_y2], [self.rec_objects_list[i][0],
                                                                                  self.rec_objects_list[i][1],
                                                                                  self.rec_objects_list[i][2],
                                                                                  self.rec_objects_list[i][3]]):
                        if out_x1 < self.rec_objects_list[i][2]:
                            out_x1 = self.rec_objects_list[i][2]
                        elif out_x2 > self.rec_objects_list[i][0]:
                            out_x2 = self.rec_objects_list[i][0]

                        if out_y1 < self.rec_objects_list[i][3]:
                            out_y1 = self.rec_objects_list[i][3]
                        elif out_y2 > self.rec_objects_list[i][1]:
                            out_y2 = self.rec_objects_list[i][1]
                areas.append([out_x1, out_y1, out_x2, out_y2])

            max_number = 0
            max_area = (areas[0][2] - areas[0][0]) * (areas[0][3] - areas[0][1])
            for i in range(len(areas)):
                if max_area < (areas[i][2] - areas[i][0]) * (areas[i][3] - areas[i][1]):
                    max_area = (areas[i][2] - areas[i][0]) * (areas[i][3] - areas[i][1])
                    max_number = i
            out_x1 = areas[max_number][0]
            out_y1 = areas[max_number][1]
            out_x2 = areas[max_number][2]
            out_y2 = areas[max_number][3]
            out_list = [out_x1, out_y1, out_x2, out_y2]
            if out_x2 - out_x1 > 1 and out_y2 - out_y1 > 1:
                if out_x2 - out_x1 >= width and out_y2 - out_y1 >= height:
                    return self.get_image().crop((out_x1, out_y1, out_x1 + width, out_y1 + height)), out_list
                else:
                    new_width = out_x2 - out_x1
                    new_height = out_y2 - out_y1
                    multiplier_width = 1
                    multiplier_height = 1
                    if width > new_width:
                        multiplier_width = width / new_width
                    if height > new_height:
                        multiplier_height = height / new_height

                    if multiplier_width > multiplier_height:
                        img = self.get_image().crop((out_x1, out_y1, out_x2, out_y2))
                        new_image = img.resize((int(new_width * multiplier_width), int(new_height * multiplier_width)))
                    else:
                        img = self.get_image().crop((out_x1, out_y1, out_x2, out_y2))
                        new_image = img.resize(
                            (int(new_width * multiplier_height), int(new_height * multiplier_height)))
                    return new_image.crop((0, 0, width, height)), out_list
            return False, out_list

    def get_image(self) -> Image:
        """
        Returns image by path from class
        """
        return Image.open(join(self.image_folder, self.image_name))

    def get_image_piece_with_object(self, width, height, min_multiplier, max_multiplier) -> Tuple[bool, list, list, list]:
        """
        This method returns image part with one or several objects and four coordinates of this piece

        :param width
        :param height
        :param min_multiplier - min object multiplier
        :param max_multiplier - max object multiplier
        :return Image - returns Image or False
        :return out_rec_list - coordinates of image part
        :return out_pic_rect - coordinates of object
        :return classes_list - list of objects classes
        """
        out_list_1 = []
        classes_list = []
        out_rec_list = []
        out_pic_rect = []
        if self.people_number == 0 or (30 >= width > 0) or (30 >= height > 0):
            return False, out_rec_list, out_pic_rect, classes_list
        else:
            first_man_number = randint(0, len(self.rec_objects_list) - 1)
            out_x1 = self.rec_objects_list[first_man_number][0]
            out_y1 = self.rec_objects_list[first_man_number][1]
            out_x2 = self.rec_objects_list[first_man_number][2]
            out_y2 = self.rec_objects_list[first_man_number][3]
            objects_in_cropped_images = [first_man_number]
            is_stop = True
            while is_stop:
                if out_x1 - width // 2 > 0:
                    out_x1 -= randint(0, width // 2)
                else:
                    out_x1 -= randint(0, out_x1)
                if out_y1 - height // 2 > 0:
                    out_y1 -= randint(0, height // 2)
                else:
                    out_y1 -= randint(0, out_y1)

                if out_x2 + width // 2 < self.img_width:
                    out_x2 += randint(0, width // 2)
                else:
                    if self.img_width - out_x2 > 0:
                        out_x2 += randint(0, self.img_width - out_x2)

                if out_y2 + height // 2 < self.img_height:
                    out_y2 += randint(0, height // 2)
                else:
                    if self.img_height - out_y2 > 0:
                        out_y2 += randint(0, self.img_height - out_y2)
                is_stop = False
                for i in range(len(self.rec_objects_list)):
                    if rectangles_intersection([out_x1, out_y1, out_x2, out_y2], [self.rec_objects_list[i][0],
                                                                                  self.rec_objects_list[i][1],
                                                                                  self.rec_objects_list[i][2],
                                                                                  self.rec_objects_list[i][
                                                                                      3]]) and not (
                            i in objects_in_cropped_images):
                        is_stop = True
                        if out_x1 > self.rec_objects_list[i][0]:
                            out_x1 = self.rec_objects_list[i][0]
                        if out_y1 > self.rec_objects_list[i][1]:
                            out_y1 = self.rec_objects_list[i][1]
                        if out_x2 < self.rec_objects_list[i][2]:
                            out_x2 = self.rec_objects_list[i][2]
                        if out_y2 < self.rec_objects_list[i][3]:
                            out_y2 = self.rec_objects_list[i][3]
                        objects_in_cropped_images.append(i)

            out_rec_list = []
            for number in objects_in_cropped_images:
                out_rec_list.append([self.rec_objects_list[number][0] - out_x1,
                                     self.rec_objects_list[number][1] - out_y1,
                                     self.rec_objects_list[number][2] - out_x1,
                                     self.rec_objects_list[number][3] - out_y1])
                classes_list.append(self.objects_classes[number])
            out_pic_rect = [out_x1, out_y1, out_x2, out_y2]
            if not (width == 0 or height == 0):
                new_width = out_x2 - out_x1
                new_height = out_y2 - out_y1
                multiplier_width = width / new_width
                multiplier_height = height / new_height
                img = self.get_image().crop((out_x1, out_y1, out_x2, out_y2))
                if multiplier_width < multiplier_height:
                    if not min_multiplier < multiplier_width < max_multiplier:
                        return False, out_rec_list, out_pic_rect, classes_list
                    else:
                        for line in out_rec_list:
                            x1 = line[0] * multiplier_width
                            y1 = line[1] * multiplier_width
                            x2 = line[2] * multiplier_width
                            y2 = line[3] * multiplier_width
                            new_line = [int(x1), int(y1), int(x2), int(y2)]
                            out_list_1.append(new_line)
                        new_image = img.resize((int(new_width * multiplier_width), int(new_height * multiplier_width)))
                else:
                    if not min_multiplier < multiplier_height < max_multiplier:
                        return False, out_rec_list, out_pic_rect, classes_list
                    else:
                        for line in out_rec_list:
                            x1 = line[0] * multiplier_height
                            y1 = line[1] * multiplier_height
                            x2 = line[2] * multiplier_height
                            y2 = line[3] * multiplier_height
                            new_line = [int(x1), int(y1), int(x2), int(y2)]
                            out_list_1.append(new_line)
                        new_image = img.resize(
                            (int(new_width * multiplier_height), int(new_height * multiplier_height)))
                return new_image, out_list_1, out_pic_rect, classes_list
            else:
                return self.get_image().crop((out_x1, out_y1, out_x2, out_y2)), out_rec_list, out_pic_rect, classes_list


class MosaicImage:
    """
    Class-container for mosaic pair(image-annotation), that contains all information about
    image and txt-annotation of mosaic.
    """
    people_number: int
    pieces_number: int
    img_width: int
    img_height: int
    yolo_objects_list: list
    rec_objects_list: list
    rec_rec_list: list
    main_image: Image
    pair_list: list
    image_folder: str
    txt_folder: str
    filename: str
    pair_classes: list
    mosaic_classes: list

    min_human_multiplier: int
    max_human_multiplier: int

    img_ext = ".jpg"
    txt_ext = ".txt"

    def __init__(self, pairs: list, arg_img_folder: str, arg_txt_folder: str, filename: str):
        """
        Constructor - takes in Data_pair type objects list 
        First object contain 1 or 0 people

        :param pairs - list of pairs
        :param arg_img_folder - save folder for image
        :param arg_txt_folder - save folder for annotation
        :param filename - name of image and annotation file

        """
        self.min_human_multiplier = 1
        self.max_human_multiplier = 2
        self.pair_classes = []
        self.mosaic_classes = []
        self.pieces_number = 0
        self.pair_list = pairs.copy()
        self.yolo_objects_list = []
        self.rec_objects_list = pairs[0].rec_objects_list.copy()
        self.rec_rec_list = []
        self.img_width = pairs[0].img_width
        self.img_height = pairs[0].img_height
        self.main_image = pairs[0].get_image()
        self.image_folder = arg_img_folder
        self.txt_folder = arg_txt_folder
        self.people_number = pairs[0].people_number
        self.filename = filename
        for i in range(0, len(self.pair_list) - 1):
            if self.pair_list[i].people_number != len(self.pair_list[i].rec_objects_list):
                self.pair_list[i].people_number = len(self.pair_list[i].rec_objects_list)

        if self.people_number == 1:
            self.mosaic_classes.append(pairs[0].objects_classes[0])
            self.yolo_objects_list.append(self.from_rec_to_cross(self.rec_objects_list[0]))
            self.get_small_area(self.rec_objects_list[0], 7, 7)
        else:
            self.people_number = 0
            self.pieces_number = 0
        logging.info('Mosaic main image is ready')

    def make_mosaic(self) -> bool:
        """
        Creating mosaic from data inside the class

        :return bool
        """
        for i in range(0, len(self.pair_list) - 1):
            self.get_part_main_image()
        logging.info(f"Pieces in mosaic number: {self.pieces_number}")
        logging.info(f"Pieces in mosaic: {self.rec_rec_list}")
        self.insert_pics()
        if self.write_in_files():
            logging.info(f"Mosaic pair number {self.filename} was wrote successful!")
            return True
        else:
            logging.info(f"On mosaic pair number {self.filename} no people found!")
        return False
       

    def get_small_area(self, obj_coordinates, delta_w: int, delta_h: int) -> None:
        """
        Create random area around one single object on image

        :param obj_coordinates - object coordinates
        :param delta_w - width of area
        :param delta_h - height of area
        """
        if obj_coordinates[0] - delta_w >= 0:
            out_x1 = obj_coordinates[0] - randint(0, delta_w)
        else:
            out_x1 = obj_coordinates[0] - randint(0, obj_coordinates[0])

        if obj_coordinates[2] + delta_w <= self.img_width - 1:
            out_x2 = obj_coordinates[2] + randint(0, delta_w)
        else:
            if self.img_width - obj_coordinates[2] <= 0:
                out_x2 = obj_coordinates[2]
            else:
                out_x2 = obj_coordinates[2] + randint(0, self.img_width - obj_coordinates[2])

        if obj_coordinates[1] - delta_h >= 0:
            out_y1 = obj_coordinates[1] - randint(0, delta_h)
        else:
            out_y1 = obj_coordinates[1] - randint(0, obj_coordinates[1])

        if obj_coordinates[3] + delta_h <= self.img_height - 1:
            out_y2 = obj_coordinates[3] + randint(0, delta_h)
        else:
            if self.img_height - obj_coordinates[3] <= 0:
                out_y2 = obj_coordinates[3]
            else:
                out_y2 = obj_coordinates[3] + randint(0, self.img_height - obj_coordinates[3])
        self.rec_rec_list.append([out_x1, out_y1, out_x2, out_y2])
        self.pieces_number += 1

    def write_in_files(self) -> bool:
        """
        Write mosaic pair in files

        """
        if self.people_number != 0:
            self.main_image.save(join(self.image_folder, self.filename + ".jpg"))
            class_number = 0
            with open(join(self.txt_folder, self.filename + ".txt"), 'w') as f:
                for item in self.yolo_objects_list:
                    f.write(f"{self.mosaic_classes[class_number]} ")
                    class_number += 1
                    for numb in item:
                        f.write(f"{numb} ")
                    f.write("\n")
            return True
        return False

    def from_rec_to_cross(self, box) -> list:
        """
        Turn rectangular coordinates in YOLO format

        :return list - YOLO coordinates
        """
        dw = 1. / self.img_width
        dh = 1. / self.img_height
        x = (box[0] + box[2]) / 2.0
        y = (box[1] + box[3]) / 2.0
        w = box[2] - box[0]
        h = box[3] - box[1]
        x = x * dw
        w = w * dw
        y = y * dh
        h = h * dh
        return [x, y, w, h]

    def get_part_main_image(self) -> None:
        """
        Get random empty part of image

        """
        areas = []
        if self.pieces_number == 0:
            for n in range(15):
                out_x1 = randint(0, self.img_width - 1)
                out_y1 = randint(0, self.img_height - 1)
                if out_x1 == self.img_width - 1:
                    out_x2 = out_x1
                else:
                    out_x2 = randint(out_x1, self.img_width - 1)
                if out_y1 == self.img_height - 1:
                    out_y2 = out_y1
                else:
                    out_y2 = randint(out_y1, self.img_height - 1)
                areas.append([out_x1, out_y1, out_x2, out_y2])
            max_number = 0
            max_area = (areas[0][2] - areas[0][0]) * (areas[0][3] - areas[0][1])
            for i in range(len(areas)):
                if max_area < (areas[i][2] - areas[i][0]) * (areas[i][3] - areas[i][1]):
                    max_area = (areas[i][2] - areas[i][0]) * (areas[i][3] - areas[i][1])
                    max_number = i
            out_x1 = areas[max_number][0]
            out_y1 = areas[max_number][1]
            out_x2 = areas[max_number][2]
            out_y2 = areas[max_number][3]
            self.rec_rec_list.append([out_x1, out_y1, out_x2, out_y2])
            self.pieces_number += 1
        else:
            for n in range(15):
                x, y = 0, 0
                stop = False
                while not stop:
                    x = randint(1, self.img_width - 1)
                    y = randint(1, self.img_height - 1)
                    stop = True
                    for line in self.rec_rec_list:
                        if point_intersection([line[0], line[1], line[2], line[3]], x, y):
                            stop = False

                out_x1 = x - randint(0, x)
                out_y1 = y - randint(0, y)
                out_x2 = randint(x, self.img_width - 1)
                out_y2 = randint(y, self.img_height - 1)
                is_good_area = False

                for i in range(len(self.rec_rec_list)):
                    for line in self.rec_rec_list:
                        if rectangles_intersection([out_x1, out_y1, out_x2, out_y2],
                                                   [line[0], line[1], line[2], line[3]]):
                            if out_x1 < line[0] and out_y1 > line[1]:
                                if line[0] - 1 >= 0:
                                    out_x2 = line[0] - 1
                                else:
                                    out_x2 = line[0]
                            if out_x1 > line[0] and out_y1 < line[1]:
                                if line[1] - 1 >= 0:
                                    out_y2 = line[1] - 1
                                else:
                                    out_y2 = line[1]
                            if out_x2 > line[2] and out_y2 < line[3]:
                                if line[2] + 1 <= self.img_width:
                                    out_x1 = line[2] + 1
                                else:
                                    out_x1 = line[2]

                            if out_x2 < line[2] and out_y2 > line[3]:
                                if line[3] + 1 <= self.img_height:
                                    out_y1 = line[3] + 1
                                else:
                                    out_y1 = line[3]
                            # if up point is higher 
                            if out_x1 < line[0]:
                                if line[0] - 1 >= 0:
                                    out_x2 = line[0] - 1
                                else:
                                    out_x2 = line[0]
                            # if up point is left
                            if out_y1 < line[1]:
                                if line[1] - 1 >= 0:
                                    out_y2 = line[1] - 1
                                else:
                                    out_y2 = line[1]
                            # if lower point is lower    
                            if out_x2 > line[2]:
                                if line[2] + 1 <= self.img_width:
                                    out_x1 = line[2] + 1
                                else:
                                    out_x1 = line[2]
                            # if lower point is right  
                            if out_y2 > line[3]:
                                if line[3] + 1 <= self.img_height:
                                    out_y1 = line[3] + 1
                                else:
                                    out_y1 = line[3]

                            if rectangles_intersection([out_x1, out_y1, out_x2, out_y2],
                                                       [line[0], line[1], line[2], line[3]]):
                                is_good_area = False
                                break
                            else:
                                is_good_area = True
                if is_good_area:
                    areas.append([out_x1, out_y1, out_x2, out_y2])
            if not len(areas) == 0:
                max_number = 0
                max_area = (areas[0][2] - areas[0][0]) * (areas[0][3] - areas[0][1])
                for i in range(len(areas)):
                    if max_area < (areas[i][2] - areas[i][0]) * (areas[i][3] - areas[i][1]):
                        max_area = (areas[i][2] - areas[i][0]) * (areas[i][3] - areas[i][1])
                        max_number = i
                out_x1 = areas[max_number][0]
                out_y1 = areas[max_number][1]
                out_x2 = areas[max_number][2]
                out_y2 = areas[max_number][3]
                if out_x2 - out_x1 > 1 and out_y2 - out_y1 > 1:
                    self.rec_rec_list.append([out_x1, out_y1, out_x2, out_y2])
                    self.pieces_number += 1

    def insert_pics(self) -> None:
        """
        Insert random parts with objects from pair images into empty parts of Main Image

        """
        for i in range(0, len(self.rec_rec_list)):
            width = self.rec_rec_list[i][2] - self.rec_rec_list[i][0]
            height = self.rec_rec_list[i][3] - self.rec_rec_list[i][1]
            for n in range(20):
                img, piece_of_objects_list, _, classes = self.pair_list[i].get_image_piece_with_object(width, height,
                                                                                                       self.min_human_multiplier,
                                                                                                       self.max_human_multiplier)
                if img:    
                    break
            if img:
                logging.info(f"Image in piece number {i} contains following objects: {piece_of_objects_list}")
                class_numb = 0
                for line in piece_of_objects_list:
                    self.mosaic_classes.append(classes[class_numb])
                    class_numb += 1
                    new_line = [line[0] + self.rec_rec_list[i][0], line[1] + self.rec_rec_list[i][1],
                                line[2] + self.rec_rec_list[i][0], line[3] + self.rec_rec_list[i][1]]
                    self.rec_objects_list.append(new_line)
                    self.yolo_objects_list.append(self.from_rec_to_cross(new_line))
                self.main_image.paste(img, (self.rec_rec_list[i][0], self.rec_rec_list[i][1]))


class ImageMosaic:
    """
    Class-controller. Read images and annotations files into DataPair classes

    """
    pair_count: int
    input_image_folder: str
    input_text_folder: str
    output_image_folder: str
    output_txt_folder: str
    image_list: list
    txt_list: list

    pair_list = []

    min_object_multiplier: int
    max_object_multiplier: int

    img_ext = ".jpg"
    txt_ext = ".txt"

    start_number: int
    end_number: int
    max_images_in_mosaic = 5

    def __init__(self, input_img_folder: str, input_txt_folder: str,
                 output_img_folder: str, output_txt_folder: str) -> None:
        """
        Constructor

        :param input_img_folder - folder to reading images
        :param input_txt_folder - folder to reading annotations
        :param output_img_folder - folder to writing images
        :param output_txt_folder - folder to writing annotations
        """
        logging.basicConfig(filename="mosaic_augment.log", level=logging.INFO)
        self.input_image_folder = input_img_folder
        self.min_object_multiplier = 1
        self.max_object_multiplier = 2
        self.start_number = 0
        self.end_number = 1
        self.input_text_folder = input_txt_folder
        self.output_image_folder = output_img_folder
        self.output_txt_folder = output_txt_folder
        self.image_list = next(os.walk(self.input_image_folder))[2]
        self.image_list.sort()
        self.txt_list = next(os.walk(self.input_text_folder))[2]
        self.txt_list.sort()
        if len(self.image_list) == len(self.txt_list):
            self.pair_count = len(self.txt_list)
            is_all_files_paired = True
            for i in tqdm(range(self.pair_count), colour="red"):
                img_pathname, img_extension = splitext(self.image_list[i])
                txt_pathname, txt_extension = splitext(self.txt_list[i])
                if not (img_pathname == txt_pathname and img_extension == self.img_ext and txt_extension == self.txt_ext):
                    print(f"ERROR! Pair {i}: img {self.image_list[i]} - txt {self.txt_list[i]}")
                    is_all_files_paired = False
            if is_all_files_paired:
                print(f"All images have a respective pair of text files!")
                print(f"Pair count is {self.pair_count}")
                for i in tqdm(range(self.pair_count), colour="blue"):
                    self.pair_list.append(DataPair(self.input_image_folder, self.input_text_folder, self.image_list[i],
                                                   self.txt_list[i]))
            else:
                print(f"ERROR! Not all images have a respective pair of text files!")
        elif len(self.image_list) > len(self.txt_list):
            print(f"ERROR! Not all images have a respective pair of text files!")
            print(f"There is {len(self.image_list) - len(self.txt_list)} images without pairs")
        else:
            print(f"ERROR! Not all images have a respective pair of text files!")
            print(f"There is {len(self.txt_list) - len(self.image_list)} txt files without pairs")

    def get_several_rand_pairs(self) -> list:
        """
        Create list of several random pairs

        :return list - pairs list
        
        """
        pic_number = randint(2, self.max_images_in_mosaic)
        rand_pairs_list = []
        for i in range(pic_number):
            if i == 0:
                stop = False
                while not stop:
                    pair = randint(0, self.pair_count - 1)
                    if self.pair_list[pair].people_number == 0 or self.pair_list[pair].people_number == 1:
                        rand_pairs_list.append(pair)
                        stop = True
            elif i == 1:
                stop = False
                while not stop:
                    pair = randint(0, self.pair_count - 1)
                    if self.pair_list[pair].people_number >= 1:
                        rand_pairs_list.append(pair)
                        stop = True
            else:
                pair = randint(0, self.pair_count - 1)
                rand_pairs_list.append(pair)
        logging.info(f"Chased {pic_number} images for mosaic. Images: {rand_pairs_list}")
        for i in range(pic_number):
            logging.info(f"People count on image number {i} - {rand_pairs_list[i]} = {self.pair_list[pair].people_number}")
        return rand_pairs_list

    def set_min_object_multiplier(self, new_multiplier) -> None:
        """
        Set min object multiplier
        """
        self.min_object_multiplier = new_multiplier

    def set_max_object_multiplier(self, new_multiplier) -> None:
        """
        Set max object multiplier
        """
        self.max_object_multiplier = new_multiplier

    def set_max_images_in_mosaic(self, new_max) -> None:
        """
        Set max images in mosaic
        """
        self.max_images_in_mosaic = new_max

    def set_start_count(self, count) -> None:
        """
        Set start count
        """
        self.start_number = count

    def set_end_count(self, count) -> None:
        """
        Set end count
        """
        self.end_number = count

    def print_params(self) -> None:
        """
        Print parameters of class
        """
        print(f"--------------------------------------------------")
        print("Parameters of class:")
        print(f"Minimum object multiplier = {self.min_object_multiplier}")
        print(f"Maximum object multiplier = {self.max_object_multiplier}")
        print(f"Open images folder: {self.input_image_folder}")
        print(f"Open annotations folder: {self.input_text_folder}")
        print(f"Save images folder: {self.output_image_folder}")
        print(f"Save annotations folder: {self.output_txt_folder}")
        print(f"Loaded pairs count: {len(self.txt_list)}")
        print(f"Image format to save {self.img_ext}")
        print(f"Annotation format to save {self.txt_ext}")
        print(f"Maximum images in mosaic {self.max_images_in_mosaic}")
        print(f"Start number {self.start_number}")
        print(f"End number {self.end_number}")
        print(f"--------------------------------------------------")
        logging.info(f"--------------------------------------------------")
        logging.info("Parameters of class:")
        logging.info(f"Minimum object multiplier = {self.min_object_multiplier}")
        logging.info(f"Maximum object multiplier = {self.max_object_multiplier}")
        logging.info(f"Open images folder: {self.input_image_folder}")
        logging.info(f"Open annotations folder: {self.input_text_folder}")
        logging.info(f"Save images folder: {self.output_image_folder}")
        logging.info(f"Save annotations folder: {self.output_txt_folder}")
        logging.info(f"Loaded pairs count: {len(self.txt_list)}")
        logging.info(f"Image format to save {self.img_ext}")
        logging.info(f"Annotation format to save {self.txt_ext}")
        logging.info(f"Maximum images in mosaic {self.max_images_in_mosaic}")
        logging.info(f"Start number {self.start_number}")
        logging.info(f"End number {self.end_number}")
        logging.info(f"--------------------------------------------------")

    def make_mosaic(self, ):
        """
        Make several mosaics from class data 
        """
        self.print_params()
        if self.end_number > self.start_number:
            if self.min_object_multiplier < self.max_object_multiplier:
                logging.info(f"Will be creating {self.end_number-self.start_number} mosaics")
                logging.info(f"From start number {self.start_number} to end number {self.end_number}")
                logging.info("Mosaic creation started...")
                print(f"Will be creating {self.end_number-self.start_number} mosaics")
                print(f"From start number {self.start_number} to end number {self.end_number}")
                print("Mosaic creation started...")
                for counter in tqdm(range(self.start_number, self.end_number), colour="green"):
                    rand_pair_numbers = self.get_several_rand_pairs()
                    rand_pair_list = []
                    for i in range(len(rand_pair_numbers)):
                        rand_pair_list.append(self.pair_list[rand_pair_numbers[i]])
                    mosaic = MosaicImage(rand_pair_list, self.output_image_folder, self.output_txt_folder, str(counter))
                    mosaic.min_human_multiplier = self.min_object_multiplier
                    mosaic.max_human_multiplier = self.max_object_multiplier
                    mosaic.img_ext = self.img_ext
                    mosaic.txt_ext = self.txt_ext
                    if not mosaic.make_mosaic():
                        i -= 1

                    logging.info(f"--------------------------------------------------")
            else:
                print("ERROR! Wrong multipliers!")
        else:
            print("ERROR! end < start")


start = time.time()
img_folder = "/media/nikita/Новый том/test_data/df_to_mosaic"
txt_folder = "/media/nikita/Новый том/test_data/txt_to_mosaic"
out_img_folder = "/media/nikita/Новый том/test_data/mosaic_images"
out_txt_folder = "/media/nikita/Новый том/test_data/mosaic_txt"
Img_mosaic = ImageMosaic(img_folder, txt_folder, out_img_folder, out_txt_folder)
Img_mosaic.set_start_count(0)
Img_mosaic.set_end_count(560000)
Img_mosaic.make_mosaic()
end = time.time()
print(end - start)
