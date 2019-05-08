import subprocess
import time
import os
import struct
import signal
import sys
import json
import requests
import yaml
import matplotlib.pyplot as plt
import numpy as np
from kubernetes import client, config
from faker_schema.faker_schema import FakerSchema
from os import path
from tqdm import tqdm
from random import randint

class kubernetes:

    def __init__(self):
          config.load_kube_config()
          self.extensions_v1beta1 = client.ExtensionsV1beta1Api()

    def get_deployment(self,service,namespace):
         deployments_list = self.extensions_v1beta1.list_namespaced_deployment(namespace)
         for deployment in deployments_list.items:
              if deployment.metadata.name == service.name:
                     return deployment


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

class resource:
     def __init__(self,min_res,max_res,interval,platform):
        self.min = min_res
        self.max = max_res
        self.interval = interval
        self.platform = platform
     def profile(self):
        print("profling is not implemented for this resource")

     def allocate(self):
        print("allocate resource is not implemented for this resource")

class max_conn_requests(resource):
       def __init__(self,min_res,max_res,interval,platform):
           resource.__init__(self,min_res,max_res,interval,platform)

       def profile(self,service,total_req):
              print("# profiling for max concurrent requests\n")
              keys= range(self.min,self.max,self.interval)
              limits = []

              print("## service: ",service.name,"\n")
              for endpoint in service.endpoints:
                    print("### endpoint: ",endpoint.name,"\n")
                    report = reporter(total_req)
                    # run the stress and simulated process co-located for different array sizes
                    for key in tqdm(keys):        
                            
                            service.generate_data(self.__class__.__name__+str(key))
                            loadgen_cmd = endpoint.get_load_command(total_req,key,self.__class__.__name__+str(key))

                            # wait for the service to come up
                            service.wait()

                            #execute the load on the service
                            output = subprocess.check_output([loadgen_cmd], shell=True) 
                            report.process(key,output)                         
                            time.sleep(5)
                    
                    filename = service.get_sign()+endpoint.get_sign()+"_p_"+self.__class__.__name__+"_t_"+time.strftime("%Y%m%d-%H%M%S")
                    endpoint.max_conn_requests = report.get_value_for_maxthroughput()
                    report.dump_data(filename) 
                    #limits.append(reporter.get_value_for_target(keys,target_through,target_resp))
            #   return limits

class memory(resource):
       def __init__(self,min_res,max_res,interval,platform):
           resource.__init__(self,min_res,max_res,interval,platform)

       def allocate(self,service,value):    
     
             platform.allocate_mem(service,value)

       def profile(self,service,total_req):
              print("profiling for memory limit\n")
              keys= range(self.min,self.max,self.interval)
              limits = []

              for endpoint in service.endpoints:

                    report = reporter(total_req)
                    # run the stress and simulated process co-located for different array sizes
                    for key in tqdm(keys):        
                            
                            service.generate_data(self.__class__.__name__+str(key))
                            loadgen_cmd = endpoint.get_load_command(total_req,endpoint.max_conn_requests,self.__class__.__name__+str(key))
                            
                            # now restart the service
                            self.allocate(service,key)

                            # wait for the service to come up
                            service.wait()

                            #execute the load on the service
                            output = subprocess.check_output([loadgen_cmd], shell=True) 
                            report.process(key,output)                         
                            time.sleep(5)
                    
                    filename = service.get_sign()+endpoint.get_sign()+"_p_"+self.__class__.__name__+"_t_"+time.strftime("%Y%m%d-%H%M%S")
                    report.dump_data(filename) 
                    limits.append(report.get_value_for_target(keys,target_through,target_resp))

              #  return limits

class cpu(resource):
    
        def __init__(self,min_res,max_res,interval,platform):
            resource.__init__(self,min_res,max_res,interval,platform)

        def allocate(self,service,value):

             platform.allocate_cpu(service,value)

        def profile(self,service,total_req):
              print("profiling for cpu limit\n")
              keys= range(self.min,self.max,self.interval)
              limits = []

              for endpoint in service.endpoints:

                    report = reporter(total_req)
                    # run the stress and simulated process co-located for different array sizes
                    for key in tqdm(keys):        
                            
                            service.generate_data(self.__class__.__name__+str(key))
                            loadgen_cmd = endpoint.get_load_command(total_req,endpoint.max_conn_requests,self.__class__.__name__+str(key))
                            
                            # now restart the service
                            self.allocate(service,key)

                            # wait for the service to come up
                            service.wait()

                            #execute the load on the service
                            output = subprocess.check_output([loadgen_cmd], shell=True) 
                            report.process(key,output)                         
                            time.sleep(5)
                    
                    filename = service.get_sign()+endpoint.get_sign()+"_p_"+self.__class__.__name__+"_t_"+time.strftime("%Y%m%d-%H%M%S")
                    report.dump_data(filename) 
                    limits.append(report.get_value_for_target(keys,target_through,target_resp))

             #   return limits

class profiler:
       def __init__(self):
             self.services = []
             self.resources = []
             self.total_req = 0
             self.platform = kubernetes()

       def run(self):
            for service in self.services:
              for resource in self.resources:
                    resource.profile(service,self.total_req)

       def load_config(self,filename):

              with open(filename, 'r') as stream:
                try:
                    config = yaml.safe_load(stream)

                    self.total_req = config['total_req']
                      
                    min_value = config['resources']['conn_reqs']['min']
                    max_value = config['resources']['conn_reqs']['max']
                    interval_value = config['resources']['conn_reqs']['interval']
                    self.resources.append(max_conn_requests(min_value,max_value,interval_value,self.platform))

                    min_value = config['resources']['cpu']['min']
                    max_value = config['resources']['cpu']['max']
                    interval_value = config['resources']['cpu']['interval']
                    self.resources.append(cpu(min_value,max_value,interval_value,self.platform))
                    
                    min_value = config['resources']['mem']['min']
                    max_value = config['resources']['mem']['max']
                    interval_value = config['resources']['mem']['interval']
                    self.resources.append(memory(min_value,max_value,interval_value,self.platform))

                  
                    for service_conf in config['services']:
                         
                         service_name = service_conf['service']['name']
                         port = service_conf['service']['port']
                         schema = service_conf['service']['data'][0]['type']

                         endpoints = []
                         for endpoint_conf in service_conf['service']['endpoints']:
                             method = endpoint_conf['endpoint'][0]['method']
                             endpoint_name = endpoint_conf['endpoint'][1]['name']
                             headers = endpoint_conf['endpoint'][2]['header']
                             target_throughput = endpoint_conf['endpoint'][3]['target_throughput']
                             target_latency = endpoint_conf['endpoint'][4]['target_latency']
                             endpoints.append(endpoint(endpoint_name,method,headers,target_throughput,target_latency))
                    
                         self.services.append(service(service_name,port,service_data(schema),endpoints))
                except yaml.YAMLError as exc:
                   print(exc)

class service:
      def __init__(self,name,port,data,endpoints):
          self.name = name
          self.port = port
          self.data = data
          self.endpoints = endpoints
          self.url = 'http://'+self.name+':'+str(self.port)
          for endpoint in endpoints:
            endpoint.service = self
          try:
            os.mkdir("fakedata")
          except Exception as e:
            print(e)

      def generate_data(self,file_name):
            if not os.path.isfile("fakedata/"+file_name):
               self.data.generate_data("fakedata/"+file_name)

      def wait(self):
            service_up = -1
            while(service_up != 1):                       
                  time.sleep(3)
                  service_up = float(subprocess.check_output(["kubectl get deployment "+self.name+" | tail -n +2 | awk '{print $4}'"], shell=True))
                  if(service_up == 0.0):
                      print("number of available instances of "+self.name+" :"+str(service_up))

            sleep_time = 10
            status_code = 0
            while(status_code != 200):      
                  try:
                      status_code = requests.get(self.url+"/welcome",timeout=None).status_code
                  except requests.exceptions.ConnectionError:
                       sleep_time = sleep_time+20
                       time.sleep(sleep_time)
                       print("service "+self.name+" responding with code "+status_code+" trying again ...")
      def get_sign(self):
             return "sev_"+self.name
                 
class endpoint:
        def __init__(self,name,method,header,target_throughput,target_latency):
            self.name = name
            self.method = method
            self.header = header
            self.target_throughput = target_throughput
            self.target_latency = target_latency
            self.max_conn_requests = 0

        def get_load_command(self,total_req,con_req,datafilename):

              loadgen_cmd = "hey -n "+str(total_req)+" -c "+str(con_req)
                      
              if self.header != "":
                   loadgen_cmd = loadgen_cmd+" -H '"+self.header+"' -m "+self.method+" -D "+datafilename
                        
              loadgen_cmd = loadgen_cmd+" "+self.service.url+self.name 
              return loadgen_cmd

        def get_sign(self):
              return "_api_"+self.name.replace("/", "_")+"_m_"+self.method

class service_data:
       def __init__(self,schema):
            self.schema = schema

       def generate_data(self,file_name): 
             faker = FakerSchema()
             data = faker.generate_fake(self.schema, iterations=10000)
             with open(file_name, 'w') as f:
                   for item in data:
                       json.dump(item,f)
                       f.write('\n') 
                 
class reporter:
    def __init__(self,total_req):
          self.throughput_values = []
          self.latency_values = []
          self.errors=[]
          self.slos_dict = {}
          self.keys = []
          self.total_req = total_req
          try:
            os.mkdir("output")
            os.mkdir("output/data")
            os.mkdir("output/graphs")
          except FileExistsError as e:
             pass
          except Exception as e:
            print(e)

    def extract_hey_output(self,output):       
        output_str = output.decode("utf-8") 
        responses = {}
        throughput = 0.0
        latency = 0.0
        for item in output_str.split("\n"):
            if "Requests/sec:" in item:
                throughput = float(item.split("Requests/sec:",1)[1])
            if "90% in" in item:
                latency = float(item.split("90% in",1)[1].split("secs",1)[0])
            if "responses" in item:
                responses.setdefault(item.split()[0], []).append(float(item.split()[1]))
        return [throughput,latency,responses]

    def process(self,key,output):

          self.slos_dict[key] = self.extract_hey_output(output)  
          self.throughput_values.append(self.slos_dict[key][0])
          self.latency_values.append(self.slos_dict[key][1])
          self.keys.append(key)
          if '[200]' in self.slos_dict[key][2]:
              self.errors.append(self.total_req-self.slos_dict[key][2]['[200]'][0])
          else:
              self.errors.append(self.total_req)

    def plot_data(self,filename):
        try:
            plt.plot(self.keys, self.throughput_values)
            plt.xlabel('number of concurrent requests')
            plt.ylabel('throughput (req/sec)')
            plt.savefig("output/graphs/graph_"+filename+'_throughput.pdf')
       
            plt.plot(self.keys, self.latency_values)
            plt.xlabel('number of concurrent requests')
            plt.ylabel('latency (secs)')
            plt.savefig("output/graphs/graph_"+filename+'_latency.pdf')

            plt.plot(self.keys, self.errors)
            plt.xlabel('number of concurrent requests')
            plt.ylabel('number of non-200 requests')
            plt.savefig("output/graphs/graph_"+filename+'_errors.pdf')
        except Exception as e:
            print(e)
        return True

    def dump_data(self,filename):
        try:
         with open('output/data/data_'+filename+'.txt', 'w') as f:
            f.write("throughput:\n")
            for value,item in zip(self.keys,self.throughput_values):
                f.write("%s," % value)
                f.write("%s\n" % item)
            f.write("latency:\n")
            for value,item in zip(self.keys,self.latency_values):
                f.write("%s," % value)
                f.write("%s\n" % item)
            f.write("errors:\n")
            for value,item in zip(self.keys,self.errors):
                f.write("%s," % value)
                f.write("%s\n" % item)           
        except Exception as e:
            print(e)
        return True


    def get_value_for_target(self,target_through,target_resp):
          for index in range(0, len(throughput_values)):
                if throughput_values[index] >= target_through and latency_values[index] <= target_resp and errors[index]==0 :
                    return keys[index]
    
    def get_value_for_maxthroughput(self):
             throughput_values = self.throughput_values
             errors = self.errors
             keys = self.keys
             while len(throughput_values) != 0 and errors[throughput_values.index(max(throughput_values))] < 100:
                    index = throughput_values.index(max(throughput_values))
                    throughput_values.remove(throughput_values[index])
                    errors.remove(errors[index])
                    keys.remove(keys[index])
             if len(throughput_values) != 0:     
                 return keys[throughput_values.index(max(throughput_values))]
             return 0   
   

