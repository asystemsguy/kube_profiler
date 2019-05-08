import subprocess
import time
import os
import struct
import signal
import sys
import matplotlib.pyplot as plt
from tqdm import tqdm
from random import randint
import numpy as np
from os import path
import yaml
from kubernetes import client, config
import requests
from faker_schema.faker_schema import FakerSchema
import json

class profiler:
    def generate_data_from_schema(self,schema,file_name): 
             faker = FakerSchema()
             data = faker.generate_fake(schema, iterations=10000)
             with open(file_name, 'w') as f:
                   for item in data:
                       json.dump(item,f)
                       f.write('\n') 
    def allocate_cpu(self,service,cpus):

            config.load_kube_config()
            extensions_v1beta1 = client.ExtensionsV1beta1Api()

            deployments_list = extensions_v1beta1.list_namespaced_deployment("default")
            
            for deployment in deployments_list.items:
                if deployment.metadata.name == service:

                   print(deployment.spec.template.spec.containers[0].resources.limits)

                   deployment.spec.template.spec.containers[0].resources.limits['cpu'] = cpus
                   api_response = extensions_v1beta1.patch_namespaced_deployment(
                      name=service,
                      namespace="default",
                      body=deployment)
                deployments_list = extensions_v1beta1.list_namespaced_deployment("default")

            for deployment in deployments_list.items:
                if deployment.metadata.name == service:
                   print(deployment.spec.template.spec.containers[0].resources.limits)   


    def allocate_mem(self,service,mem):    
     
            config.load_kube_config()
            extensions_v1beta1 = client.ExtensionsV1beta1Api()

            deployments_list = extensions_v1beta1.list_namespaced_deployment("default")
            
            for deployment in deployments_list.items:
                if deployment.metadata.name == service:
                   print("existing memory limits ",deployment.spec.template.spec.containers[0].resources.limits['memory'])
                   deployment.spec.template.spec.containers[0].resources.limits['memory'] = mem
                   api_response = extensions_v1beta1.patch_namespaced_deployment(
                      name=service,
                      namespace="default",
                      body=deployment)
                deployments_list = extensions_v1beta1.list_namespaced_deployment("default")

            for deployment in deployments_list.items:
                if deployment.metadata.name == service:
                   print("new memory limits ",deployment.spec.template.spec.containers[0].resources.limits['memory'])     
       
    def extract_slo(self,output):
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

    def reporter(self,filename,throughput_values,latency_values,errors,values):
        try:
         with open('data/data_'+filename+'.txt', 'w') as f:
            f.write("throughput:\n")
            for value,item in zip(values,throughput_values):
                f.write("%s," % value)
                f.write("%s\n" % item)
            f.write("latency:\n")
            for value,item in zip(values,latency_values):
                f.write("%s," % value)
                f.write("%s\n" % item)
            f.write("errors:\n")
            for value,item in zip(values,errors):
                f.write("%s," % value)
                f.write("%s\n" % item)
            plt.plot(values, throughput_values)
            plt.xlabel('number of concurrent requests')
            plt.ylabel('throughput (req/sec)')
            plt.savefig("data/graph_"+filename+'_throughput.pdf')
       
            plt.plot(values, latency_values)
            plt.xlabel('number of concurrent requests')
            plt.ylabel('latency (secs)')
            plt.savefig("data/graph_"+filename+'_latency.pdf')

            plt.plot(values, errors)
            plt.xlabel('number of concurrent requests')
            plt.ylabel('number of non-200 requests')
            plt.savefig("data/graph_"+filename+'_errors.pdf')
        except Exception as e:
            print(e)
        return True
    def get_conn_req_max_throughput(self,throughput_values,errors,values):
         while len(throughput_values) != 0 and errors[throughput_values.index(max(throughput_values))] < 100:
                index = throughput_values.index(max(throughput_values))
                throughput_values.remove(throughput_values[index])
                errors.remove(errors[index])
                values.remove(values[index])
         if len(throughput_values) != 0:     
             return values[throughput_values.index(max(throughput_values))]
         return 0
    def get_res_for_target(self,throughput_values,errors,latency_values,values,target_through,target_resp):
          for index in range(0, len(throughput_values)):
                if throughput_values[index] >= target_through and latency_values[index] <= target_resp and errors[index]==0 :
                    return values[index]
                 
    def profile_max_throughput(self,headers_str,method,service,port,API,data,total_req):

        slos_dict = {}
        throughput_values = []
        latency_values = []
        errors = []
        
        num_requests=[10,30,50,70,100,200,300,400,500,600,700,800,1000,1100,1200,1300,1400,1500]

        # allocate the docker container maximum possible resources
        self.allocate_cpu(service,"2")
        time.sleep(5)
        self.allocate_mem(service,"16G")
        time.sleep(5)
       
        url = 'http://'+service+':'+str(port)
        while(float(subprocess.check_output(["kubectl get deployment ts-station-service | tail -n +2 | awk '{print $4}'"], shell=True)) != 1):
                time.sleep(3)
                print(float(subprocess.check_output(["kubectl get deployment ts-station-service | tail -n +2 | awk '{print $4}'"], shell=True)))
                status_code = 0
        status_code = 0
        sleep_time = 0
        while(status_code != 200):

                try:
                     status_code = requests.get(url+"/welcome",timeout=None).status_code
                except requests.exceptions.ConnectionError:
                     sleep_time = sleep_time+20
                     time.sleep(sleep_time)
                     print(status_code)

        # run the stress and simulated process co-located for different array sizes
        for con_req in tqdm(num_requests):        
                loadgen_cmd = "hey -n "+str(total_req)+" -c "+str(con_req)
                
                if headers_str != "":
                      
                    data_filename = 'datafake/throughput_'+str(con_req)+'txt'
                    if not os.path.isfile(data_filename):                
                        self.generate_data_from_schema(data,data_filename)
                    loadgen_cmd = loadgen_cmd+" "+headers_str+" -m "+method+" -D "+data_filename
                
                loadgen_cmd = loadgen_cmd+" "+url+API 
              
                print(loadgen_cmd) 
        
                #execute the load on the service
                output = subprocess.check_output([loadgen_cmd], shell=True)
                slos_dict[con_req] = self.extract_slo(output)
                throughput_values.append(slos_dict[con_req][0])
                latency_values.append(slos_dict[con_req][1])
                if '[200]' in slos_dict[con_req][2]:
                     errors.append(total_req-slos_dict[con_req][2]['[200]'][0])
                else:
                     break
                time.sleep(5)
     
        filename = service+"_api_"+API.replace("/", "_")+"_m_"+method+"_p_max_throughput"+"_t_"+time.strftime("%Y%m%d-%H%M%S")
        self.reporter(filename,throughput_values,latency_values,errors,num_requests)
        return self.get_conn_req_max_throughput(throughput_values,errors,num_requests)

    def profile_cpu(self,headers_str,method,service,port,API,data,total_req,con_req,target_through,target_resp):

        throughput_values = []
        latency_values = []
        errors=[]
        slos_dict = {}

        cpu_cores=[2,1.8,1.6,1.2,1,0.8,0.6,0.4,0.2]
        url = 'http://'+service+':'+str(port)

        
        loadgen_cmd = "hey -n "+str(total_req)+" -c "+str(con_req)
                
        if headers_str != "":
             loadgen_cmd = loadgen_cmd+" "+headers_str+" -m "+method+" -D data.txt"
                  
        loadgen_cmd = loadgen_cmd+" "+url+API 
        
        # run the stress and simulated process co-located for different array sizes
        for cpu_core in tqdm(cpu_cores):        
                print(loadgen_cmd)
                sleep_time = 10
                # now restart the service
                self.allocate_cpu(service,cpu_core)
                while(float(subprocess.check_output(["kubectl get deployment ts-station-service | tail -n +2 | awk '{print $4}'"], shell=True)) != 1):                       
                      time.sleep(3)
                      print(float(subprocess.check_output(["kubectl get deployment ts-station-service | tail -n +2 | awk '{print $4}'"], shell=True)))
                status_code = 0
                while(status_code != 200):
                      
                      try:
                          status_code = requests.get(url+"/welcome",timeout=None).status_code
                      except requests.exceptions.ConnectionError:
                           sleep_time = sleep_time+20
                           time.sleep(sleep_time)
                           print(status_code)
                #execute the load on the service
                output = subprocess.check_output([loadgen_cmd], shell=True)
                slos_dict[cpu_core] = self.extract_slo(output)  
                print(slos_dict[cpu_core])
                throughput_values.append(slos_dict[cpu_core][0])
                latency_values.append(slos_dict[cpu_core][1])
                if '[200]' in slos_dict[cpu_core][2]:
                    errors.append(total_req-slos_dict[cpu_core][2]['[200]'][0])
                else:
                    errors.append(total_req)
                time.sleep(5)
        
        filename = service+"_api_"+API.replace("/", "_")+"_m_"+method+"_p_cpu"+"_t_"+time.strftime("%Y%m%d-%H%M%S")
        self.reporter(filename,throughput_values,latency_values,errors,cpu_cores)
        return self.get_res_for_target(throughput_values,errors,latency_values,cpu_cores,target_through,target_resp)

    def profile_mem(self,headers_str,method,service,port,API,data,total_req,con_req,target_through,target_resp,max_cpu):

        throughput_values = []
        latency_values = []
        errors=[]
        slos_dict = {}

        self.allocate_cpu(service,max_cpu)
        time.sleep(10)

        url = 'http://'+service+':'+str(port)
        
         
        loadgen_cmd = "hey -n "+str(total_req)+" -c "+str(con_req)
                
        if headers_str != "":
              loadgen_cmd = loadgen_cmd+" "+headers_str+" -m "+method+" -D data.txt"
                  
        loadgen_cmd = loadgen_cmd+" "+url+API 
     
        mem_available = ["800Mi","900Mi","1000Mi","2000Mi","3000Mi","4000Mi","5000Mi","6000Mi"]

        # run the stress and simulated process co-located for different array sizes
        for mem in tqdm(mem_available):        
           
                time.sleep(5)
                # now restart the service
                self.allocate_mem(service,mem)
                time.sleep(5)
                sleep_time = 10
                while(float(subprocess.check_output(["kubectl get deployment ts-station-service | tail -n +2 | awk '{print $4}'"], shell=True)) != 1):
                      time.sleep(3)
                      print(float(subprocess.check_output(["kubectl get deployment ts-station-service | tail -n +2 | awk '{print $4}'"], shell=True)))
                status_code = 0
                while(status_code != 200):

                      try:
                          status_code = requests.get(url+"/welcome",timeout=None).status_code
                      except requests.exceptions.ConnectionError:
                           sleep_time = sleep_time+20
                           time.sleep(sleep_time)
                           print(status_code)
                #execute the load on the service
                output = subprocess.check_output([loadgen_cmd], shell=True)
                slos_dict[mem] = self.extract_slo(output)
                throughput_values.append(slos_dict[mem][0])
                latency_values.append(slos_dict[mem][1])
                if '[200]' in slos_dict[mem][2]:
                   errors.append(total_req-slos_dict[mem][2]['[200]'][0])
                else:
                   errors.append(total_req)
                print(slos_dict[mem])
                time.sleep(5)

        filename = service+"_api_"+API.replace("/", "_")+"_m_"+method+"_p_mem"+"_t_"+time.strftime("%Y%m%d-%H%M%S")
        self.reporter(filename,throughput_values,latency_values,errors,mem_available)
        return self.get_res_for_target(throughput_values,errors,latency_values,mem_available,target_through,target_resp)




