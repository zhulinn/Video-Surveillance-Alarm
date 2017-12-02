#!/bin/bash
# start signal
read -p "enter the image name you want to update:" image_name
sftp ubuntu@192.168.199.100 <<EOF
cd /home/ubuntu/update
put signal.txt
cd /home/ubuntu/image
put ${image_name}
cd /home/ubuntu/confirm
put signal.txt
EOF
