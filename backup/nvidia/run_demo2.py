#!/usr/bin/python  
# -*- coding: utf-8 -*-
"""
Created on Thu May 19 13:47:38 2016

@author: root
"""

import os
import numpy as np
import cv2
import subprocess
import matplotlib.pyplot as plt
import find_caffe
import time
import caffe
from sklearn.preprocessing import normalize
from sklearn.linear_model import OrthogonalMatchingPursuit

class image_data_repo:
    def __init__(self, name='image_', image_feature_dict={}, reconsitution_element_nums=8, error_limit=0.2):
        self.name = name
        self.image_feature_dict = image_feature_dict.copy()
        self.reconsitution_element_nums=reconsitution_element_nums
        self.error_limit=error_limit
        self.omp=OrthogonalMatchingPursuit(n_nonzero_coefs=reconsitution_element_nums)
    def image_nums(self):
        return np.size(self.image_feature_dict.keys())
    def add_element(self, keys, values):
        self.image_feature_dict[keys]=values
    def use_image(self, image_feature):
        data = np.array(self.image_feature_dict.values()).T
        self.omp.fit(data, image_feature)
        err = 1 - self.omp.score(data, image_feature)
        if err<self.error_limit:
            return False,err
        else:
            return True,err
    def update(self):
        image_list = self.image_feature_dict.items()
        data = np.array([i[1] for i in image_list])
        name = [i[0] for i in image_list]
        similar_matrix = np.dot(data.T,data)
        for i in range(np.size(name)):
            similar_matrix[i][i]=0            
        similar_coef = np.amax( similar_matrix)
        filename = name[ np.argmax( similar_coef )]
        self.image_feature_dict.pop( filename)  
       # os.system('cp ~/caffe/{} ~/rubbish/'.format(filename)) 
        os.system('rm -f ~/caffe/{}'.format(filename))  
        return
    

def send_image(image):
    os.system('echo {} | ~/send_image.sh'.format(image))
    return         

def caffe_init():
    caffe.set_mode_gpu()
    
    model_def = '/home/ubuntu/caffe/models/bvlc_reference_caffenet/deploy_one_image.prototxt'
    model_weights = '/home/ubuntu/caffe/models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'
    
    net = caffe.Net(model_def,      # defines the structure of the model
                    model_weights,  # contains the trained weights              
                    caffe.TEST)     # use test mode (e.g., don't perform dropout)
    
    # load the mean ImageNet image (as distributed with Caffe) for subtractiond
    mu = np.load('./python/caffe/imagenet/ilsvrc_2012_mean.npy')
    mu = mu.mean(1).mean(1)  # average over pixels to obtain the mean (BGR) pixel values
    #print 'mean-subtracted values:', zip('BGR', mu)
    
    # create transformer for the input called 'data'
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    
    transformer.set_transpose('data', (2,0,1))  # move image channels to outermost dimension
    transformer.set_mean('data', mu)            # subtract the dataset-mean value in each channel
    transformer.set_raw_scale('data', 255)      # rescale from [0, 1] to [0, 255]
    transformer.set_channel_swap('data', (2,1,0))  # swap channels from RGB to BGR
    net.blobs['data'].reshape(1,        # batch size
                              3,         # 3-channel (BGR) images
                              227, 227)  # image size is 227x227
    return net,transformer
    
def camera_init():
    os.system('~/camera_init.sh')

#def image_show_init():
   # plt.ion()
   # plt.figure(figsize=(24,13),dpi=80)

def signal_init():
    os.system('rm -f ~/start/*')
    os.system('rm -f ~/step/*')
    os.system('rm -f ~/next/*')
    os.system('rm -f ~/update/*')
    os.system('rm -f ~/confirm/*')
    os.system('rm -f ~/caffe/*.jpg')
    #os.system('rm -f ~/rubbish/*')
    
def get_feature(net,transformer,image):
    transformed_image = transformer.preprocess('data', image)
    #plt.imshow(image)
    net.blobs['data'].data[...] = transformed_image
    net.forward()
    feature = net.blobs['fc6'].data
    return normalize(feature).reshape(feature.size)

if __name__=='__main__':
    i=0
    state="continues"
    signal_init()
    cap = cv2.VideoCapture(0)

    net,transformer = caffe_init()  
    image_pool = image_data_repo()
    child_start = subprocess.Popen(['inotifywait', '-e' ,'create,move,attrib,delete,access', '/home/ubuntu/start/'])
    child_start.wait()
    while 1:
     _,im = cap.read()
     cv2.namedWindow("Now the library is building")
     cv2.imshow("Now the library is building", im)  
     key = cv2.waitKey(1) & 0xFF
     if i>=60:
         break
     if key == ord("s"):
   	 image_file_name = "image_{}.jpg".format(i)
         cv2.imwrite('image_{}.jpg'.format(i), im) 
 	 image = caffe.io.load_image(image_file_name)     
         feature = get_feature(net,transformer,image)
         image_pool.add_element(image_file_name, feature)
         i=i+1
     elif key == ord("q"):
		break
    cap.release()
    cv2.destroyAllWindows()
    cv2.waitKey(1)
    cv2.waitKey(1)
    cv2.waitKey(1)
    cv2.waitKey(1)  
    print(image_pool.image_nums())
    sent_image=0
    
    '''while image_pool.image_nums()<20:
	i=i+1
	print(image_pool.image_nums())
        # 开子进程检测状态控制信号
        child_step = subprocess.Popen(['inotifywait', '-e' ,'create,move,attrib,delete,access', '/home/ubuntu/step/'])

        image_file_name = "image_{}.jpg".format(i)
        os.system('echo {0} | ~/caffe/get_image_from_usb_camera.sh'.format(image_file_name))
        image = caffe.io.load_image(image_file_name)
        feature = get_feature(net,transformer,image)
        choise,err = image_pool.use_image(feature)
        if choise:
            plt.clf()
            plt.imshow(image)
            plt.title(r'Now the image library have {} images ,reconstruction error for this image is {}'.format(image_pool.image_nums(), err))
            plt.xlabel(r'build the image library...')
            image_pool.add_element(image_file_name, feature)
            plt.draw()
            send_image(image_file_name)
        else:
            plt.clf()
            plt.imshow(image)
            plt.title(r'Now the image library have {} images ,reconstruction error for this image is {}'.format(image_pool.image_nums(), err))
            plt.xlabel(r'build the image library...')
            plt.draw()
         #   os.system('cp {} ~/rubbish/'.format(image_file_name)) 
            os.system('rm -f ~/caffe/{}'.format(image_file_name))
        if child_step.poll()==0:
            state="step mode"
	    os.system('rm -f ~/step/*')
        else:
            child_step.terminate()
        if state=="step mode":
            child_next = subprocess.Popen(['inotifywait', '-e' ,'create,move,attrib,delete,access', '/home/ubuntu/next/'])
	    child_next.wait()
	    time.sleep(0.1)
	    f = open('/home/ubuntu/next/signal.txt','r')
	    temp = f.readlines()[0].split()[0]
	    f.close()
	    os.system('rm -f ~/next/*')
            if temp=='continues':
                state="continues"
    sent_image=20
    i=image_pool.image_nums()'''

    while 1:
        i=i+1
        # 开子进程检测状态控制信号
   #     child_step = subprocess.Popen(['inotifywait', '-e' ,'create,move,attrib,delete,access', '/home/ubuntu/step/'])
        image_file_name = "image_{}.jpg".format(i)
        os.system('echo {0} | ~/caffe/get_image_from_usb_camera.sh'.format(image_file_name))
        image = caffe.io.load_image(image_file_name)
        feature = get_feature(net,transformer,image)
        choise,err = image_pool.use_image(feature)
        print("err: %s") %(err)
        if choise:
            sent_image=sent_image+1
            send_image(image_file_name)
    #        image_pool.update()
        else:
         #   os.system('cp {} ~/rubbish/'.format(image_file_name)) 
            os.system('rm -f ~/caffe/{}'.format(image_file_name))
        if os.listdir('/home/ubuntu/update'):
            print('update checked')
            os.system('rm -f ~/update/*')
     #       child_image=subprocess.Popen(['inotifywait', '-e' ,'create,move,attrib,delete,access', '/home/ubuntu/image/'])
            time.sleep(1.5)
            if os.listdir('/home/ubuntu/confirm'):
             #image_show_init()
             print('receiving confirmed')
             os.system('rm -f ~/confirm/*')
             os.system('ls /home/ubuntu/image >log.txt')
             myfile=open('log.txt')
             a233=myfile.readline()
             a233=a233.split('.')[0]
             a233='/home/ubuntu/image/'+a233+'.jpg'
             image = caffe.io.load_image(a233)
             feature = get_feature(net,transformer,image)
             image_pool.add_element(a233, feature)
             myfile.close()
             #plt.clf()
	     plt.fiure(1)
	     
	     plt.axis('off')
             plt.imshow(image)
             plt.title(r'2333,u finally updated the base successfully')
             plt.draw()
             os.system('rm -f ~/image/*')

        
