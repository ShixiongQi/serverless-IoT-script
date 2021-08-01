# NAS 21 paper experiment instructions
In this work, we...

We have three different experiment configurations:
1. The service instances are deployed as native Kubernetes services
2. The service instances are deployed as native Kubernetes serivces with eProxy equipped
3. The service instances are deployed as Knative services with queue proxy equipped

To deploy **CONFIG-1**, please use `ksvc_trigger.yaml` and `ksvc_helloworld.yaml`