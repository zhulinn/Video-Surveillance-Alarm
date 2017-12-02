#!/bin/bash
# send_image.sh 
read -p "Enter image file name :" image_name
#image_name=image_3.jpg
src_image_root=~/caffe
src_bin_root=~/caffe
dst_image_root=/home/jhm/image
dst_bin_root=/home/jhm/bin
sftp jhm@192.168.199.140 <<EOF
cd ${dst_image_root}
put $src_image_root/${image_name}
cd ${dst_bin_root}
put ${src_bin_root}/signal.txt
quit
EOF
