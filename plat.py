from kubernetes import client, config, watch
import time
import util
import json
from cluster import service

class kube:

    def __init__(self):
          config.load_kube_config()
          self.extensions_v1beta1 = client.ExtensionsV1beta1Api()
          self.v1 = client.CoreV1Api()
          self.current_test_service = ""
    
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
           
           deployment.spec.template.spec.containers[0].resources.limits = dict([('memory',mem)])

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
                          deployment.spec.template.spec.containers[0].resources.limits = dict([('memory',mem)])
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

           deployment.spec.template.spec.containers[0].resources.limits = dict([('cpu',cpu)])

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
                          deployment.spec.template.spec.containers[0].resources.limits = dict([('cpu',cpu)])
                          if count > 5:
                              break
                          count = count + 1
                          time.sleep(5)
                 break

    def get_node_selector_obj(self,nodelist,service,namespace="default"):

            deployment = self.get_deployment(service,namespace)
            

            # add required tolerations
            toleration = client.models.v1_toleration.V1Toleration()
            toleration.effect = "NoSchedule"
            toleration.key = "dedicated"
            toleration.value = "test"
            toleration.operator = "Equal"

            # add required node affinities
            node_selector_terms  = client.models.v1_node_selector_term.V1NodeSelectorTerm()
            node_selector_terms.match_expressions = [client.models.v1_node_selector_requirement.V1NodeSelectorRequirement('kubernetes.io/hostname','In',[])] 
            required_during_scheduling_ignored_during_execution = client.models.v1_node_selector.V1NodeSelector([node_selector_terms])
            required_during_scheduling_ignored_during_execution.node_selector_terms = [node_selector_terms]
            affinity = client.models.v1_node_affinity.V1NodeAffinity()
            affinity.required_during_scheduling_ignored_during_execution = required_during_scheduling_ignored_during_execution

            # update the spec
            deployment.spec.template.spec.affinity = client.models.v1_affinity.V1Affinity()
            deployment.spec.template.spec.affinity.node_affinity = affinity
            deployment.spec.template.spec.affinity.node_affinity.required_during_scheduling_ignored_during_execution.node_selector_terms[0].match_expressions[0].key = 'kubernetes.io/hostname'
            deployment.spec.template.spec.affinity.node_affinity.required_during_scheduling_ignored_during_execution.node_selector_terms[0].match_expressions[0].operator = 'In'
            deployment.spec.template.spec.affinity.node_affinity.required_during_scheduling_ignored_during_execution.node_selector_terms[0].match_expressions[0].values = nodelist
            deployment.spec.template.spec.tolerations = [toleration]
            

            return deployment
    
    def assain_service_to_testVM(self,service,namespace="default"):

            self.remove_service_from_testVM(self.current_test_service)

            time.sleep(10)
            

            # get list of nodes that are not labeled test or load
            nontestnode_list = []
            
            for node in self.v1.list_node().items:
               if 'type' in node.metadata.labels:
                     if node.metadata.labels['type'] == 'test':
                           Test_node_name = node.metadata.name
               else:
                 nontestnode_list.append(node.metadata.name)

                   # Create node affinity object to send to K8 master
            print("Moving the node ",Test_node_name)

            deployment = self.get_node_selector_obj([Test_node_name],service)
           
            # Update the spec
            # Retry for 5 times if conflit exception happens due to quick change in resources
            count = 0
            while True:
                 try:
                         api_response = self.extensions_v1beta1.patch_namespaced_deployment(
                            name=service.name,
                            namespace=namespace,
                            body=deployment)
                 except Exception as e:
                          deployment = self.get_node_selector_obj([Test_node_name],service)
                          if deployment is None:
                              return
                          if count > 5:
                              break
                          count = count + 1
                          time.sleep(5)

                 break
            self.current_test_service = service


    def remove_service_from_testVM(self,service,namespace="default"):
            if self.current_test_service == "":
                return
            deployment = self.get_deployment(service,namespace)

            # get list of nodes that are not labeled test or load
            nontestnode_list = []
            
            for node in self.v1.list_node().items:
               if 'type' in node.metadata.labels:
                     if node.metadata.labels['type'] == 'test':
                           Test_node_name = node.metadata.name
               else:
                 nontestnode_list.append(node.metadata.name)
  
            print("Removing the service from ",Test_node_name)

            deployment = self.get_node_selector_obj(nontestnode_list,service)
            deployment.spec.template.spec.tolerations = []
            
            # Update the spec
            # Retry for 5 times if conflit exception happens due to quick change in resources
            count = 0
            while True:
                 try:
                         api_response = self.extensions_v1beta1.patch_namespaced_deployment(
                            name=service.name,
                            namespace=namespace,
                            body=deployment)
                 except Exception as e:
                          deployment = self.get_node_selector_obj(nontestnode_list,service)
                          deployment.spec.template.spec.tolerations = []
                          if deployment is None:
                              return
                          if count > 5:
                              break
                          count = count + 1
                          time.sleep(5)

                 break




