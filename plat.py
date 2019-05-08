from kubernetes import client, config
import subprocess

class kube:

    def __init__(self):
          config.load_kube_config()
          self.extensions_v1beta1 = client.ExtensionsV1beta1Api()

    def get_deployment(self,service,namespace):
         deployments_list = self.extensions_v1beta1.list_namespaced_deployment(namespace)
         for deployment in deployments_list.items:
              if deployment.metadata.name == service.name:
                     return deployment
    
    def restart_services_deployment(self,service,namespace):
           subprocess.check_output(["kubectl get deployment "+service.name+" | tail -n +2 | awk '{print $4}'"], shell=True)

    def get_current_instance_count(self,service,namespace):
           return float(subprocess.check_output(["kubectl get deployment "+service.name+" | tail -n +2 | awk '{print $4}'"], shell=True))
         
    def allocate_mem(self,service,mem):
                   
           deployment = self.get_deployment(service,"default")
           deployment.spec.template.spec.containers[0].resources.limits['memory'] = mem
           api_response = self.extensions_v1beta1.patch_namespaced_deployment(
              name=service.name,
              namespace="default",
              body=deployment)

    def get_current_mem(self,service):

          deployment = get_deployment(service,"default")
          return deployment.spec.template.spec.containers[0].resources.limits['memory']

    def get_current_cpu(self,service):

          deployment = get_deployment(service,"default")
          return deployment.spec.template.spec.containers[0].resources.limits['memory']  

    def allocate_cpu(self,service,cpu):
           deployment = self.get_deployment(service,"default")
           deployment.spec.template.spec.containers[0].resources.limits['memory'] = mem
           api_response = self.extensions_v1beta1.patch_namespaced_deployment(
              name=service.name,
              namespace="default",
              body=deployment)
