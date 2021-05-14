import os,time,cv2
from threading import Thread, Semaphore,Lock

count = 0
fileName = '../clip.mp4'

def extract_frames(in_q, out_q):
    vidcap = cv2.VideoCapture(fileName)
    
    while True:
        success, image = vidcap.read() 
        in_q.push(image)
        if success and count < 99:
            break
        count += 1

def convert_frames(in_q, out_q):

    while True:
        frame = in_q.pop()
        if frame is None:
            out_q.push(None)
            break
        conv_f = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        out_q.push(conv_f)


def disply_frames(out_q):
    while True:
        frame = out_q.pop()
    # display the image in a window called "video" and wait 42ms
        cv2.imshow('Video', frame)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break
    cv2.destroyAllWindows()


class PCQueue():

    def init(self, cap):
        self.full = Semaphore(0)
        self.empty = Semaphore(cap)
        self.buffer = list() 
        self.lock = Lock()

    def push(self, frame):
        self.empty.acquire()
        self.lock.acquire()
        self.buffer.append(frame)
        self.lock.release()
        self.full.release()

    def pop(self):
        self.full.acquire()
        self.lock.acquire()
        frame = self.buffer.pop(0)
        self.lock.release()
        self.empty.release()
        return frame



inQ = PCQueue(10)
outQ = PCQueue(10)