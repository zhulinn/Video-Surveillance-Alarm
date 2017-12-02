#!/bin/bash

for i in 0 1 2 3 4 5 6 7 8 9 
do
gst-launch-0.10 v4l2src device="/dev/video0" num-buffers=1 ! 'video/x-raw-yuv,format=(fourcc)I420,width=1920,height=1080,framerate=(fraction)30/1' ! jpegenc ! filesink location=~/caffe/image_1$i.jpg -e
done
