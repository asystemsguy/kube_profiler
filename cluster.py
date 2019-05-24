import os
import json
import time
import requests
import shutil
from faker_schema.faker_schema import FakerSchema
from faker import Faker
import util

class service:
      def __init__(self,name,port,data,endpoints,platform):
          self.name = name
          self.port = port
          self.data = data
          self.endpoints = endpoints
          self.platform = platform
          self.url = 'http://'+self.name+':'+str(self.port)
          self.limits =  dict()
          for endpoint in endpoints:
            endpoint.service = self
          try:
            shutil.rmtree("fakedata")
            os.mkdir("fakedata")
          except FileExistsError as e:
             pass
          except Exception as e:
            print(e)

      def prepare_for_profiling(self):
          self.platform.assain_service_to_testVM(self)

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

      def wait(self,timeout):
            service_up = -1
            time_start = time.time()
            while(service_up != 1):                       
                  if time.time() > time_start+timeout :
                       return False
                  time.sleep(3)
                  service_up = self.platform.get_instance_count(self,"default")
                  # if(service_up == 0.0):
                  #     print("number of available instances of "+self.name+" :"+str(service_up))

            sleep_time = 1
            status_code = 0
            time_start = time.time()
            while(status_code != 200):      
                  try:
                      status_code = requests.get(self.url+"/welcome",timeout=timeout).status_code
                  except requests.exceptions.ConnectionError:
                       if time.time() > time_start+timeout :
                               return False
                       sleep_time = sleep_time+2
                       # print("service "+self.name+" responding with code "+str(status_code)+" trying again ... after "+str(sleep_time)+" secs")
                       time.sleep(sleep_time)
            return True

      def get_sign(self):
             return "sev_"+self.name
                 
class endpoint:
        def __init__(self,name,method,headers,target_throughput,target_latency):
            self.name = name
            self.method = method
            self.headers = headers
            self.target_throughput = target_throughput
            self.target_latency = target_latency
            self.max_conn_requests = 0
            self.limits = dict() 

        def get_load_command(self,total_req,con_req,timeout,datafilename):

              loadgen_cmd = "hey -n "+str(total_req)+" -c "+str(con_req)+" -t "+str(timeout)+" -m "+self.method
                      
              if len(self.headers) > 0:
                  for header in self.headers:
                      loadgen_cmd = loadgen_cmd+" -H '"+header+"'"

              if 'Content-Type: application/json' in self.headers: 
                   loadgen_cmd = loadgen_cmd+" -D fakedata/"+datafilename

              loadgen_cmd = loadgen_cmd+" "+self.service.url+self.name 
              # print(loadgen_cmd)
              return loadgen_cmd

        def gen_load(self,total_req,con_req,timeout,datafilename):
              print("in gen_load for endpoint ",self.name)
              if 'Content-Type: application/json' in self.headers:
                 self.service.generate_fake_data(datafilename)

              # wait for the service to come up
              if self.service.wait(timeout):
                   return util.run_cmd(self.get_load_command(total_req,con_req,timeout,datafilename),timeout)
              else:
                   return ""
        def get_sign(self):
              return "_api_"+self.name.replace("/", "_")+"_m_"+self.method

class service_data:
     def __init__(self,schema,total_req):
            self.schema = schema
            self.total_req = total_req
            self._faker = Faker()

     def generate_data(self,file_name):
             faker = FakerSchema()
             data = self.generate_fake(self.schema, iterations=self.total_req)
             with open(file_name, 'w') as f:
                   for item in data:
                       json.dump(item,f)
                       f.write('\n') 
                       
     def generate_fake(self, schema, iterations=1):
        result = [self._generate_one_fake(schema) for _ in range(iterations)]
        return result[0] if len(result) == 1 else result
     
     def _generate_one_fake(self, schema):
        """
        Recursively traverse schema dictionary and for each "leaf node", evaluate the fake
        value

        Implementation:
        For each key-value pair:
        1) If value is not an iterable (i.e. dict or list), evaluate the fake data (base case)
        2) If value is a dictionary, recurse
        3) If value is a list, iteratively recurse over each item
        """
        data = {}
        for k, v in schema.items():
          if isinstance(v, dict):
            data[k] = self._generate_one_fake(v)
          elif isinstance(v, list):
            data[k] = [self._generate_one_fake(item) for item in v]
          else:  
            args = v.split(',')
            temp =''
            for arg in args:
                if hasattr(self._faker, arg): 
                    temp = temp+str(getattr(self._faker, arg)())
                else:
                    temp = temp+arg
            data[k] = temp
        return data
