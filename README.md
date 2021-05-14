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
git clone https://github.com/ShixiongQi/serverless-IoT.git
cd <mount point>/serverless-IoT
```
Then run `export MYMOUNT=<mount point>` with the added storage mount point name

- if your **Temporary Filesystem Mount Point** is as default (**/mydata**), please run
```
sudo chown -R $(id -u):$(id -g) /mydata
cd /mydata
git clone https://github.com/ShixiongQi/serverless-IoT.git
cd /mydata/serverless-IoT
export MYMOUNT=/mydata
```

## Deploy Kubernetes Cluster
1. Run `./docker_install.sh` without *sudo* on both *master* node and *worker* node
2. Run `source ~/.bashrc`
3. On *master* node, run `./k8s_insatll.sh master <master node IP address>`
4. On *worker* node, run `./k8s_install.sh slave` and then use the `kubeadm join ...` command obtained at the end of the previous step run in the master node to join the k8s cluster. Run the `kubeadm join` command with *sudo*

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
3. Install a default channel (messaging) layer:
```
kubectl apply -f https://github.com/knative/eventing/releases/download/v0.22.0/in-memory-channel.yaml
```
4. Install a broker layer:
```
kubectl apply -f https://github.com/knative/eventing/releases/download/v0.22.0/mt-channel-broker.yaml
```

## Deploy IoT service chains
```
kubectl apply -f deployment/mt_broker.yaml
kubectl apply -f deployment/event_source.yaml
kubectl apply -f deployment/temp/
```

## Metrics to be collected
1. The metrics we are collecting do not provide enough information to help the control plane to make the decision. 
```
struct metrics_record {
      _u64 appRequestCountM;
      _u64 appResponseTimeInMsecM;
} __attributed__((packed));
```
* The metrics collected by eproxy:
        * *appRequestCountM*: The number of requests that are routed to user-container
        * *appResponseTimeInMsecM*: The response time in millisecond
* The metrics collected by other components
        * *requestCountM*: The number of requests that are routed to queue-proxy
        * *responseTimeInMsecM*: The response time in millisecond
        * *queueDepthM*: The current number of items in the serving and waiting queue, or not reported if unlimited concurrency (Collected by where the buffer locates)

## Deploy the netdata
1. Run `bash <(curl -Ss https://my-netdata.io/kickstart.sh)`, wait until the installation completes.
2. Install the EPROXY program
	1. Run `cp eproxy.chart.py /usr/libexec/netdata/python.d/eproxy.chart.py`
3. Restart netdate service
	1. Run `systemctl restart netdata`
4. Scraping the metrics remotely
	1. `curl 'http://128.110.154.174:19999/api/v1/data?chart=eproxy.RequestCount&after=-1'`
	2. `curl 'http://128.110.154.174:19999/api/v1/data?chart=eproxy.ReponseTime&after=-1'`
	The output will be like
```
{
 "labels": ["time", "random1", "random0", "random2", "random3"],
    "data":
 [
      [ 1620602324, 38, 59, 86, 88]
  ]
}
```

 
