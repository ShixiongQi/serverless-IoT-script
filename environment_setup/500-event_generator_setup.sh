#!/bin/bash
# please hardcode the mount path and run this script with non-root user
mount_path=$MYMOUNT

if [[ $mount_path == "" ]]
then
	echo MYMOUNT env var not defined
	exit 1
fi

echo 'Download motion dataset'
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1MwJIxaokG52YQ9xkCxoT4AmZprgBoO0z' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1MwJIxaokG52YQ9xkCxoT4AmZprgBoO0z" -O motion_dataset.tar.gz && rm -rf /tmp/cookies.txt
tar -zxvf motion_dataset.tar.gz
echo 'Move dataset to serverless-IoT-script/motion_gen/'
mv merl/ $mount_path/serverless-IoT-script/motion_gen/
rm motion_dataset.tar.gz

# NOTE: assume using python3.6.9
echo 'Install required python package'
sudo apt update
sudo apt install -y python3-pip
pip3 install paho-mqtt
