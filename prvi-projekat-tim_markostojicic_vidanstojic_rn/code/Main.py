import json
import os
import shutil
from datetime import datetime
from queue import Queue, Empty
from time import sleep
from xmlrpc.client import DateTime
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter
from dataclasses import dataclass, field
import threading
import sys
from PIL import Image as PILImage
import multiprocessing as mp



imageRegistry = []
taskRegistry = []
condition = threading.Condition()
threadList = []
eventQueue = Queue(0)
completedTasksQueue = Queue(0)
filterProcessing = False
deleteProcessing = False
jsonFiles = ["../json/1.json", "../json/2.json", "../json/3.json"]

def grayscale(image_array):
    red_channel = image_array[..., 0]
    green_channel = image_array[..., 1]
    blue_channel = image_array[..., 2]

    grayscale_image = (red_channel * 0.299 + green_channel * 0.587 + blue_channel * 0.114)
    return grayscale_image.astype(np.uint8)


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
    mean_intensity = np.mean(image_array, axis=(0, 1), keepdims=True)
    image_array = (image_array - mean_intensity) * factor + mean_intensity

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
        self.filterType = None


@dataclass
class Task:
    def __init__(self, taskId:int,taskStatus: str, taskName : str, imagePath: str, filterType: str, image = None  ):
        self.taskId = taskId
        self.taskStatus = taskStatus
        self.filterType = filterType
        self.taskName = taskName
        self.pathForImage = None
        self.imageId = None
        self.imagePath = imagePath
        self.image = image


cnt_taskID = 1
cnt_imageID = 1
cnt_json = 1
def add_image():
    global cnt_imageID
    global imageRegistry
    image_path = input("Write your image path(for example  ../imageResources/slika1.jpg): ")

    target_dir = "../slike"
    os.makedirs(target_dir, exist_ok=True)
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

def multiProcessTask(task_id, image_id, newImage_path, filter_type_value, imagePath):


    if filter_type_value == "grayscale":
        newImage_array = grayscale(load_image(imagePath))
        newImage_arrayPil = Image.fromarray(newImage_array)
        newImage_arrayPil.save(newImage_path)
        newImage = MyImage(False, image_id, task_id, False, datetime.now(), os.path.getsize(imagePath),
                           os.path.getsize(imagePath) * 1.0, newImage_path)
        print("Odradjen grayscale")
        return newImage
    elif filter_type_value == "gaussian_blur":
        newImage_array = gaussian_blur(load_image(imagePath))
        newImage_arrayPil = Image.fromarray(newImage_array)
        newImage_arrayPil.save(newImage_path)
        newImage = MyImage(False, image_id, task_id, False, datetime.now(), os.path.getsize(imagePath),
                           os.path.getsize(imagePath) * 1.0, newImage_path)
        print("Odradjen gaussianBlur")
        return newImage
    elif filter_type_value == "adjust_brightness":
        newImage_array = adjust_brightness(load_image(imagePath), 2.0)
        newImage_arrayPil = Image.fromarray(newImage_array)
        newImage_arrayPil.save(newImage_path)
        newImage = MyImage(False, image_id, task_id, False, datetime.now(), os.path.getsize(imagePath),
                           os.path.getsize(imagePath) * 1.0, newImage_path)
        print("Odradjen adjustBrightness")
        return newImage
def processTask():
    global imageRegistry, taskRegistry, cnt_taskID, cnt_imageID, cnt_json, filterProcessing,condition, save_path
    removeList = []
    with condition:

        save_path = None

        for jsonFile in jsonFiles:
            idImage_value, filter_type_value = load_JSON_file(jsonFile)
            for imageElement in imageRegistry:
                if imageElement.id == idImage_value:
                    file = jsonFile
                    image = imageElement
                    image.filterType = filter_type_value
                    newTask = Task(cnt_taskID,"Waiting","", image.imagePath, str(filter_type_value))
                    filterProcessing = True
                    newTask.imageId = idImage_value
                    taskRegistry.append(newTask)
                    folderName = "../slike"
                    file_name = str(image.id) + filter_type_value + ".jpg"
                    save_path = os.path.join(folderName, file_name)
                    newTask.taskName = save_path
                    newTask.image = image
                    cnt_taskID += 1
                    removeList.append(file)
        for file in removeList:
            jsonFiles.remove(file)
        with mp.Pool(processes=2) as pool:
            for task in taskRegistry:
                if(task.taskStatus != "Finished"):
                    newImage = pool.apply(multiProcessTask, args=(task.taskId, cnt_imageID, task.taskName,task.filterType, task.imagePath))
                    newImage.imageSizeBeforeProcessing = task.image.imageSizeBeforeProcessing
                    if (task.image.taskId != None):
                        newImage.usedTasklist = task.image.usedTasklist.copy()
                        newImage.filterImageList = task.image.filterImageList.copy()
                    newImage.filterImageList.append(str(task.image.id))
                    newImage.usedTasklist.append(str(task.taskId))
                    newImage.id = cnt_imageID
                    condition.notify_all()
                    cnt_imageID += 1
                    print("new image " + str(newImage.id))
                    imageRegistry.append(newImage)
                    callbackFunction(task.taskId)
                    task.taskStatus = "Finished"
        completedTasksQueue.put(None)
        filterProcessing = False


def list_command():
    global eventQueue, eventFlag, condition, deleteProcessing, filterProcessing, imageRegistry
    with  condition:
        while deleteProcessing & filterProcessing:
            condition.wait()
        for image in imageRegistry:
            imageValue = "Image ID " + str(image.id) + ", image path " + str(image.imagePath)
            eventQueue.put(imageValue)

def describe():
    global eventQueue, condition, filterProcessing, imageRegistry
    with condition:
        while filterProcessing:
            condition.wait()
        for image in imageRegistry:
            imageValue = "Image ID " + str(image.id) + " made of images "
            if image.original == True:
                continue
            for str1 in image.filterImageList:
                imageValue += str1 + " "
            imageValue += ", used task "
            for str1 in image.usedTasklist:
                imageValue += str1 + " "
            eventQueue.put(imageValue)

def delete():
    global imageRegistry, filterProcessing, condition, deleteProcessing
    id_image = input("Write your image id for delete: ")  # pitati da li moze ovako
    with condition:
        while filterProcessing:
            print("Waiting filter")
            condition.wait()
        deleteProcessing = True
        toDelete = None
        indexForDelete = -1
        i = -1
        for image in imageRegistry:
            i += 1
            if image.id == int(id_image):

                image.deleteFlag = True
                toDelete = image
                file_path = image.imagePath
                indexForDelete = i
                print("Deleted.")
                if os.path.exists(file_path):
                    print(image.imagePath)
                    os.remove(file_path)

        print("Brisem sliku sa id-ijem:" + str(toDelete.id))
        del imageRegistry[indexForDelete]
        deleteProcessing = False

def exit_delete():
    global imageRegistry
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

def callbackFunction(taskId):
    completedTasksQueue.put(taskId)
    print(f"Task {taskId} is finished!")

def taskCompleted():
    while True:
        taskId = completedTasksQueue.get()
        if(taskId == None):
            break
    with condition:
        condition.notify_all()
    print("Red za zavrsene taskove je prazan.")

def command_input():

    global imageRegistry, taskRegistry, threadList,eventQueue

    taskCompletedThread = threading.Thread(target=taskCompleted)  # PROVERITI DA LI JE OVDE POTREBNO KREIRATI OVU NIT
    taskCompletedThread.start()
    threadList.append(taskCompletedThread)

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
        sleep(1)#vratiti na 3 sekunde
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