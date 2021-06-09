#!/bin/bash
mount_path=$MYMOUNT

if [[ $mount_path == "" ]]
then
	echo MYMOUNT env var not defined
	exit 1
fi

pushd $mount_path

# # get Istio
# git clone --recursive https://github.com/mu-serverless/istio
# pushd istio
# #git checkout 803d66019c79ab9e41850c4e27ef26ed2a82025c
# git checkout custom-istio
# rm -rf api
# git clone https://github.com/mu-serverless/api.git
# popd

# # get Envoy
# git clone https://github.com/mu-serverless/lb-envoy-wasm.git
# pushd lb-envoy-wasm
# #git checkout weighted_avg_and_max
# git checkout expose_metrics_for_LC 
# popd

# # get proxy
# #git clone https://github.com/istio/proxy.git
# git clone https://github.com/mu-serverless/proxy-1.git proxy
# pushd proxy
# #git checkout 7879d4f093343ece7c9249c9ee86cf1395fee05e
# git checkout custom-proxy
# popd

# # get knative-func
# git clone https://github.com/mu-serverless/knative-func.git

# get knative-serving
mkdir -p ${GOPATH}/src/knative.dev
pushd ${GOPATH}/src/knative.dev
SERVING_FILE_NAME=serving
git clone https://github.com/cowbon/serving.git ${SERVING_FILE_NAME}
pushd ${SERVING_FILE_NAME}

#git checkout custom-algo-support
# git checkout confidence_flag
popd

# return to script dir
popd
