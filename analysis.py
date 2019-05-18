from cluster import service,endpoint

class analysis:

    def __init__(self):
         self.endpoints_cpu = []
         self.endpoints_mem = []
         self.limits["cpu"] = 0
         self.limits["mem"] = 0

    def get_limits(self,service,strategy):
        for endpoint in service.endpoints:
             self.endpoints_cpu.append(endpoint.cpu_limits)
             self.endpoints_mem.append(endpont.mem_limits)
        return getattr(self,strategy)()

    def max_strategy(self): 
        self.limits["cpu"] = max(self.endpoints_cpu)
        self.limits["mem"] = max(self.endpoints_mem)
        return self.limits

