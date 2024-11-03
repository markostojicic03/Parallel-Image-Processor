import json
import os
import queue
import shutil
from datetime import datetime
from io import StringIO
from queue import Queue, Empty
from time import sleep
from xmlrpc.client import DateTime
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter
import argparse
import sys
import threading
from dataclasses import dataclass, field
import threading
import time
import random
import sys
from threading import Thread, Event
from PIL import Image as PILImage



imageRegistry = []
taskRegistry = []
condition = threading.Condition()
threadList = []
eventQueue = Queue(0)
filterProcessing = False
deleteProcessing = False
#describeProcessing = False

def grayscale(image_array):
    red_channel = image_array[..., 0]
    green_channel = image_array[..., 1]
    blue_channel = image_array[..., 2]

    # Ponderisane vrednosti za RGB komponente
    grayscale_image = (red_channel * 0.299 + green_channel * 0.587 + blue_channel * 0.114)
    return grayscale_image.astype(np.uint8)


# sigma: Vrednost standardne devijacije
def gaussian_blur(image_array, sigma=1):


    red_channel = gaussian_filter(image_array[..., 0], sigma=sigma)
    green_channel = gaussian_filter(image_array[..., 1], sigma=sigma)
    blue_channel = gaussian_filter(image_array[..., 2], sigma=sigma)

    blurred_image = np.zeros_like(image_array)
    blurred_image[..., 0] = red_channel
    blurred_image[..., 1] = green_channel
    blurred_image[..., 2] = blue_channel

    if image_array.shape[-1] == 4:
        alpha_channel = image_array[..., 3]
        blurred_image[..., 3] = alpha_channel

    blurred_image = np.clip(blurred_image, 0, 255)

    return blurred_image.astype(np.uint8)


def adjust_brightness(image_array, factor=1.0):
    mean_intensity = np.mean(image_array, axis=(0, 1), keepdims=True)  # Računanje srednje vrednosti piksela
    image_array = (image_array - mean_intensity) * factor + mean_intensity  # Skaliranje prema srednjoj vrednosti

    '''
    # Ručno implementirani clamp
    adjusted_image = np.where(image_array < 0, 0, image_array)  # Postavljanje vrednosti ispod 0 na 0
    adjusted_image = np.where(adjusted_image > 255, 255, adjusted_image)  # Postavljanje vrednosti iznad 255 na 255
    '''


    adjusted_image = np.clip(image_array, 0, 255)

    return adjusted_image.astype(np.uint8)


def load_JSON_file(json_path):
    with open(json_path) as f:
        params = json.load(f)
        print(params)
        id_param = params.get('id')
        print(f"First param: {id_param}")
        filterType_param = params.get('filterType')
        return id_param, filterType_param


@dataclass
class MyImage:
    def __init__(self,original :bool,id:int,taskId:int, deleteFlag:bool, processTime:DateTime, imageSizeBeforeProcessing:float, imageSizeAfterProcessing:float, imagePath:str):
        self.original = original
        self.id = id
        self.taskId = taskId
        self.usedTasklist = []
        self.deleteFlag = deleteFlag
        self.filterImageList = []
        self.processTime = processTime
        self.imageSizeBeforeProcessing = imageSizeBeforeProcessing
        self.imageSizeAfterProcessing = imageSizeAfterProcessing
        self.imagePath = imagePath


@dataclass
class Task:
    def __init__(self,  taskStatus: str ):
        self.imageId = None
        self.taskStatus = taskStatus



cnt_taskID = 1
cnt_imageID = 1
cnt_json = 1
def add_image():
    global cnt_imageID
    global imageRegistry
    image_path = input("Write your image path: ")

    target_dir = "../slike"
    os.makedirs(target_dir, exist_ok=True)  # Kreira folder ako ne postoji
    try:
        image_name = os.path.basename(image_path)
        target_path = os.path.join(target_dir, image_name)
        file_size = os.path.getsize(image_path) * 1.0
        shutil.copy2(image_path, target_path)
        print(f"Image moved to {target_path}")
        image = MyImage(True, cnt_imageID, None, False, datetime.now(), file_size, file_size, target_path)
        imageRegistry.append(image)
        cnt_imageID += 1
        print(image.id)
    except FileNotFoundError:
        print("Wrong image path.")
        return

def load_image(image_path):
    image = PILImage.open(image_path)
    return np.array(image)
#image_array = load_image("example.png")


def processTask():
    global cnt_taskID, cnt_imageID, cnt_json, filterProcessing,condition

    with condition:
        idImage_value, filter_type_value = load_JSON_file("../json/" + str(cnt_json) + ".json")
        newTask = Task("In processing")
        filterProcessing = True
        newTask.imageId = idImage_value
        taskRegistry.append(newTask)
        for image in imageRegistry:
            if image.id == idImage_value:
                if filter_type_value == "grayscale":
                    newImage_array = grayscale(load_image(image.imagePath))
                    newImage_arrayPil = Image.fromarray(newImage_array)
                    folderName = "../slike"
                    file_name = str(image.id) + "grayScale.jpg"
                    save_path = os.path.join(folderName, file_name)
                    newImage_arrayPil.save(save_path)
                    newImage = MyImage(False, cnt_imageID, cnt_taskID, False, datetime.now(),
                                    image.imageSizeBeforeProcessing, os.path.getsize(image.imagePath) * 1.0, save_path)
                    imageRegistry.append(newImage)
                    if(image.taskId != None):
                        newImage.usedTasklist = image.usedTasklist.copy()
                        newImage.filterImageList = image.filterImageList.copy()
                    newImage.filterImageList.append(str(image.id))
                    newImage.usedTasklist.append(str(cnt_taskID))
                    newTask.taskStatus = "Finished"
                    filterProcessing = False
                    condition.notify_all()
                    cnt_taskID += 1
                    cnt_imageID += 1
                    cnt_json += 1
                    print("Odradjen grayscale")
                    break
                elif filter_type_value == "gaussian_blur":
                    newImage_array = gaussian_blur(load_image(image.imagePath))
                    newImage_arrayPil = Image.fromarray(newImage_array)
                    folderName = "../slike"
                    file_name = str(image.id) + "gaussianBlur.jpg"
                    save_path = os.path.join(folderName, file_name)
                    newImage_arrayPil.save(save_path)
                    newImage = MyImage(False, cnt_imageID, cnt_taskID, False, datetime.now(),
                                    image.imageSizeBeforeProcessing, os.path.getsize(image.imagePath) * 1.0, save_path)
                    imageRegistry.append(newImage)
                    if (image.taskId != None):
                        newImage.usedTasklist = image.usedTasklist.copy()
                        newImage.filterImageList = image.filterImageList.copy()
                    newImage.filterImageList.append(str(image.id))
                    newImage.usedTasklist.append(str(cnt_taskID))
                    newTask.taskStatus = "Finished"
                    filterProcessing = False
                    condition.notify_all()
                    cnt_taskID += 1
                    cnt_imageID += 1
                    cnt_json += 1
                    print("Odradjen gaussianBlur")
                    break
                elif filter_type_value == "adjust_brightness":
                    newImage_array = adjust_brightness(load_image(image.imagePath), 2.0)
                    newImage_arrayPil = Image.fromarray(newImage_array)
                    folderName = "../slike"
                    file_name = str(image.id) + "adjustBrightness.jpg"
                    save_path = os.path.join(folderName, file_name)
                    newImage_arrayPil.save(save_path)
                    newImage = MyImage(False, cnt_imageID, cnt_taskID, False, datetime.now(),
                                    image.imageSizeBeforeProcessing, os.path.getsize(image.imagePath) * 1.0, save_path)
                    imageRegistry.append(newImage)
                    if (image.taskId != None):
                        newImage.usedTasklist = image.usedTasklist.copy()
                        newImage.filterImageList = image.filterImageList.copy()
                    newImage.filterImageList.append(str(image.id))
                    newImage.usedTasklist.append(str(cnt_taskID))
                    newTask.taskStatus = "Finished"
                    filterProcessing = False
                    condition.notify_all()
                    cnt_taskID += 1
                    cnt_imageID += 1
                    cnt_json += 1
                    print("Odradjen adjustBrightness")
                    break
                else:
                    continue
                break    #mozda nepotrebno
                    #fali provera ukolika slika ne postoji u registru

def list_command():
    global eventQueue, eventFlag, condition, deleteProcessing, filterProcessing
    with  condition:
        while deleteProcessing & filterProcessing:
            condition.wait()
        for image in imageRegistry:
            imageValue = "Image ID " + str(image.id) + ", image path " + str(image.imagePath)
            eventQueue.put(imageValue)

# proveriti da li je potrebno namestiti da dok se jedna slika filtrira, druga slika radi describe
def describe():
    global eventQueue, condition, filterProcessing
    with condition:
        while filterProcessing:
            condition.wait()
        for image in imageRegistry:
            imageValue = "Image ID "
            if image.original == True:
                continue
            for str in image.filterImageList:
                imageValue += str + " "
            imageValue += ", used task "
            for str in image.usedTasklist:
                imageValue += str + " "
            eventQueue.put(imageValue)

def delete():
    global imageRegistry, filterProcessing, condition,deleteProcessing
    id_image = input("Write your image id for delete: ")#pitati da li moze ovako
    with condition:
        while filterProcessing:
            condition.wait()
        deleteProcessing = True
        for image in imageRegistry:
            print("Image " + str(id_image))
            if image.id == int(id_image):
                print("Image id " + str(image.id))
                image.deleteFlag = True
                for task in taskRegistry:
                    if task.imageId == int(id_image):
                        if task.taskStatus == "In processing":
                            print("processing")
                        elif task.taskStatus == "Finished":
                            imageRegistry.remove(image)
                            file_path = image.imagePath
                            print("finished")
                            if os.path.exists(file_path):
                                print(image.imagePath)
                                os.remove(file_path)
                        else:
                            print("wait")
        deleteProcessing = False

def exit_delete():
    eventQueue.put("exit")
    for image in imageRegistry:
        file_path = image.imagePath
        print(file_path)
        os.remove(file_path)
    for threadElement in threadList:
        if threadElement != threading.current_thread(): #proveriti da li je potrebno da se stavi i exit nit u listu niti
            threadElement.join()
        else:
            print(threadElement.name)

def command_input():

    global imageRegistry, taskRegistry, threadList,eventQueue
    # dodati periodicno proveravanje
    while True:
        command = input("Write the command you want to do: ")

        if command == "add":
            threadForAddImageC = threading.Thread(target=add_image())
            threadForAddImageC.start()
            threadList.append(threadForAddImageC)
            print("Izvrsena add komanda.")
        elif command == "process":
            threadForProcessC = threading.Thread(target=processTask())
            threadForProcessC.start()
            threadList.append(threadForProcessC)
            print("Process komanda.")
        elif command == "delete":
            threadForDeleteC = threading.Thread(target=delete())
            threadForDeleteC.start()
            threadList.append(threadForDeleteC)
            print("Delete komanda")
        elif command == "list":
            threadForListC = threading.Thread(target=list_command())
            threadForListC.start()
            threadList.append(threadForListC)
        elif command == "describe":
            threadForDescribeC = threading.Thread(target=describe())
            threadForDescribeC.start()
            threadList.append(threadForDescribeC)
            print("describe")
        elif command == "exit":
            threadForExitC = threading.Thread(target=exit_delete())
            threadForExitC.start()
            threadList.append(threadForExitC)
            threadForExitC.join()
            print("Izlazak iz programa - exit")
            sys.exit()
        else:
            print("Nepoznata komanda.")
        sleep(3)
        while not eventQueue.empty():
            try:
                value = eventQueue.get(timeout=5)
                if (value == "exit"):
                    print("Izlazak iz programa - exit")
                    sys.exit()
                print(value)
            except Empty:
                pass

if __name__ == "__main__":
    threadMain = threading.Thread(target=command_input)
    threadMain.start()
    threadList.append(threadMain)
    threadMain.join()
#C:\Users\vidan_gofx79m\Desktop\slika.jpg
#C:\Users\Marko\Desktop\slika.jpg