import json
from io import StringIO
from xmlrpc.client import DateTime
from PIL import Image
import numpy as np
from scipy.ndimage import gaussian_filter
import argparse
import sys
import threading
from dataclasses import dataclass, field


condition = threading.Condition()

@dataclass
class RegisterImage:
    def __init__(self,original :int,id:int,taskId:int, deleteFlag:int, processTime:DateTime, imageSizeBeforeProcessing:float, imageSizeAfterProcessing:float):
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
class RegisterTask:
    #   PROVERITI GDE TREBA DA STAVIMO CONDITION ACQUIRE/WAIT
    def __init__(self,  taskStatus: str ):
        self.imageIdList = []
        self.filterTypeList = []
        self.taskStatus = taskStatus
    def taskFinished(self):
        self.taskStatus = "Finished"
        condition.notify_all()




def process_command(command):
    if command == "komanda1":
        print("Ovo je prva komanda.")
    elif command == "komanda2":
        print("Ovo je druga komanda.")
    elif command == "kraj":
        print("Izlazim iz programa.")
        exit(0)
    else:
        print("Nepoznata komanda.")

if __name__ == "__main__":
    while True:
        command = input("Unesite komandu koju želite da izvršite: ")
        process_command(command)


