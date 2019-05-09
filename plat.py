from kubernetes import client, config
import subprocess

class kube:

    def __init__(self):
          config.load_kube_config()
          self.extensions_v1beta1 = client.ExtensionsV1beta1Api()

    def get_deployment(self,service,namespace="default"):
         deployments_list = self.extensions_v1beta1.list_namespaced_deployment(namespace)
         for deployment in deployments_list.items:
              if deployment.metadata.name == service.name:
                     return deployment   
    def restart(self,service,namespace="default"):
           subprocess.check_output(["kubectl scale --replicas=0 deployment/"+service.name], shell=True)
           subprocess.check_output(["kubectl scale --replicas=1 deployment/"+service.name], shell=True)

    def get_instance_count(self,service,namespace="default"):
           return float(subprocess.check_output(["kubectl get deployment "+service.name+" | tail -n +2 | awk '{print $4}'"], shell=True))

    def get_current_mem(self,service,namespace="default"):

          deployment = get_deployment(service,namespace)
          return deployment.spec.template.spec.containers[0].resources.limits['memory']
         
    def update_deployment(self,deployment,service,namespace="default"):
          count  = 0 
          while True:
                 try:
                   api_response = self.extensions_v1beta1.patch_namespaced_deployment(
                      name=service.name,
                      namespace=namespace,
                      body=deployment)
                 except Exception as e:
                      print(e)
                      if count < 5:
                          count = count+1
                          continue
                 break

    def allocate_mem(self,service,mem,namespace="default"):
           service.wait()
           deployment = self.get_deployment(service,namespace)
           deployment.spec.template.spec.containers[0].resources.limits['memory'] = mem
           self.update_deployment(deployment,service,deployment)

    def get_current_cpu(self,service,namespace="default"):

          deployment = get_deployment(service,namespace)
          return deployment.spec.template.spec.containers[0].resources.limits['cpu']  

    def allocate_cpu(self,service,cpu,namespace="default"):
           service.wait()
           deployment = self.get_deployment(service,namespace)
           deployment.spec.template.spec.containers[0].resources.limits['cpu'] = cpu
           self.update_deployment(deployment,service,deployment)


