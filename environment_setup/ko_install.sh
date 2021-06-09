#!/bin/bash
#please hardcode the dockerhub_account and run this script
#don't forget to source ~/.bashrc after running this script
#if you get some permission issue, please add the permission 
#to the corresponding files or path
dockerhub_account=$DOCKER_USER

if [[ $dockerhub_account == "" ]]
then
	echo DOCKER_USER not defined
	exit 1
fi

#GO111MODULE=on go get github.com/google/ko/cmd/ko
go get github.com/google/ko
echo "export KO_DOCKER_REPO='docker.io/$dockerhub_account'" >> ~/.bashrc
echo "please source ~/.bashrc"
