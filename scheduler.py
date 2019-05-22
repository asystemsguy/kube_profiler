from cluster import service
from analysis import vm_type


class machine:
    def __init__(self,resources):
         self.resources = resources
         self.services = list()

    def add_service(self,service):
         if self.alloc_resource("cpu",service.limits["cpu"]) != True:
               return False
         if self.alloc_resource("mem",service.limits["mem"]) != True:
               return False
         self.services.append(service)
         return True
    def alloc_resource(self,type_res,value):
        if self.resources[type_res] <= value:
              return False
        else:
            self.resources[type_res] = self.resources[type_res]-value
            return True
    def print_services(self):
        for service in self.services:
              print(service.name)
class cluster:
    def __init__(self,vm_type):
         self.machine_resources = dict()
         self.machine_resources = vm_type.limits.copy()
         self.node_list = list()
         self.current_machine = machine(self.machine_resources.copy())
         self.node_list.append(self.current_machine)
    def add_service(self,service):
         if self.current_machine.add_service(service) != True:
              self.current_machine = machine(self.machine_resources.copy())
              self.node_list.append(self.current_machine)
              if self.current_machine.add_service(service) != True:
                  print("scheduling ",service.name," not possable as it needs more resources than vm_type")
    def schedule(self,services):
         for service in services:
              self.add_service(service)
         for machine in self.node_list:
              machine.print_services()


