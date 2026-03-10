# Parallel Image Processing System

## Project Overview
This project involves the development of a system designed for the parallel processing of large sets of images. The system applies various filters and transformations, saves the processed versions, and maintains a record of the processing status. It is implemented in a single Python file and utilizes both multi-threading and multi-processing to handle concurrent commands and image manipulations.

---

## System Components
The architecture consists of several interconnected modules:

1. Image Registry: Maintains a list of original and processed images, unique identifiers, task IDs, and metadata such as applied filters, processing time, and file sizes.
2. Task Registry: Stores tasks for processing, including image IDs, transformation types, and current status (waiting, in progress, or completed). It uses condition variables to notify the system when a task is finished.
3. Main Reception Thread: The primary thread that initializes all registries, threads, and processes. It continuously listens for input commands and delegates them to handler threads.
4. Command Processing Threads: Individual threads that process user commands (add, process, delete, list, describe, exit) concurrently.
5. Image Processing Processes: Utilizes a multiprocessing pool to execute image transformations independently, ensuring efficient parallel execution.
6. Completion Queue and Thread: A mechanism where completed task IDs are placed in a queue, and a dedicated thread marks them as finished and triggers necessary notifications.

---

## Supported Transformations
The system implements the following image processing techniques:

* Grayscale: Conversion of color images to gray tones using a weighted sum of RGB channels (0.299*R + 0.587*G + 0.114*B).
* Gaussian Blur: A blurring technique achieved by applying a Gaussian filter kernel to pixels to soften sharp transitions.
* Brightness Adjustment: Modifying image brightness by scaling pixel values by a constant factor while preventing value overflow.

---

## Technical Requirements and Execution
The project is submitted via GitHub Classroom. To run the system:

1. Clone the repository and ensure at least one sample image and JSON file are present.
2. Run the Python script.
3. Use the command-line interface to issue commands such as add to import images, process to apply filters via JSON parameters, and exit to safely stop all active components.

---
Developed for the Parallel Algorithms course.
