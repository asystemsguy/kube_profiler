from cluster import service,endpoint

class vm_type:
    def __init__(self,cpu_cap,mem_cap,cost):
        self.limits = dict()
        self.limits["cpu"] = cpu_cap
        self.limits["mem"] = mem_cap
        self.costs = dict()
        self.costs["cpu"] = cpu_cap/cost
        self.costs["mem"] = mem_cap/cost

class Limits_Extraction:
    def max_strategy(self,resources):
        limits = dict()
        limits["cpu"] = max(resources["cpu"])
        limits["mem"] = max(resources["mem"])
        return limits

class analysis:

    def __init__(self):
         self.Limits_Extraction = Limits_Extraction()

    def get_limits(self,service,strategy):
        resources_dict =  dict()
        resources_dict["cpu"] = list()
        resources_dict["mem"] = list()
        for endpoint in service.endpoints:
            if "cpu" in endpoint.limits and "mem" in endpoint.limits:
               resources_dict["cpu"].append(endpoint.limits["cpu"])
               resources_dict["mem"].append(endpoint.limits["mem"])
        service.limits =  getattr(self.Limits_Extraction,strategy)(resources_dict)
        return service.limits

    def get_vm_type(self,services,vm_types):
        # get the largest required resource
        total_resources = dict()
        total_resources["cpu"] = 0
        total_resources["mem"] = 0

        # calculate total available resources
        for service in services:
             total_resources["cpu"] = total_resources["cpu"]+service.limits["cpu"]
             total_resources["mem"] = total_resources["mem"]+service.limits["mem"]

        # Find least costly VM type
        total_cost_dollers = 0
        least_cost_vm_type = vm_types[0]
        total_cost_dollers_least = 0
        for vm_type_t in vm_types:
             total_cost_dollers = total_resources["cpu"]*vm_type_t.costs["cpu"]
             total_cost_dollers = total_cost_dollers+total_resources["mem"]*vm_type_t.costs["mem"]
             if total_cost_dollers < total_cost_dollers_least:
                 total_cost_dollers_least = total_cost_dollers
                 least_cost_vm_type = vm_type_t
        return least_cost_vm_type


