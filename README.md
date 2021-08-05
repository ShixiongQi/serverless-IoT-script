## Starting up a 2-node cluster on Cloudlab 
1. When starting a new experiment on Cloudlab, select the **small-lan** profile
2. In the profile parameterization page, 
        - Set **Number of Nodes** as **2**
        - Set OS image as **Ubuntu 18.04**
        - Set physical node type as **xl170**
        - Please check **Temp Filesystem Max Space**
        - Keep **Temporary Filesystem Mount Point** as default (**/mydata**)

## Extend the disk
On the master node and worker nodes, run
```bash
sudo chown -R $(id -u):$(id -g) <mount point(to be used as extra storage)>
cd <mount point>
git clone https://github.com/ShixiongQi/serverless-IoT-script.git
cd <mount point>/serverless-IoT-script
```
Then run `export MYMOUNT=<mount point>` with the added storage mount point name

- if your **Temporary Filesystem Mount Point** is as default (**/mydata**), please run
```
sudo chown -R $(id -u):$(id -g) /mydata
cd /mydata
git clone https://github.com/ShixiongQi/serverless-IoT-script.git
cd /mydata/serverless-IoT-script/environment_setup/
export MYMOUNT=/mydata
```

## Deploy Kubernetes Cluster
1. Run `./docker_install.sh` without *sudo* on both *master* node and *worker* node
2. Run `source ~/.bashrc`
3. Run `./git_clone.sh` to clone all relevant repos. Edit as required before moving on.
4. On *master* node, run `./k8s_insatll.sh master <master node IP address>`
5. On *worker* node, run `./k8s_install.sh slave` and then use the `kubeadm join ...` command obtained at the end of the previous step run in the master node to join the k8s cluster. Run the `kubeadm join` command with *sudo*
6. On master node, run `./prerequisite.sh` (Currently not needed)

## Deploy Knative Serving
1. Install the required custom resources and the core components of Serving:
```
kubectl apply -f https://github.com/knative/serving/releases/download/v0.22.0/serving-crds.yaml
kubectl apply -f https://github.com/knative/serving/releases/download/v0.22.0/serving-core.yaml
```
2. Install a networking layer (Istio):
```
# Install a properly configured Istio
kubectl apply -f https://github.com/knative/net-istio/releases/download/v0.22.0/istio.yaml
# Install the Knative Istio controller:
kubectl apply -f https://github.com/knative/net-istio/releases/download/v0.22.0/net-istio.yaml
# Fetch the External IP or CNAME:
kubectl --namespace istio-system get service istio-ingressgateway
```
3. Verify the installation until all of the components show a `STATUS` of `Running` or `Completed`
```
kubectl get pods --namespace knative-serving
```
4. Configure DNS to prevent the need to run curl commands with a host header.
```
kubectl apply -f https://github.com/knative/serving/releases/download/v0.22.0/serving-default-domain.yaml
```

## Customize Knative Serving (Please skip this step)
1. If you haven't done the above steps, please complete them before moving to step 2.
2. On master node, run `./ko_install.sh`. Please source ~/.bashrc after you run the script.
3. On master node, run `./go_dep_install.sh` 
4. On master node, run `sudo docker login` to login to your dockerhub account 
5. On master node, run `./build_knative_serving_without_istio.sh` to build and install knative

To uninstall, run `ko delete -f $GOPATH/src/knative.dev/serving/config/`

## Deploy Knative Eventing
1. Install the required CRDs and the core components of Eventing:
```
kubectl apply -f https://github.com/knative/eventing/releases/download/v0.22.0/eventing-crds.yaml
kubectl apply -f https://github.com/knative/eventing/releases/download/v0.22.0/eventing-core.yaml
```
2. Verify the installation until all of the components show a `STATUS` of `Running`:
```
kubectl get pods --namespace knative-eventing
```
3. Install a default channel (messaging) layer: <span style="color:red">(Deprecated)</span>.
```
kubectl apply -f https://github.com/knative/eventing/releases/download/v0.22.0/in-memory-channel.yaml
```
4. Install a broker layer: <span style="color:red">(Deprecated)</span>
```
kubectl apply -f https://github.com/knative/eventing/releases/download/v0.22.0/mt-channel-broker.yaml
```

## Deploy camel-k source <span style="color:red">(Deprecated)</span>
As camel-k source is no longer supported by the community, Kamel is recommended as a replacement of camel-k source.
The way to install Kamel: https://camel.apache.org/camel-k/latest/installation/installation.html
You can also try the commands below, which I used to set up my environment:
```
wget https://github.com/apache/camel-k/releases/download/v1.5.0/camel-k-client-1.5.0-linux-64bit.tar.gz
tar -zxvf camel-k-client-1.5.0-linux-64bit.tar.gz
cd camel-k-client/
sudo install kamel /usr/bin/
sudo -s
kamel install --cluster-setup --registry=docker.io/shixiongqi/ # Replace with your own docker registry
exit
```

## Deploy IoT services
```
cd serverless-IoT-script/
# Deploy the mosquitto broker
kubectl apply -f ./nas21/mosquitto.yaml
# Deploy the brokerchannel (MQTT-to-HTTP Adapter) --- <span style="color:red">Before deploying, configure the IP address of mosquitto broker</span>
kubectl apply -f ksvc_brokerchannel.yaml
# Deploy the helloworld-go service (Kubernetes Service)
kubectl apply -f ./nas21/ksvc_helloworld.yaml
```

## Run the motion event generator
```
# download the dataset and install required python package
# I hardcoded the mosquitto address into the generator.py
# But you can change it through the input flags
python3 generator.py -f $MOSQUITTO_IP
```
