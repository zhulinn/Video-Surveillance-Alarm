#!/bin/bash

read -p "Enter image file name :" name
cd 
gst-launch-0.10 v4l2src device="/dev/video0" num-buffers=1 ! 'video/x-raw-yuv,format=(fourcc)I420,width=1280,height=720,framerate=(fraction)30/1' ! jpegenc ! filesink location=~/caffe/$name -e
