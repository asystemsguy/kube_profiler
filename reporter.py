import matplotlib.pyplot as plt
import numpy as np
import os
import time
import math

class reporter:
    def __init__(self,total_req):
          
          self.throughput_values = []
          self.latency_values = []
          self.errors=[]
          self.slos_dict = {}
          self.keys = []
          self.total_req = total_req
          self.create_folders()

    def create_folders(self):
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

    def process(self,endpoint,key,output):

          self.slos_dict[key] = self.extract_hey_output(output)  
          self.throughput_values.append(self.slos_dict[key][0])
          self.latency_values.append(self.slos_dict[key][1])
          self.keys.append(key)
          if '[200]' in self.slos_dict[key][2]:
              total_actual_reqs = math.floor(self.total_req/endpoint.max_conn_requests)*endpoint.max_conn_requests
              self.errors.append(total_actual_reqs-self.slos_dict[key][2]['[200]'][0])
          else:
              self.errors.append(self.total_req)

    def plot_data(self,filename):
        try:
            plt.plot(self.keys, self.throughput_values)
            plt.xlabel('number of concurrent requests')
            plt.ylabel('throughput (req/sec)')
            plt.savefig("output/graphs/graph_"+filename+"_t_"+time.strftime("%Y%m%d-%H%M%S")+'_throughput.pdf')
       
            plt.plot(self.keys, self.latency_values)
            plt.xlabel('number of concurrent requests')
            plt.ylabel('latency (secs)')
            plt.savefig("output/graphs/graph_"+filename+"_t_"+time.strftime("%Y%m%d-%H%M%S")+'_latency.pdf')

            plt.plot(self.keys, self.errors)
            plt.xlabel('number of concurrent requests')
            plt.ylabel('number of non-200 requests')
            plt.savefig("output/graphs/graph_"+filename+"_t_"+time.strftime("%Y%m%d-%H%M%S")+'_errors.pdf')
        except Exception as e:
            print(e)
        return True

    def dump_throughput_values(self,file):
        
          file.write("throughput_values:\n")
          for value,item in zip(self.keys,self.throughput_values):
              file.write("%s," % value)
              file.write("%s\n" % item)

   
    def dump_latency_values(self,file):
       
          file.write("latency_values:\n")
          for value,item in zip(self.keys,self.latency_values):
              file.write("%s," % value)
              file.write("%s\n" % item)

    def dump_errors(self,file):

          file.write("errors:\n")
          for value,item in zip(self.keys,self.errors):
              file.write("%s," % value)
              file.write("%s\n" % item)
        

    def dump_data(self,filename):
        try:
            filecompletename = 'output/data/data_'+filename+"_t_"+time.strftime("%Y%m%d-%H%M%S")+'.txt'
            with open(filecompletename, 'w+') as file:
              self.dump_throughput_values(file)
              self.dump_latency_values(file)
              self.dump_errors(file)
              print("results are in ",filecompletename)
        except Exception as e:
            print(e)

    # get the resource for target throughput and response time
    def get_value_for_target(self,target_through,target_resp):
          print(self.throughput_values,self.latency_values,self.errors,target_through,target_resp,self.keys)
          for index in range(0, len(self.throughput_values)):
                if self.throughput_values[index] >= target_through and self.latency_values[index] <= target_resp and self.errors[index]==0 :
                    print("index ",index)
                    return self.keys[index]
    
    # get maximum throughput that has no errors
    def get_maxthroughput(self):
             throughput_values = self.throughput_values
             errors = self.errors
             keys = self.keys
             while len(throughput_values) != 0 and errors[throughput_values.index(max(throughput_values))] < 10:
                    index = throughput_values.index(max(throughput_values))
                    throughput_values.remove(throughput_values[index])
                    errors.remove(errors[index])
                    keys.remove(keys[index])
             if len(throughput_values) != 0:     
                 return keys[throughput_values.index(max(throughput_values))]
             return 0 
