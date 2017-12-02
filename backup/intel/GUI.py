# This Python file uses the following encoding: utf-8
import os
import matplotlib.pyplot as plt
import threading
import psutil
import multiprocessing
import subprocess
from time import ctime, sleep
import multiprocessing
import mraa
from FileDialog import *
import re
from  Tkinter import  *
import ImageTk
import Image
import tkFont
from tkMessageBox import *
global a
a=1
class Process(multiprocessing.Process): #The timer class is derived from the class threading.Thread
    def __init__(self,interval):
        multiprocessing.Process.__init__(self)
	      
	pid = os.getpid()
	self.interval=interval
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
    def run(self):
	green.write(0)
	beep.write(1)
	sleep(0.6)
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
green = mraa.Gpio(23)
green.dir(mraa.DIR_OUT)
red = mraa.Gpio(25)
red.dir(mraa.DIR_OUT)
beep = mraa.Gpio(21)
beep.dir(mraa.DIR_OUT)
p = Process(0.3)
p.start()
stop(p.pid) 	#alarm sub
i=initial()
i.start()	#starting hint
temp="1"
def signal_init():
    os.system('rm -f /home/jhm/image/*')
    os.system('rm -f /home/jhm/bin/*')
signal_init()	
filename = "/home/jhm/init_image.jpg"
def st_click():
    os.system(' /home/jhm/start.sh')
def ac_click():
    stop(p.pid)    
    sleep(0.5)
    root.update()

    sleep(3.5)
def nm_click():
    a=0
    stop(p.pid)

    fd = LoadFileDialog(root) # 创建打开文件对话框
    image_name = fd.go()
    os.system('echo {} | /home/jhm/update.sh'.format(image_name))
    os.system('rm -f /home/jhm/bin/*')
    sleep(3)
    a=1
def ex_click():
 	root.destroy()
root = Tk()
root.title("基于监控视频的异常报警系统")
#root.geometry('640x650')                 #是x 不是*
root.resizable(width=True, height=True) #宽不可变, 高可变,默认为True
frame = Frame(root)
frame.pack()

ft = tkFont.Font(family = 'Fixdsys',size = 20,weight = tkFont.BOLD)
stbutton = Button(frame, text="开始",font=ft,width=9,height=1,command = st_click)
stbutton.grid(row=1,column=1)
		
acbutton = Button(frame, text="确认警报",font=ft,width=9,height=1,command = ac_click)
acbutton.grid(row=1,column=2)

nmbutton = Button(frame, text="解除异常",font=ft,width=9,height=1,command = nm_click)
nmbutton.grid( row=1,column=3)
		
exbutton = Button(frame, text="退出",font=ft,width=9,height=1,command = ex_click)
exbutton.grid(row=1,column=4)

ft1 = tkFont.Font(family = 'Fixdsys',size = 12)
label2 = Label(frame, text='PS: 解除异常——使系统认定当前情景为正常状态，不再发出异常警报，达到自主学习目的',font=ft1)
label2.grid(row=2,column=1,columnspan=4)

img =  ImageTk.PhotoImage(file=filename)#read image
label = Label(frame, image=img)
label.grid(row=3,column=1,columnspan=4)

signal = '/home/jhm/bin/signal.txt'

while 1:
    root.update()
    if os.path.exists(signal) & a:
        os.system('rm -f /home/jhm/bin/*')
        wake(p.pid)#alarm
	print "Anomaly"
        os.system('bash /home/jhm/test.sh')
        f=open('image_file.txt','r')
        filename='/home/jhm/image/{}'.format(f.readline()).split()[0]
        f.close()		#read path
	 
	img =  ImageTk.PhotoImage(file=filename)#read image
	label.destroy()	
	label = Label(frame, image=img)
	label.grid(row=2,column=1,columnspan=4)
	


