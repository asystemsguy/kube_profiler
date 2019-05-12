import yaml
from plat import kube
from cluster import service,endpoint,service_data
from resource import max_conn_requests,cpu,memory

class profiler:
       def __init__(self):
             self.services = []
             self.resources = []
             self.total_req = 0
             self.timeout = 100000
             self.plat = kube()

       def run(self):
            for service in self.services:
                
                service.prepare_for_profiling()
                for resource in self.resources: 
                     resource.profile(service,self.total_req,self.timeout)

       def load_config(self,filename):

              with open(filename, 'r') as stream:
                try:
                    config = yaml.safe_load(stream)

                    self.total_req = config['total_req']
                    self.timeout = config['timeout']  
                    self.plat.timeout = self.timeout 

                    min_value = config['resources']['conn_reqs']['min']
                    max_value = config['resources']['conn_reqs']['max']
                    interval_value = config['resources']['conn_reqs']['interval']
                    self.resources.append(max_conn_requests(min_value,max_value,interval_value,self.plat))

                    min_value = config['resources']['cpu']['min']
                    max_value = config['resources']['cpu']['max']
                    interval_value = config['resources']['cpu']['interval']
                    self.resources.append(cpu(min_value,max_value,interval_value,self.plat))
                    
                    min_value = config['resources']['mem']['min']
                    max_value = config['resources']['mem']['max']
                    interval_value = config['resources']['mem']['interval']
                    self.resources.append(memory(min_value,max_value,interval_value,self.plat))

                  
                    for service_conf in config['services']:
                         
                         service_name = service_conf['service']['name']
                         port = service_conf['service']['port']
                         
                         schema = []
                         if 'data' in service_conf['service']:
                             schema = service_conf['service']['data'][0]['type']
                         endpoints = []
                         for endpoint_conf in service_conf['service']['endpoints']:
                             method = endpoint_conf['endpoint']['method']
                             endpoint_name = endpoint_conf['endpoint']['name']
                             print(endpoint_conf['endpoint'])
                             headers = endpoint_conf['endpoint']['header']
                             target_throughput = endpoint_conf['endpoint']['target_throughput']
                             print(endpoint_conf['endpoint'])
                             target_latency = endpoint_conf['endpoint']['target_latency']
                             endpoints.append(endpoint(endpoint_name,method,headers,target_throughput,target_latency))
                    
                         self.services.append(service(service_name,port,service_data(schema,self.total_req),endpoints,self.plat))
                
                except yaml.YAMLError as e:
                   print(e)


                 


