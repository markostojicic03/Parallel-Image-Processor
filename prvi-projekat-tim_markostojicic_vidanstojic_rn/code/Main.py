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
from PIL import Image as PILImage


'''
2. napisati delat
4. napisati describe
5. pogledati da li lepo menjamo sve parametre u klasi
7. istestestirati program
8. procitati za kraj specifikaciju

   

'''


imageRegistry = []
taskRegistry = []
condition = threading.Condition()
threadList = []

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
        return params.get('MyImage', [])


#example.json
'''
{
    "id": "Ovo je prvi parametar",
    "path": /putanja
    "": "Ovo je drugi parametar",
    "third": 123
}

'''

@dataclass
class MyImage:
    def __init__(self,original :bool,id:int,taskId:int, deleteFlag:bool, processTime:DateTime, imageSizeBeforeProcessing:float, imageSizeAfterProcessing:float, imagePath:str):
        self.original = original
        self.id = id
        self.taskId = taskId
        self.usedTasklist = []
        self.deleteFlag = deleteFlag
        self.filterTypeList = []
        self.processTime = processTime
        self.imageSizeBeforeProcessing = imageSizeBeforeProcessing
        self.imageSizeAfterProcessing = imageSizeAfterProcessing
        self.imagePath = imagePath


@dataclass
class Task:
    #   PROVERITI GDE TREBA DA STAVIMO CONDITION ACQUIRE/WAIT
    def __init__(self,  taskStatus: str ):
        self.imageId = None
        self.taskStatus = taskStatus


#C:\Users\Marko\Desktop\slika.jpg
cnt_taskID = 1
cnt_imageID = 1
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

def exit():
    for thread in threadList:
        thread.join()#proveriti jos jednom da li na ovaj nacin treba da radimo
    print("Exiting program")


# Ispod je apsolutna putanja do json fajla, zameniti za relativnu
#   D:\\Marko workspace\\Fakultet\\Projekti\\pp24-25-prvi-projekat-tim_markostojcic_vidanstoijc_rn\\prvi-projekat-tim_markostojcic_vidanstoijc_rn\\json\\proba.json
def processTask():
    global cnt_imageID
    global cnt_taskID
    images_params = load_JSON_file("../json/proba.json")  # Učitava sve parametre slika iz JSON fajla.

    for img_params in images_params:  # Iterira kroz svaku sliku iz liste.
        idImage_value = img_params.get("id")
        filter_type_value = img_params.get("filterType")

        newTask = Task("In processing")
        newTask.imageId = idImage_value
        taskRegistry.append(newTask)

        for image in imageRegistry:
            if image.original == False:
                break
            if image.id == idImage_value:
                image.filterTypeList.append(filter_type_value)

                if filter_type_value == "grayscale":
                    newImage_array = grayscale(load_image(image.imagePath))
                    newImage_arrayPil = Image.fromarray(newImage_array)
                    folderName = "../slike"
                    file_name = str(image.id)+"grayScale.jpg"  # Formira ime fajla sa ID-em slike.
                    save_path = os.path.join(folderName, file_name)
                    newImage_arrayPil.save(save_path)
                    print("Odradjen grayscale")

                elif filter_type_value == "gaussian_blur":
                    newImage_array = gaussian_blur(load_image(image.imagePath))
                    newImage_arrayPil = Image.fromarray(newImage_array)
                    folderName = "../slike"
                    file_name = str(image.id)+"gaussianBlur.jpg"  # Formira ime fajla sa ID-em slike.
                    save_path = os.path.join(folderName, file_name)
                    newImage_arrayPil.save(save_path)
                    print("Odradjen gaussianBlur")

                elif filter_type_value == "adjust_brightness":
                    newImage_array = adjust_brightness(load_image(image.imagePath), 2.0)
                    newImage_arrayPil = Image.fromarray(newImage_array)
                    folderName = "../slike"
                    file_name = str(image.id)+"adjustBrightness.jpg"  # Formira ime fajla sa ID-em slike.
                    save_path = os.path.join(folderName, file_name)
                    newImage_arrayPil.save(save_path)
                    print("Odradjen adjustBrightness")

                newImage = MyImage(False, cnt_imageID, cnt_taskID, False, datetime.now(),
                                   image.imageSizeBeforeProcessing, os.path.getsize(image.imagePath) * 1.0, save_path)
                imageRegistry.append(newImage)
                cnt_taskID += 1
                cnt_imageID += 1
                newTask.taskStatus = "Finished"
                break
                #fali provera ukolika slika ne postoji u registru

def list_command():
    for image in imageRegistry:
        print("Image id " + str(image.id))
        print("Original " + str(image.original))
        print("Image task " + str(image.taskId))
        print("Image path " + image.imagePath)
    print("kraj ispisa")

def describe():
    for image in imageRegistry:
        print("Image id " + str(image.id))
def delete():
    id_image = input("Write your image id for delete: ")
    for image in imageRegistry:
        print("Image " + str(id_image))
        if image.id == int(id_image):
            print("Image id " + str(image.id))
            image.deleteFlag = True
           # if image.original == True:

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


def process_command():

    global imageRegistry, taskRegistry
    # dodati periodicno proveravanje
    while True:
        command = input("Write the command you want to do: ")

        if command == "add":
            add_image()
            print("Izvrsena add komanda.")
        elif command == "process":
            processTask()
            print("Process komanda.")
        elif command == "delete":
            delete()
            print("Delete komanda")
        elif command == "list":
            list_command()
        elif command == "describe":
            print("describe")
        elif command == "exit":
            print("Izlazak iz programa - exit")
            sys.exit()
        else:
            print("Nepoznata komanda.")

if __name__ == "__main__":
    process_command()
#C:\Users\vidan_gofx79m\Desktop\slika.jpg

