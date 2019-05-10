from kubernetes import client, config, watch
import json
import time

config.load_kube_config()
v1 = client.CoreV1Api()

nodename = ""
service_name = "ts-station-service"

for node in v1.list_node().items:
      if 'type' in node.metadata.labels:
              if node.metadata.labels['type'] == 'test':
                    nodename = node.metadata.name

body = client.V1Binding()

target = client.V1ObjectReference()
target.kind = "Node"
target.apiVersion = "v1"
target.name = nodename

meta = client.V1ObjectMeta()
meta.name = 

