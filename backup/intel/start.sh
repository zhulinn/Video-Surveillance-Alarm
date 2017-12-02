#!/bin/bash
# start signal
sftp ubuntu@192.168.199.100 2>null<<EOF
ubuntu
cd /home/ubuntu/start
put signal.txt
EOF
