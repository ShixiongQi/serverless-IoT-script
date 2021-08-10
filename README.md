[toc]

## I. Starting up a 2-node cluster on Cloudlab 
1. When starting a new experiment on Cloudlab, select the **small-lan** profile
2. In the profile parameterization page, 
        - Set **Number of Nodes** as **2**
        - Set OS image as **Ubuntu 18.04**
        - Set physical node type as **xl170**
        - Please check **Temp Filesystem Max Space**
        - Keep **Temporary Filesystem Mount Point** as default (**/mydata**)

## II. Extend the disk
On the master node and worker nodes, run
```bash
sudo chown -R $(id -u):$(id -g) <mount point(to be used as extra storage)>
cd <mount point>
git clone https://github.com/ShixiongQi/serverless-IoT-script.git
cd <mount point>/serverless-IoT-script
```
Then run `export MYMOUNT=<mount point>` with the added storage mount point name

- if your **Temporary Filesystem Mount Point** is as default (**/mydata**), please directly run
```
sudo chown -R $(id -u):$(id -g) /mydata
cd /mydata
git clone https://github.com/ShixiongQi/serverless-IoT-script.git
cd /mydata/serverless-IoT-script/environment_setup/
export MYMOUNT=/mydata
```

## III. Deploy Kubernetes Cluster
1. Run `./100-docker_install.sh` without *sudo* on both *master* node and *worker* node
2. Run `source ~/.bashrc`
3. On *master* node, run `./200-k8s_install.sh master <master node IP address>`
4. On *worker* node, run `./200-k8s_install.sh slave` and then use the `kubeadm join ...` command obtained at the end of the previous step run in the master node to join the k8s cluster. Run the `kubeadm join` command with *sudo*

## IV. Deploy Knative Serving and Eventing
### Quick installation (Recommended)
```
./300-knative_install.sh
```
### Manual installation
#### Serving installation
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
#### Eventing installation
1. Install the required CRDs and the core components of Eventing:
```
kubectl apply -f https://github.com/knative/eventing/releases/download/v0.22.0/eventing-crds.yaml
kubectl apply -f https://github.com/knative/eventing/releases/download/v0.22.0/eventing-core.yaml
```
2. Verify the installation until all of the components show a `STATUS` of `Running`:
```
kubectl get pods --namespace knative-eventing
```

## V. Deploy broker layer (brokerchannel/adapter and mosquitto broker)
### Quick installation (Recommended)
```
./400-brokerlayer_install.sh
```
### Manual installation (User only)
If you are a user only, please follow the steps below to install broker layer manually.
```
git submodule sync
git submodule update --init

# deploy brokerchannel service
cd ../brokerchannel/
kubectl apply -f config/

# Deploy the mosquitto broker
cd ../
kubectl apply -f ./nas21/mosquitto.yaml
```
### Manual installation (for developer)
If you changed the brokerchannel implementation and want to rebuild it, please make sure you can install `ko` and properly configure it, i.e., KO_DOCKER_REPO
```
git submodule sync
git submodule update --init

# Install ko
cd ~/ && wget https://github.com/google/ko/releases/download/v0.8.3/ko_0.8.3_Linux_x86_64.tar.gz
tar -zxvf ko_0.8.3_Linux_x86_64.tar.gz
sudo install ko /usr/bin/

# ASSUME YOU WILL DO SOME CHANGES ON THE BROKERCHANNEL
# ...

# deploy brokerchannel service
cd ../brokerchannel/
ko apply -f config/

# Deploy the mosquitto broker
cd ../
kubectl apply -f ./nas21/mosquitto.yaml
```

## VI. Setup event generator
### Quick setup (Recommended)
```
./500-event_generator_setup.sh
```
### Manual setup
```
# Download motion dataset
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1MwJIxaokG52YQ9xkCxoT4AmZprgBoO0z' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1MwJIxaokG52YQ9xkCxoT4AmZprgBoO0z" -O motion_dataset.tar.gz && rm -rf /tmp/cookies.txt
tar -zxvf motion_dataset.tar.gz
mv merl/ /mydata/serverless-IoT-script/motion_gen/
rm motion_dataset.tar.gz

# NOTE: assume using python3.6.9
# Install required python package
sudo apt update
sudo apt install -y python3-pip
pip3 install paho-mqtt
```

## VII. Deploy IoT services (manually)
Go to `nas21` directory before moving forward
### Deploy the brokerchannel (MQTT-to-HTTP Adapter)
```
# NOTE: Before deploying, configure the IP address of mosquitto broker
MOSQUITTO_IP=$(kubectl get pods -l app=mosquitto -o jsonpath='{.items[0].status.podIP}')
sed -i 's#10.244.1.61#'$MOSQUITTO_IP'#g' ksvc_brokerchannel.yaml
sed -i 's#10.244.1.61#'$MOSQUITTO_IP'#g' knative_brokerchannel.yaml
```

You can choose to run either Knative service or Kubernetes service for a simple helloworld application. Please run them seperately, e.g., 1st time runs Knative service, 2nd time runs Kubernetes service. Before switching between different services, please clean up the old deployment first.
### **Knative service**
```
## OPTION-1
# Deploy brokerchannel for Knative Service
kubectl apply -f knative_brokerchannel.yaml
# Deploy the helloworld-go service (Knative Service)
kubectl apply -f knative_helloworld.yaml

## If you want to cleanup the Knative service
kubectl delete -f knative_helloworld.yaml
kubectl delete -f knative_brokerchannel.yaml
```
### Create RPS Pod Autoscaler for Knative service
To create rps autoscaler for Knative serivce, please use `knative_helloworld_autoscaling_rps.yaml`.
The following parameters in `knative_helloworld_autoscaling_rps.yaml` can be configured
```
    metadata:
      annotations:
        autoscaling.knative.dev/metric: "rps"
        autoscaling.knative.dev/target: "1"
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "20"
```
### Create Horizontal Pod Autoscaler (CPU based) for Knative service
To create horizontal autoscaler for Knative serivce, please use `knative_helloworld_autoscaling_cpu.yaml`.
The following parameters in `knative_helloworld_autoscaling_cpu.yaml` can be configured
```
    metadata:
      annotations:
        # For an hpa.autoscaling.knative.dev class Service, the autoscaling.knative.dev/target specifies the CPU percentage target (default "80").
        autoscaling.knative.dev/target: "10"
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "20"
```
### **Kubernetes service**
```
## OPTION-2
# Deploy brokerchannel for Kubernetes Service
kubectl apply -f ksvc_brokerchannel.yaml
# Deploy the helloworld-go service (Kubernetes Service)
kubectl apply -f ksvc_helloworld.yaml

## If you want to cleanup the Kubernetes service
kubectl delete -f ksvc_helloworld.yaml
kubectl delete -f ksvc_brokerchannel.yaml
```
### Create Horizontal Pod Autoscaler for Kubernetes service
Now that the Kubernetes service is running, we will create the autoscaler using kubectl autoscale. The following command will create a Horizontal Pod Autoscaler that maintains between 1 and 10 replicas of the Pods controlled by the Kubernetes deployment we created in the first step of these instructions. Roughly speaking, HPA will increase and decrease the number of replicas (via the deployment) to maintain an average CPU utilization across all Pods of 50% (since each pod requests 200 milli-cores by kubectl run), this means average CPU usage of 100 milli-cores).
```
kubectl autoscale deployment helloworld-go --cpu-percent=10 --min=1 --max=20
```
We may check the current status of autoscaler by running:
```
kubectl get hpa
```

## VIII. Run the motion event generator
```
# I hardcoded the mosquitto address into the generator.py
# But you can change it through the input flags
python3 generator.py -a $MOSQUITTO_IP
```
## IX. Verify whether the service instance receives the messages
If you are running **Kubernetes service**, please run
```
kubectl logs -l app=helloworld-go
```

If you are running **Knative service**, please get the pod name first. You can run
```
kubectl get pods
```
The output will be like
```
sqi009@node0:/mydata/serverless-IoT-script$ kubectl get pods
NAME                                             READY   STATUS    RESTARTS   AGE
helloworld-go-00001-deployment-6584fd8bd-2qdmt   2/2     Running   0          3m20s
mosquitto-5586d6587c-5pnnr                       1/1     Running   0          156m
```
**NOTE: Knative support zero-scaling. Please make sure you started the event generator. Otherwise, you may not find the active pod.**
The pod name is in the format of `helloworld-go-00001-deployment-xxxx-xxx`. Use it to replace the `POD_NAME` in the command below.
```
kubectl logs $POD_NAME -c user-container
```
You can find the message recived info' in the print out.
