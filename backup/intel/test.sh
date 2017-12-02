#!usr/bin/bash

ls  -r -alc ~/image>log.txt
inf=$(grep -o -E "image_[0-9]+\.jpg" log.txt)
echo $inf|awk '{print $1}' > ~/image_file.txt

