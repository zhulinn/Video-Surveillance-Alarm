#!/usr/bin/python  
# -*- coding: utf-8 -*-
"""
Created on Thu May 19 13:47:38 2016

@author: root
"""

import os
import numpy as np
import subprocess
import matplotlib.pyplot as plt
import find_caffe
import time
import caffe
from sklearn.preprocessing import normalize
from sklearn.linear_model import OrthogonalMatchingPursuit

class image_data_repo:
    def __init__(self, name='image_', image_feature_dict={}, reconsitution_element_nums=6, error_limit=0.1):
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
        similar_coef = np.amax( np.dot(data.T,data))
        filename = name[ np.argmax( similar_coef )]
        dst_filename = '';
        self.image_feature_dict.pop( filename)  
        os.system('cp ~/caffe/{} ~/rubbish/'.format(filename)) 
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

def image_show_init():
    plt.ion()
    plt.figure(figsize=(24,13),dpi=80)

def signal_init():
    os.system('rm -f ~/start/*')
    os.system('rm -f ~/step/*')
    os.system('rm -f ~/next/*')
    os.system('rm -f ~/rubbish/*')
    
def get_feature(net,transformer,image):
    transformed_image = transformer.preprocess('data', image)
    #plt.imshow(image)
    net.blobs['data'].data[...] = transformed_image
    net.forward()
    feature = net.blobs['fc6'].data
    return normalize(feature).reshape(feature.size)

if __name__=='__main__':
    state="continues"
    signal_init()
    camera_init()
    image_show_init()
    net,transformer = caffe_init()  
    image_pool = image_data_repo()
    #child_start = subprocess.Popen(['inotifywait', '-e' ,'create,move,attrib,delete,access', '/home/ubuntu/start/'])
    #child_start.wait()
    print(time.clock())
    for i in range(10):
	print(time.clock())
        image_file_name = "image_{}.jpg".format(i)
        os.system('echo {0} | ~/caffe/get_image_from_usb_camera.sh 1>/dev/null 2>&1'.format(image_file_name))
	print('capture_image: ',time.clock())
        image = caffe.io.load_image(image_file_name)
        feature = get_feature(net,transformer,image)
        image_pool.add_element(image_file_name, feature)
	print('save_feature: ',time.clock())
	plt.clf()	
        plt.imshow(image)
	plt.title(r'the {}th image'.format(i+1))
        plt.xlabel(r'build the image library...')
        plt.draw()
	print(image_pool.image_nums())
	print(time.clock())

    raw_input('stay here:\n')

    while image_pool.image_nums()<30:
	i=i+1
	print(image_pool.image_nums())
        # 开子进程检测状态控制信号
        #child_step = subprocess.Popen(['inotifywait', '-e' ,'create,move,attrib,delete,access', '/home/ubuntu/step/'])

        image_file_name = "image_{}.jpg".format(i)
        os.system('echo {0} | ~/caffe/get_image_from_usb_camera.sh 1>/dev/null 2>&1'.format(image_file_name))
        image = caffe.io.load_image(image_file_name)
        feature = get_feature(net,transformer,image)
	print('before OMP:',time.clock())
        choise,err = image_pool.use_image(feature)
	print('after OMP:',time.clock())
        if choise:
            plt.clf()
            plt.imshow(image)
            plt.title(r'Now the image library have {} images ,reconstruction error for this image is {}, this is an abnormal image'.format(image_pool.image_nums(), err))
            plt.xlabel(r'build the image library...')
            image_pool.add_element(image_file_name, feature)
            plt.draw()
	    raw_input('next:\n')
            #send_image(image_file_name)
        else:
            plt.clf()
            plt.imshow(image)
            plt.title(r'Now the image library have {} images ,reconstruction error for this image is {}, this is an normal image'.format(image_pool.image_nums(), err))
            plt.xlabel(r'build the image library...')
            plt.draw()
            os.system('cp {} ~/rubbish/'.format(image_file_name)) 
            os.system('rm -f ~/caffe/{}'.format(image_file_name))
	'''
        if child_step.poll()==0:
            state="step mode"
	    os.system('rm -f ~/step/*')
        else:
            child_step.terminate()
        if state=="step mode":
            child_next = subprocess.Popen(['inotifywait', '-e' ,'create,move,attrib,delete,access', '/home/ubuntu/next/'])
	    child_next.wait()
	    time.sleep(0.01)
	    f = open('/home/ubuntu/next/signal.txt','r')
	    temp = f.readlines()[0].split()[0]
	    f.close()
	    os.system('rm -f ~/next/*')
            if temp=='continues':
                state="continues"
	'''
    i=image_pool.image_nums()
    while i<1000:
	i=i+1
        # 开子进程检测状态控制信号
	'''	
        child_step = subprocess.Popen(['inotifywait', '-e' ,'create,move,attrib,delete,access', '/home/ubuntu/step/'])
	'''	
	print('before capture:',time.clock())
        image_file_name = "image_{}.jpg".format(i)
        os.system('echo {0} | ~/caffe/get_image_from_usb_camera.sh 1>/dev/null 2>&1'.format(image_file_name))
	print('before load:',time.clock())
        image = caffe.io.load_image(image_file_name)
	print('before get_feature:',time.clock())
        feature = get_feature(net,transformer,image)
	print('before OMP:',time.clock())
        choise,err = image_pool.use_image(feature)
        if choise:
	    '''
	    plt.clf()
            plt.imshow(image)
            plt.title(r'Now the client has sent {} images ,reconstruction error for this image is {}'.format(i, err))
            plt.xlabel(r'the image library has been build')
	    '''	    
	    print('before add_element:',time.clock())
            image_pool.add_element(image_file_name, feature)
	    '''
            plt.draw()
            send_image(image_file_name)
	    '''
	    print('before update:',time.clock())
            image_pool.update()
	    print('after update:',time.clock())
        else:
	    '''
	    plt.clf()
            plt.imshow(image)
            plt.title(r'Now the client has sent {} images ,reconstruction error for this image is {}'.format(i, err))
            plt.xlabel(r'the image library has been build')
            plt.draw()
	    '''
            os.system('cp {} ~/rubbish/'.format(image_file_name)) 
            os.system('rm -f ~/caffe/{}'.format(image_file_name))
	if i==70:
	    raw_input('123:')
	'''
        if child_step.poll()==0:
            state="step mode"
	    os.system('rm -f ~/step/*')
        else:
            child_step.terminate()
        if state=="step mode":
            child_next = subprocess.Popen(['inotifywait', '-e' ,'create,move,attrib,delete,access', '/home/ubuntu/next/'])
	    child_next.wait()
	    time.sleep(0.01)
	    f = open('/home/ubuntu/next/signal.txt','r')
	    temp = f.readlines()[0].split()[0]
	    f.close()
	    os.system('rm -f ~/next/*')
            if temp=='continues':
                state="continues"
	'''      
