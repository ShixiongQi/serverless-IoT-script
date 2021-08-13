# NAS 21 paper experiment instructions

### Experiment setup
We use two `xl170` nodes on Cloudlab@Utah. Each node has a 20-core Intel E5-2640v4 at 2.4 GHz and 64GB memory, and 2 Dual-port Mellanox ConnectX-4 25 Gb NIC. Each node is created with default `small_lan` profile. **One node is configured as master node, which will run `generator.py` to generate events. The other node is configured as worker, which will run the service instance (pod) only.**
We use Ubuntu 18.04 with kernel version 4.15.0-88-generic. We use Kubernetes v1.19.0 and Knative v0.22 in the experiment. We run the `helloworld-go` as the service to process the events.

**We have three different experiment configurations:** NOTE: config-2 is not available.
1. The service instances are deployed as native Kubernetes services

Generator.py --> MQTT broker (mosquitto) -> brokerchannel -> Kubernetes service

2. The service instances are deployed as native Kubernetes serivces with eProxy equipped

Generator.py --> MQTT broker (mosquitto) --> brokerchannel --> eProxy  --> Kubernetes service

3. The service instances are deployed as Knative services with queue proxy equipped

Generator.py --> MQTT broker (mosquitto) --> brokerchannel --> Queue proxy  --> Knative service

To deploy **CONFIG-1** and **CONFIG-2**, please use `ksvc_brokerchannel.yaml` and `ksvc_helloworld.yaml`

To deploy **CONFIG-3**, please use `knative_brokerchannel.yaml` and `knative_helloworld.yaml`

### Experiment plan
The experiment plan is to generate CPU and RPS results as we currently did in the NAS paper.
x-axis is the number of instances. y-axis is the CPU usage or RPS value.
With a given event generation rate, e.g., 780 events/second, we can adjust the autoscaling parameters and vary the number of instances between 1 ~ 20. And then collect the CPU usage under that number of instances. To collected results can be used to plot the Fig.2 as in the paper.

### How to collect results
One of the results we need to collect is the overall CPU usage of worker node. To automate the CPU usage collection, please run [`cpu_measure.sh $MEASUREMENT_TIME`][cpu measure]. For example, if you want to do a 60-second measurement, please run `cpu_measure.sh 60`. The output will be like
```
========= Check whether mpstat is installed =========
mpstat installed
========= Check whether bc is installed =========
bc installed
Collect CPU usage for 4 seconds
CPU usage: 3.22
```

### How to configure autoscaling parameters
Configurable parameters:
1. event generation rate
2. cpu-based autosacling parameter for Kubernetes service
3. rps-based autoscaling parameter for Knative service
#### Event generation rate setup
The default event generation rate of `merl-0114` dataset is 0.78 events/second, which is not enough to stress the service instances, we can scale the initial event generation rate based on the requirement:
```
python3 generator.py -a $MOSQUITTO_IP -s $RATE_SCALE_DEGREE
```
If you set `RATE_SCALE_DEGREE` as 1000, the event generation rate will be scaled up to 780 events/second.

#### Kubernetes servivce
**Kubernetes servivce** is configured to use [CPU-based autoscaling][ksvc helloworld]. We specify each Pod (pod and instance are used interchangably) request **500m CPU core (0.5 CPU core)**. The average CPU utilization across all instances are kept as **60%**. Details are described below.

As the node provides 20 CPU cores, we specify the requested CPU core for a single service instance as 500m (0.5 CPU core).
```yaml
    resources:
    limits:
        cpu: 700m
    requests:
        cpu: 500m
```
To enable the autoscaling policy for the given Kubernetes service, we need to apply
```
kubectl autoscale deployment helloworld-go --cpu-percent=60 --min=1 --max=20
```
The autoscaling policy creates a Horizontal Pod Autoscaler that maintains between 1 and 20 replicas of the instances controlled by the Kubernetes deployment we created by [`ksvc_helloworld.yaml`][ksvc helloworld]. `--cpu-percent` maintain an average CPU utilization across all instances. In our configuration, we keep it as 60% (since each pod requests 500 milli-cores), this means average CPU usage of 300 milli-cores).

#### Knative servivce
**Knative servivce** is configured to use [RPS-based autoscaling][knative helloworld rps]. The target RPS value of each pod needs to be adjusted based on the input event rate (event generation rate of generator). Details are described below.

Assuming the given event generation rate is 780 events/second. If we set the target RPS value of each pod as 78, we will then have 10 pod instance. If we set the target RPS value of each pod as 39, we will have 20 instance. **By adjusting the target RPS value, we can vary the number of instances.**

### How to run the experiment for **Kubernetes servivce - Config-1**
*NOTE 1: make sure you finish step I ~ VI to get the environment ready*
*NOTE 2: make sure you modify the MOSQUITTO IP before deploying the brokerchannel (MQTT-to-HTTP Adapter)*
1. Deploy required brokerchannel and service **Master node**
```
# Deploy brokerchannel for Kubernetes Service
kubectl apply -f ksvc_brokerchannel.yaml
# Deploy the helloworld-go service (Kubernetes Service)
kubectl apply -f ksvc_helloworld.yaml
```
2. Enable autoscaling policy **Master node**
```
kubectl autoscale deployment helloworld-go --cpu-percent=60 --min=1 --max=20
```
3. Generating events **Master node**
```
python3 generator.py -a $MOSQUITTO_IP -s $RATE_SCALE_DEGREE
```
4. Measure worker CPU usage **Worker node**
```
cpu_measure.sh $TIME
```
5. Collect printout on worker node **Worker node**

6. Cleaup if switching to other configs
```
kubectl delete -f knative_helloworld.yaml
kubectl delete -f knative_brokerchannel.yaml
```

### How to run the experiment for **Knative service - Config-3**
*NOTE 1: make sure you finish step I ~ VI to get the environment ready*
*NOTE 2: make sure you modify the MOSQUITTO IP before deploying the brokerchannel (MQTT-to-HTTP Adapter)*
1. Deploy required brokerchannel and service **Master node**
```
# Deploy brokerchannel for Knative Service
kubectl apply -f knative_brokerchannel.yaml
# Deploy the helloworld-go service (Knative Service)
kubectl apply -f knative_helloworld_autoscaling_rps.yaml
```
2. Generating events **Master node**
```
python3 generator.py -a $MOSQUITTO_IP -s $RATE_SCALE_DEGREE
```
3. Measure worker CPU usage **Worker node**
```
cpu_measure.sh $TIME
```
4. Collect printout on worker node **Worker node**

5. Cleaup if switching to other configs
```
kubectl delete -f knative_helloworld_autoscaling_rps.yaml
kubectl delete -f knative_brokerchannel.yaml
```

# Experiment steps in detail
## Experiment group 1
1. Start the experiment robot on the worker node
```
python3 exp_robot.py --addr $WORKER_IP --port 65432 --node worker
```
2. Configure the autoscaling parameters
number of instances: 1          5       10      15      20
RPS (200 e/s):       200        40      20      13      10
RPS (400 e/s):       400        80      40      26      20
RPS (800 e/s):       800        160     80      52      40
RPS (1600 e/s):      1600       320     160     104     80
RPS (3200 e/s):      3200       640     320     208     160
RPS (6400 e/s):      6400       1280    640     416     320
RPS (12800 e/s):     12800      2560    1280    832     640

3. Deploy the service and brokerchannel (NOTE: if keep using the same service, no need to deploy brokerchannel again)
```
kubectl apply -f knative_brokerchannel.yaml
kubectl apply -f knative_helloworld_autoscaling_rps.yaml
```
4. Start the experiment script on master node. Set the event generation rate at different levels (200, 400, 800, 1600, 3200, 6400, 12800 events/second)
```
python3 generator.py -a $MOSQUITTO_IP -s 256
python3 exp_robot.py --addr $WORKER_IP --port 65432 --time $TIME --node master
```
5. The results should be returned to master node. Collect the results.

[ksvc helloworld]: https://github.com/ShixiongQi/serverless-IoT-script/blob/master/nas21/knative_helloworld.yaml
[knative helloworld rps]: https://github.com/ShixiongQi/serverless-IoT-script/blob/master/nas21/knative_helloworld_autoscaling_rps.yaml
[cpu measure]: https://github.com/ShixiongQi/serverless-IoT-script/blob/master/nas21/experiments/cpu_measure.sh