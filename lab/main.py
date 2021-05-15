#!/usr/bin/env python3

import os,time,cv2
from threading import Thread, Semaphore,Lock


fileName = '../clip.mp4'

def extract_frames(in_q):
    count = 0
    vidcap = cv2.VideoCapture(fileName)

    while True:
        success, image = vidcap.read() 
        in_q.push(image)

        print("Extracted frame# " + str(count))

        if success and count > 99:
            break
        count += 1
    in_q.push(None)
    print("Finished extracting")

def convert_frames(in_q, out_q):
    count = 0
    while True:
        frame = in_q.pop()
        if frame is None:
            out_q.push(None)
            break
        conv_f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        print("Converted frame# "+str(count))
        count += 1
        out_q.push(conv_f)
    print("Finished grayscale conversion")


def disply_frames(out_q):
    count = 0
    while True:
        frame = out_q.pop()
        if frame is not None:
            cv2.imshow('Video', frame)
            print("Displaying frame# " + str(count))
            if cv2.waitKey(42) and 0xFF == ord("q"):
                break
            count += 1
    cv2.destroyAllWindows()
    print("Display finished")


class PCQueue():

    def __init__(self, cap):
        self.full = Semaphore(0)
        self.empty = Semaphore(cap)
        self.queue = []
        self.lock = Lock()

    def push(self, frame):
        self.empty.acquire()
        self.lock.acquire()
        self.queue.append(frame)
        self.lock.release()
        self.full.release()

    def pop(self):
        self.full.acquire()
        self.lock.acquire()
        frame = self.queue.pop(0)
        self.lock.release()
        self.empty.release()
        return frame



inQ = PCQueue(10)
outQ = PCQueue(10)

t1 = Thread(target=extract_frames, args=(inQ,))
t2 = Thread(target=convert_frames, args= (inQ,outQ))
t3 = Thread(target=disply_frames, args=(outQ,))

t1.start()
t2.start()
t3.start()
