from kubernetes import client, config, watch
import time
import util
import json
   
config.load_kube_config()
extensions_v1beta1 = client.ExtensionsV1beta1Api()
v1=client.CoreV1Api()


test_node = ""
load_node = ""
service_exit = "ts-station-service"
service_entry = "ts-train-service"
nontestnode_list = []

def get_deployment(service,namespace="default"):
        deployments_list = extensions_v1beta1.list_namespaced_deployment(namespace)
        if deployments_list is None:
                return
        for deployment in deployments_list.items:
            if deployment.metadata.name == service:
                return deployment  

 

       
deployment_service_1 = get_deployment(service_exit)
deployment_service_2 = get_deployment(service_entry)

print(type(deployment_service_1.spec.template.spec.affinity.node_affinity.required_during_scheduling_ignored_during_execution.node_selector_terms[0].match_expressions[0]))
affinity.required_during_scheduling_ignored_during_execution.node_selector_terms[0].match_expressions.values = nontestnode_list
deployment_service_1.spec.template.spec.affinity.node_affinity.required_during_scheduling_ignored_during_execution.node_selector_terms[0].match_expressions[0].values = nontestnode_list

api_response = extensions_v1beta1.patch_namespaced_deployment(
                            name=service_exit,
                            namespace="default",
                            body=deployment_service_1)
deployment_service_1 = get_deployment(service_exit)
print(deployment_service_1.spec.template.spec.affinity)
