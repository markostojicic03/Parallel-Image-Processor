import json
import os
import shutil
from datetime import datetime
from io import StringIO
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
from threading import Thread

imageRegistry = []
taskRegistry = []
condition = threading.Condition()

def grayscale(image_array):
    red_channel = image_array[..., 0]
    green_channel = image_array[..., 1]
    blue_channel = image_array[..., 2]

    # Ponderisane vrednosti za RGB komponente
    grayscale_image = (red_channel * 0.299 + green_channel * 0.587 + blue_channel * 0.114)
    return grayscale_image.astype(np.uint8)


# sigma: Vrednost standardne devijacije
def gaussian_blur(image_array, sigma=1):

    # Primena Gaussian blur na R, G, B kanale
    red_channel = gaussian_filter(image_array[..., 0], sigma=sigma)
    green_channel = gaussian_filter(image_array[..., 1], sigma=sigma)
    blue_channel = gaussian_filter(image_array[..., 2], sigma=sigma)

    # Kombinovanje kanala nazad u jednu sliku
    blurred_image = np.zeros_like(image_array)
    blurred_image[..., 0] = red_channel
    blurred_image[..., 1] = green_channel
    blurred_image[..., 2] = blue_channel

    # Ukoliko nam postoji i alfa kanal,
    # potrebno je da i njega iskombinujemo kako bismo dobili RGBA kao što je bilo u originalnoj slici
    if image_array.shape[-1] == 4:
        alpha_channel = image_array[..., 3]
        blurred_image[..., 3] = alpha_channel

    blurred_image = np.clip(blurred_image, 0, 255)

    # Osigurajte da su vrednosti u validnom opsegu
    return blurred_image.astype(np.uint8)


def adjust_brightness(image_array, factor=1.0):
    mean_intensity = np.mean(image_array, axis=(0, 1), keepdims=True)  # Računanje srednje vrednosti piksela
    image_array = (image_array - mean_intensity) * factor + mean_intensity  # Skaliranje prema srednjoj vrednosti

    '''
    # Ručno implementirani clamp
    adjusted_image = np.where(image_array < 0, 0, image_array)  # Postavljanje vrednosti ispod 0 na 0
    adjusted_image = np.where(adjusted_image > 255, 255, adjusted_image)  # Postavljanje vrednosti iznad 255 na 255
    '''

    # Osiguravamo da vrednosti ostanu između 0 i 255
    adjusted_image = np.clip(image_array, 0, 255)

    return adjusted_image.astype(np.uint8)


def load_JSON_file(json_path):
    with open(json_path) as f:
        params = json.load(f)
        print(params)
        first_param = params.get('first')
        print(f"First param: {first_param}")


#example.json
'''
{
    "first": "Ovo je prvi parametar",
    "second": "Ovo je drugi parametar",
    "third": 123
}

'''
@dataclass
class Image:
    def __init__(self,original :bool,id:int,taskId:int, deleteFlag:bool, processTime:DateTime, imageSizeBeforeProcessing:float, imageSizeAfterProcessing:float):
        self.original = original
        self.id = id
        self.taskId = taskId
        self.usedTasklist = []
        self.deleteFlag = deleteFlag
        self.filterTypeList = []
        self.processTime = processTime
        self.imageSizeBeforeProcessing = imageSizeBeforeProcessing
        self.imageSizeAfterProcessing = imageSizeAfterProcessing

@dataclass
class Task:
    #   PROVERITI GDE TREBA DA STAVIMO CONDITION ACQUIRE/WAIT
    def __init__(self,  taskStatus: str ):
        self.imageIdList = []
        self.filterTypeList = []
        self.taskStatus = taskStatus
    def taskFinished(self):
        self.taskStatus = "Finished"
        condition.notify_all()

#C:\Users\Marko\Desktop\proba.jpg
cnt_imageID = 1
def add_image():
    global cnt_imageID
    global imageRegistry
    image_path = input("Write your image path: ")
    image_array = load_image(image_path)

    target_dir = "./slike"
    os.makedirs(target_dir, exist_ok=True)  # Kreira folder ako ne postoji

    # Ime slike sa putanje
    image_name = os.path.basename(image_path)
    target_path = os.path.join(target_dir, image_name)
    file_size = os.path.getsize(image_path) * 1.0

    # Premesti sliku na ciljnu putanju
    shutil.copy2(image_path, target_path)
    print(f"Image moved to {target_path}")
    image = Image(True, cnt_imageID, None, False, datetime.now(), file_size, file_size)
    imageRegistry.append(image)
    cnt_imageID += 1

def load_image(image_path):
    image = Image.open(image_path)
    return np.array(image)
#image_array = load_image("example.png")

def exit():
    print("Exiting program")


def process_command():

    global imageRegistry, taskRegistry
    # dodati periodicno proveravanje
    while True:
        command = input("Write the command you want to do: ")

        if command == "add":
            addCommandThread = threading.Thread(target=add_image)
            addCommandThread.start()
            addCommandThread.join()

            print("Ovo je prva komanda.")
        elif command == "process":
            print("Ovo je druga komanda.")
        elif command == "delete":
            print("Izlazim iz programa.")
            exit(0)
        elif command == "list":
            print("list")
        elif command == "describe":
            print("describe")
        elif command == "exit":
            
            exit(0)
        else:
            print("Nepoznata komanda.")

if __name__ == "__main__":
    mainThread = threading.Thread(target=process_command)
    mainThread.start()
    mainThread.join()




