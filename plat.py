from kubernetes import client, config, watch
import time
import util
import json

class kube:

    def __init__(self):
          config.load_kube_config()
          self.extensions_v1beta1 = client.ExtensionsV1beta1Api()
    
    def is_machine_up(self,machine):
           for n in v1.list_node().items:
    def get_deployment(self,service,namespace="default"):
         deployments_list = self.extensions_v1beta1.list_namespaced_deployment(namespace)
         if deployments_list is None:
             return
         for deployment in deployments_list.items:
              if deployment.metadata.name == service.name:
                     return deployment   
    def restart(self,service,namespace="default"):
           util.run_cmd("kubectl scale --replicas=0 deployment/"+service.name,self.timeout)
           util.run_cmd("kubectl scale --replicas=1 deployment/"+service.name,self.timeout)

    def get_instance_count(self,service,namespace="default"):
           output = util.run_cmd("kubectl get deployment "+service.name+" | tail -n +2 | awk '{print $4}'",self.timeout)
           if output != "":
               return float(output)
           return 0

    def get_current_mem(self,service,namespace="default"):

          deployment = get_deployment(service,namespace)
          if deployment is not None:
              return deployment.spec.template.spec.containers[0].resources.limits['memory']
         

    def allocate_mem(self,service,mem,namespace="default"):
           deployment = self.get_deployment(service,namespace)
           if deployment is None:
               return
           deployment.spec.template.spec.containers[0].resources.limits['memory'] = mem

           # Retry for 5 times if conflit exception happens due to quick change in resources
           count = 0
           while True:
                 try:
                         api_response = self.extensions_v1beta1.patch_namespaced_deployment(
                            name=service.name,
                            namespace=namespace,
                            body=deployment)
                 except Exception as e:
                          deployment = self.get_deployment(service,namespace)
                          if deployment is None:
                              return
                          deployment.spec.template.spec.containers[0].resources.limits['memory'] = mem
                          if count > 5:
                              break
                          count = count + 1
                          time.sleep(5)
                 break

    def get_current_cpu(self,service,namespace="default"):

          deployment = get_deployment(service,namespace)
          if deployment is not None:
              return deployment.spec.template.spec.containers[0].resources.limits['cpu']  

    def allocate_cpu(self,service,cpu,namespace="default"):

           deployment = self.get_deployment(service,namespace)
           if deployment is None:
              return 
           deployment.spec.template.spec.containers[0].resources.limits['cpu'] = cpu

           # Retry for 5 times if conflit exception happens due to quick change in resources
           count = 0
           while True:
                 try:
                         api_response = self.extensions_v1beta1.patch_namespaced_deployment(
                            name=service.name,
                            namespace=namespace,
                            body=deployment)
                 except Exception as e:
                          deployment = self.get_deployment(service,namespace)
                          if deployment is None:
                              return
                          deployment.spec.template.spec.containers[0].resources.limits['cpu'] = cpu
                          if count > 5:
                              break
                          count = count + 1
                          time.sleep(5)
                 break

    def move_service_to_machine(self,service,machine,namespace="default"):
         
         # Reduce number of replicas to 1 for deployment service.name
	 # Find the pod name for the deployment in service.name
         # Check if the machine is available
         # Bind the pod with the machine
         # return 
  



