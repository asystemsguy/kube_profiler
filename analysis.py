from cluster import service,endpoint


class Limits_Extraction:
    def max_strategy(self,resources): 
        self.limits["cpu"] = max(cpus)
        self.limits["mem"] = max(self.endpoints_mem)
        return self.limits

class analysis:
       def __init__(self):
           self.endpoints_cpu = []
           self.endpoints_mem = []
           self.limits = dict()
           self.limits["cpu"] = 0
           self.limits["mem"] = 0

    def __init__(self,resources):
         self.endpoint_resources =  dict()
         self.resources = resources
         self.limits["cpu"] = 0
         self.limits["mem"] = 0
         self.Limits_Extraction = Limits_Extraction()

    def get_limits(self,service,strategy):
        for endpoint in service.endpoints:
            for resource in resources:
                 self.endpoints_resources(endpoint.cpu_limits)
        service.limits =  getattr(self.Limits_Extraction,strategy)()
        return service.limits

    def get_vm_type(self,services,vm_types):
        # get the largest required resource
        for service in services:



