from rectpack import newPacker
from cluster import service
from analysis import vm_type


class machine:
    def __init__(self,resources):
         self.resources = resources
         self.services = list()

    def add_service(service):
         if self.alloc_resource("cpu",service.limits["cpu"]) != True
               return False
         if self.alloc_resource("mem",service.limits["mem"]) != True
               return False
         self.services.append(service)
         return True

    def alloc_resource(self,type_res,value):
        if self.resources[type_res] <= value:
              return False
        else:
            self.resources[type_res] = self.resources[type_res]-value
            return True
class cluster:
    def __init__(self,vm_type):
         self.machine_resources = dict()
         self.machine_resources["cpu"] = vm_type.limits["cpu"]
         self.machine_resources["mem"] = vm_type.limits["mem"]
         self.node_list = list()
         self.node_list[-1] = machine(self.machine_resources)
    def add_service(service):
         if self.node_list[-1].add_service(service) != True:
              self.node_list.append(machine(self.machine_resources))
              self.node_list[-1].add_service(service)

cluster_kube = cluster()
def schedule(services,vm_type):
     for service in services:
          cluster_kube.add_service(service)

