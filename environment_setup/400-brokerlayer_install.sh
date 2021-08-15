#!/bin/bash
# please hardcode the mount path and run this script with non-root user
mount_path=$MYMOUNT

if [[ $mount_path == "" ]]
then
	echo MYMOUNT env var not defined
	exit 1
fi

# cd $mount_path/serverless-IoT-script/
# git submodule sync
# git submodule update --init

# cd ./brokerchannel/
# # deploy brokerchannel service
# kubectl apply -f ./config/

# Deploy the mosquitto broker
kubectl apply -f $mount_path/serverless-IoT-script/nas21/mosquitto.yaml

echo 'Install Camel-K binary'
mkdir camel && cd camel
wget https://github.com/apache/camel-k/releases/download/v1.5.0/camel-k-client-1.5.0-linux-64bit.tar.gz && tar -zxvf camel-k-client-1.5.0-linux-64bit.tar.gz
sudo install kamel /usr/bin

echo 'ATTENTION: please login to your docker account first and then install kamel into Kubernetes'
# sudo docker login
# sudo kamel install --registry docker.io --organization your-user-id-or-org --registry-auth-username your-user-id --registry-auth-password your-password

# kubectl describe IntegrationPlatform camel-k