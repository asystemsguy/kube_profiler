import os
import json
import time
import requests
import subprocess
from faker_schema.faker_schema import FakerSchema

class service:
      def __init__(self,name,port,data,endpoints,platform):
          self.name = name
          self.port = port
          self.data = data
          self.endpoints = endpoints
          self.platform = platform
          self.url = 'http://'+self.name+':'+str(self.port)
          for endpoint in endpoints:
            endpoint.service = self
          try:
            os.mkdir("fakedata")
          except FileExistsError as e:
             pass
          except Exception as e:
            print(e)


      def generate_fake_data(self,file_name):
            if not os.path.isfile("fakedata/"+file_name):
               self.data.generate_data("fakedata/"+file_name)

      def delete_fake_data(self):
            if os.path.isfile("fakedata"):
                  try:
                    os.rmdir("fakedata")
                  except FileExistsError as e:
                     pass
                  except Exception as e:
                    print(e)

      def wait(self):
            service_up = -1
            while(service_up != 1):                       
                  time.sleep(3)
                  service_up = self.platform.get_current_instance_count(self,"default")
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
                       print("service "+self.name+" responding with code "+str(status_code)+" trying again ...")
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

        def get_load_command(self,total_req,con_req,timeout,datafilename):

              loadgen_cmd = "hey -n "+str(total_req)+" -c "+str(con_req)+" -t "+str(timeout)+" -m "+self.method
                      
              if self.header != "":
                   loadgen_cmd = loadgen_cmd+" -H '"+self.header+"' -D fakedata/"+datafilename
                        
              loadgen_cmd = loadgen_cmd+" "+self.service.url+self.name 
              return loadgen_cmd

        def gen_load(self,total_req,con_req,timeout,datafilename):

             if self.header != "":
                 self.service.generate_fake_data(datafilename)

             loadgen_cmd = self.get_load_command(total_req,con_req,timeout,datafilename)

             return subprocess.check_output([loadgen_cmd], shell=True) 

        def get_sign(self):
              return "_api_"+self.name.replace("/", "_")+"_m_"+self.method

class service_data:
       def __init__(self,schema,total_req):
            self.schema = schema
            self.total_req = total_req

       def generate_data(self,file_name): 
             faker = FakerSchema()
             data = faker.generate_fake(self.schema, iterations=self.total_req)
             with open(file_name, 'w') as f:
                   for item in data:
                       json.dump(item,f)
                       f.write('\n') 