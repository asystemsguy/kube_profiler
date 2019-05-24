import unittest
from analysis import *
from cluster import *

class analysis_test(unittest.TestCase):
    def setUp(self):
        self.endpoints = list()
        self.endpoint_1 = endpoint("e1",None,None,None,None)
        self.endpoint_2 = endpoint("e2",None,None,None,None)
        self.endpoint_3 = endpoint("e3",None,None,None,None)
        self.endpoint_4 = endpoint("e4",None,None,None,None)
        self.endpoint_1.limits["cpu"] = 2
        self.endpoint_1.limits["mem"] = 4
        self.endpoint_2.limits["cpu"] = 2
        self.endpoint_2.limits["mem"] = 8
        self.endpoint_3.limits["cpu"] = 2
        self.endpoint_3.limits["mem"] = 8
        self.endpoint_4.limits["cpu"] = 2
        self.endpoint_4.limits["mem"] = 8
        self.endpoints.append(self.endpoint_1)
        self.endpoints.append(self.endpoint_2)       
        self.endpoints.append(self.endpoint_3)
        self.endpoints.append(self.endpoint_4)
        self.service = service("service1",None,None,self.endpoints,None)
        self.vm_types = list()
        self.vm_types.append(vm_type(2,16,30)) 
        self.vm_types.append(vm_type(4,16,60))
        self.vm_types.append(vm_type(4,32,80))
        
    def test_calculate_limits(self):
          analysis_test = analysis()
          limits = analysis_test.get_limits(self.service,"max_strategy")
          self.assertTrue(limits["cpu"] == 2)
          self.assertTrue(limits["mem"] == 8)
    
    def test_vm_type(self):
          analysis_test = analysis()
          limits = analysis_test.get_limits(self.service,"max_strategy")
          vm_type_t = analysis_test.get_vm_type([self.service],self.vm_types)
          self.assertTrue(vm_type_t.limits["cpu"] == 2 and vm_type_t.limits["mem"] == 16)
if __name__ == '__main__':
    unittest.main()

