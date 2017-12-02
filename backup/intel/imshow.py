#!/usr/bin/ipython
import mraa
import os
import matplotlib.pyplot as plt
import threading  
import psutil
import multiprocessing
import subprocess
from time import ctime, sleep 
import multiprocessing
import cv2
green = mraa.Gpio(23)
green.dir(mraa.DIR_OUT)  
red = mraa.Gpio(25)
red.dir(mraa.DIR_OUT)
beep = mraa.Gpio(26)
beep.dir(mraa.DIR_OUT)
'''
def signal_init():
    os.system('rm -f ~/image/*')
    os.system('rm -f ~/bin/*')
plt.ion()
plt.figure(figsize=(24,13))
#im=plt.imread('init_image.jpg')
#plt.imshow(im)
#plt.draw()
signal_init()
'''
class Process(multiprocessing.Process): #The timer class is derived from the class threading.Thread  
    def __init__(self,interval):  
        multiprocessing.Process.__init__(self)  
        pid = os.getpid()        
        self.interval = interval
    def run(self): 
	while 1: 
	   green.write(0) 	
    	   red.write(1)
     	   beep.write(1) 
   	   sleep(self.interval)
   	   red.write(0)
   	   beep.write(0) 
   	   sleep(self.interval)
	  
class initial(multiprocessing.Process):  
    def __init__(self):  
        multiprocessing.Process.__init__(self)  
        pid = os.getpid()        
    def run(self): 
	green.write(0)
	beep.write(1)
	sleep(0.2)
	beep.write(0)
	green.write(1)
	sleep(0.1)
	green.write(0)
	beep.write(1)
	sleep(0.2)
	green.write(1)
	beep.write(0)
	 

def stop(pid):  
        p = psutil.Process(pid)
        p.suspend()
	green.write(1)
	red.write(0)
	beep.write(0) 
        #print 'suspend: %s ' %(pid)
def wake(pid):
        #print 'resume: %s ' %(pid)
        p=psutil.Process(pid)
        p.resume()


i=initial()
i.start()	#starting hint

p = Process(0.3)
p.start()
stop(p.pid) 	#alarm sub

signal=r'/home/jhm/bin/signal.txt'
   # state = subprocess.Popen(['inotifywait', '-e', 'create,move,delete,attrib' ,'/home/jhm/bin/'])
while 1:
    cv2.namedWindow("Image")   
    if os.path.exists(signal):
	wake(p.pid)
	os.system('bash ~/test.sh')
    	f=open('image_file.txt','r')
    	filename='image/{}'.format(f.readline()).split()[0]
    	f.close()
   	os.system('rm -f ~/bin/*')
        im=cv2.imread(filename)
        cv2.imshow("Image", im)   

  #  if os.listdir('/home/jhm/bin'):
	#wake(p.pid)
	#os.system('rm -f ~/bin/*')
    key=cv2.waitKey(1) & 0xFF	
    if key == ord("s"):
    	os.system('bash ~/start.sh')
    elif key == ord("a"):
	stop(p.pid)

    elif key == ord("n"):
	stop(p.pid)    	
	os.system('bash ~/update.sh')
    elif key == ord("q"):
		break


    '''
    os.system('bash ~/test.sh')
    f=open('image_file.txt','r')
    filename='image/{}'.format(f.readline()).split()[0]
    f.close()
    os.system('rm -f ~/bin/*')
    im=plt.imread(filename)
    plt.clf()
    plt.imshow(im)
    plt.draw()
    '''




