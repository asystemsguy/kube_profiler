import time
import subprocess
import numpy as np
from tqdm import tqdm
from reporter import reporter

class resource:
     def __init__(self,min_res,max_res,interval,platform):
        self.min = min_res
        self.max = max_res
        self.interval = interval
        self.platform = platform

     def profile(self,service,total_req,timeout):

              print("# profiling for "+self.__class__.__name__+"\n")
                  
              keys = np.arange(self.min, self.max, self.interval)

              print("## service: ",service.name,"\n")

              self.platform.restart(service)
              

              # Run profiling for each endpoint
              for endpoint in service.endpoints:
                    
                    endpoint.max_conn_requests = 5

                    print("### endpoint: ",endpoint.method," ",endpoint.name,"\n")

                    filename = service.get_sign()+endpoint.get_sign()+"_p_"+self.__class__.__name__

                    report = reporter(total_req)

                    timeout_t = time.time() + timeout  

                    self.allocate(endpoint,2)

                    # Run the load on the endpoint for each iteration
                    # an iteration can be a resource partition or a concurrent load depending on resource
                    for key in tqdm(keys):        
                                               
                            # allocate a resource in this iteration and restart the service                    
                            self.allocate(endpoint,key)
             
                            # generate load in the service
                            try: 
                               output = endpoint.gen_load(total_req,endpoint.max_conn_requests,timeout,self.__class__.__name__+str(key))
                            except Exception as e:
                               # Timeout due to overload on the server
                               # Restart the server
                               self.platform.restart(service)
                               # Dump the data for logging and future use
                               report.dump_data(filename)
                               # Max load reached stop running profling on this endpoint
                               break
                            # process the output from load
                            report.process(key,output)                         
                            
                            # Timeout may due to delay in startup of the service etc.
                            if time.time() > timeout_t:
                              # try higher CPU or memory allocation
                                continue
                            else:
                               time.sleep(2)
                    
                    # Dump the data fro logging and future use
                    report.dump_data(filename) 

                    # finish any required final processing
                    self.finally_do(endpoint,report)

              service.delete_fake_data()
                        
                        
     def allocate(self,service,value):
          pass

     def finally_do(self,endpoint,report):
          pass

class max_conn_requests(resource):
       def __init__(self,min_res,max_res,interval,platform):
             resource.__init__(self,min_res,max_res,interval,platform)

       def allocate(self,endpoint,value):
             endpoint.max_conn_requests = value

       def finally_do(self,endpoint,report):
             endpoint.max_conn_requests = report.get_maxthroughput()


class memory(resource):
       def __init__(self,min_res,max_res,interval,platform):
             resource.__init__(self,min_res,max_res,interval,platform)

       def allocate(self,endpoint,value):    
             self.platform.allocate_mem(endpoint.service,value)

       def finally_do(self,endpoint,report):
             required_memory = report.get_value_for_target(endpoint.target_throughput,endpoint.target_latency)


class cpu(resource):
    
       def __init__(self,min_res,max_res,interval,platform):
             resource.__init__(self,min_res,max_res,interval,platform)

       def allocate(self,endpoint,value):
             self.platform.allocate_cpu(endpoint.service,value)

       def finally_do(self,endpoint,report):
             required_cpu = report.get_value_for_target(endpoint.target_throughput,endpoint.target_latency)
