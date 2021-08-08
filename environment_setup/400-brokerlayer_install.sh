#!/bin/bash
# please hardcode the mount path and run this script with non-root user
mount_path=$MYMOUNT

if [[ $mount_path == "" ]]
then
	echo MYMOUNT env var not defined
	exit 1
fi

cd $mount_path/serverless-IoT-script/
git submodule sync
git submodule update --init

cd ./brokerchannel/
# deploy brokerchannel service
kubectl apply -f ./config/

# Deploy the mosquitto broker
kubectl apply -f $mount_path/serverless-IoT-script/nas21/mosquitto.yaml