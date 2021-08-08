#!/bin/bash

echo 'Install Knative Serving'
kubectl apply -f https://github.com/knative/serving/releases/download/v0.22.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/v0.22.0/serving-core.yaml

echo 'Install Istio'
kubectl apply -f https://github.com/knative/net-istio/releases/download/v0.22.0/istio.yaml # Install a properly configured Istio
kubectl apply -f https://github.com/knative/net-istio/releases/download/v0.22.0/net-istio.yaml # Install the Knative Istio controller
kubectl --namespace istio-system get service istio-ingressgateway # Fetch the External IP or CNAME

echo 'Configure DNS to prevent the need to run curl commands with a host header'
kubectl apply -f https://github.com/knative/serving/releases/download/v0.22.0/serving-default-domain.yaml

echo 'Install the required CRDs and the core components of Eventing'
kubectl apply -f https://github.com/knative/eventing/releases/download/v0.22.0/eventing-crds.yaml
kubectl apply -f https://github.com/knative/eventing/releases/download/v0.22.0/eventing-core.yaml

echo 'Verify the installation until all of the components show a STATUS of Running or Completed'
kubectl get pods --namespace knative-serving
echo 'Verify the installation until all of the components show a STATUS of Running'
kubectl get pods --namespace knative-eventing
