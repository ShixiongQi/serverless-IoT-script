# NAS 21 paper experiment instructions
In this work, we...

We have three different experiment configurations:
1. The service instances are deployed as native Kubernetes services

Generator.py --> MQTT broker (mosquitto) -> brokerchannel -> Kubernetes service

2. The service instances are deployed as native Kubernetes serivces with eProxy equipped

Generator.py --> MQTT broker (mosquitto) --> brokerchannel --> eProxy  --> Kubernetes service

3. The service instances are deployed as Knative services with queue proxy equipped

Generator.py --> MQTT broker (mosquitto) --> brokerchannel --> Queue proxy  --> Knative service

To deploy **CONFIG-1** and **CONFIG-2**, please use `ksvc_brokerchannel.yaml` and `ksvc_helloworld.yaml`

To deploy **CONFIG-1** and **CONFIG-2**, please use `knative_brokerchannel.yaml` and `knative_helloworld.yaml`