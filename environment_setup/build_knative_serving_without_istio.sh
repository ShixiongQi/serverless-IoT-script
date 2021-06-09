#!/bin/bash

# https://github.com/knative/serving/blob/master/DEVELOPMENT.md#starting-knative-serving
#please git clone knative-fun and specify its path
mount_path=$MYMOUNT

if [[ $mount_path == "" ]]
then
	echo MYMOUNT env var not defined
	exit 1
fi

sudo chmod 777 $mount_path
cd ${mount_path}
#git clone https://github.com/mu-serverless/knative-func.git
knative_fun=$mount_path/knative-func
#echo "====== please install go, dep, ko ======"
#read check
#mkdir -p ${GOPATH}/src/knative.dev
cd ${GOPATH}/src/knative.dev

#echo "====== please verify the git repository 'serving' exists ======"
#read check
# # the latest version
# git clone git@github.com:hotjunfeng/serving_li.git
# # change the folder name from "serving_li" to "serving".
SERVING_FILE_NAME=serving
#git clone https://github.com/mu-serverless/serving_li.git ${SERVING_FILE_NAME} 

# make no sense.
# echo "====== please verify 'serving' file name is ${SERVING_FILE_NAME} ======" 
# read check 

cd ${SERVING_FILE_NAME}
# git remote add upstream git@github.com:knative/serving.git
# git remote set-url --push upstream no_push
#git checkout custom-algo-support
# For minikube or Kubernetes on Docker Desktop
kubectl create clusterrolebinding cluster-admin-binding \
  --clusterrole=cluster-admin \
  --user=$(id -nu)

# # deploy istio
# kubectl apply -f ./third_party/istio-1.3-latest/istio-crds.yaml
# while [[ $(kubectl get crd gateways.networking.istio.io -o jsonpath='{.status.conditions[?(@.type=="Established")].status}') != 'True' ]]; do
#   echo "Waiting on Istio CRDs"; sleep 1
# done
# kubectl apply -f ./third_party/istio-1.3-latest/istio-local.yaml

# Deploy cert-manager CRDs
kubectl apply -f ./third_party/cert-manager-0.12.0/cert-manager-crds.yaml
# while [[ $(kubectl get crd certificates.certmanager.k8s.io -o jsonpath='{.status.conditions[?(@.type=="Established")].status}') != 'True' ]]; do
#   echo "Waiting on Cert-Manager CRDs"; sleep 1
# done

# Edited config-network.yaml:
# Don't always directly copy the configure file.
cp $knative_fun/knative_install/config-network.yaml ${GOPATH}/src/knative.dev/${SERVING_FILE_NAME}/config/config-network.yaml
echo "====== please check config-network.yaml ======"
read check

sudo docker login

#sudo chown "$USER":root /users/"$USER"/.docker -R
#sudo chmod g+rwx "/users/$USER/.docker" -R
sudo chown -R $(id -u):$(id -g) /users/$(id -nu)/.docker
sudo chmod g+rwx "/users/$(id -nu)/.docker" -R
# Connect to gcr.io. Have to use proxy.
ko apply -f config/

cd $knative_fun/knative_install_v0_8
chmod +x ./knative_deploy_auto_scaling_rule.sh
./knative_deploy_auto_scaling_rule.sh

echo "====== if you encounter: error: unable to recognize STDIN: no matches for kind Image in version"
echo "====== please re-run ko apply -f config/"
echo " "

echo "====== please verify the metric server exists ======"
read check
cd $knative_fun
kubectl apply -f metric_authority.yaml
sudo ./clean_disk.sh

echo "kubectl -n knative-serving get pods -w"
kubectl -n knative-serving get pods -w

# Remove the knative
# ko delete -f config/
