# VisionParallel: Image Processing Parallel System

## Project Overview
VisionParallel is an advanced system developed for the Parallel Algorithms course, designed for the efficient and concurrent processing of large image datasets. The system allows for the application of various visual filters and transformations while maintaining precise records of processing status and data integrity. The architecture leverages Python’s multi-threading and multi-processing ecosystems to achieve maximum throughput and scalability.

---

## System Architecture and Components
The system is divided into several key components that enable asynchronous operation and secure resource manipulation:

1. Image Registry: A central ledger that tracks original and processed images, their unique identifiers, task associations, and metadata such as processing time and file sizes.
2. Task Registry: A module for managing the task lifecycle, tracking transformations and current status (waiting, in progress, completed). It utilizes synchronization primitives to notify the system upon task completion.
3. Main Management Thread: The central controller that initializes the system, receives user commands, and distributes them to the appropriate execution threads.
4. Command Processing Threads: Dedicated threads responsible for executing user operations such as adding, deleting, and listing information, allowing multiple management commands to run simultaneously.
5. Image Processing Processes: An execution layer that utilizes a Process Pool (multiprocessing.Pool) to apply actual transformations, bypassing global interpreter lock (GIL) limitations to achieve true parallelism.

---

## Functional Capabilities
The system supports a variety of operations for managing and processing visual data:

- Dynamic Image Management: Securely copying images into the system and controlled deletion with task dependency verification.
- Task-Based Processing: Defining transformation parameters via JSON files and tracking dependencies between different tasks.
- Feedback Mechanism: A mechanism based on Queues and callback functions that ensures tasks are marked as finished in real-time.
- Output Management: Viewing available images and reconstructing the detailed history of how each image was generated through the identifier system.

---

## Supported Transformations
The system implements mathematically precise algorithms for image modification:

- Grayscale: Converting color images to grayscale using a weighted sum of RGB channels (0.299R + 0.587G + 0.114B).
- Gaussian Blur: Applying a Gaussian filter and convolution matrix to soften transitions within the image.
- Brightness Adjustment: Scaling pixel values to achieve desired lighting or contrast levels while protecting against value overflow.

---

## Technical Setup and Execution
The project is implemented in Python using standard libraries for parallel programming.

1. Clone the repository to your local machine.
2. Ensure the required images and JSON configuration files are present in the root directory.
3. Launch the main script using the following command:
   python main.py
4. The system will wait for command input via the standard input (add, process, list, delete, describe, exit).

---
Project developed as part of the Parallel Algorithms course curriculum.
