from scheduler import cluster
from cluster import service
from analysis import vm_type
import unittest

class cluster_test(unittest.TestCase):
    def setUp(self):
         self.services = list()
         self.services.append(service("s1",None,None,[None],None))
         self.services.append(service("s2",None,None,[None],None))
         self.services.append(service("s3",None,None,[None],None))
         self.services.append(service("s4",None,None,[None],None))

         self.services[0].limits["cpu"] = 2
         self.services[0].limits["mem"] = 190
         self.services[1].limits["mem"] = 20
         self.services[1].limits["cpu"] = 2
         self.services[2].limits["mem"] = 20
         self.services[2].limits["cpu"] = 2
         self.services[3].limits["mem"] = 20
         self.services[3].limits["cpu"] = 2

         self.vm_type = vm_type(200,200,20)

    def schedule(self):
         cluster_kube = cluster(self.vm_type)
         cluster_kube.schedule(self.services)
         return cluster_kube
    def test_are_all_services_scheduled(self):
         cluster_kube = self.schedule()
         # number of services should be same
         count  = 0
         for machine in cluster_kube.node_list:
               count = count + len(machine.services)
         self.assertTrue(count == len(self.services))

    def test_no_duplicates(self):
        cluster_kube = self.schedule()
        name_set = set()
        for machine in cluster_kube.node_list:
            for service in machine.services:
                 self.assertFalse(service.name in name_set)
                 name_set.add(service.name)

if __name__ == '__main__':
    unittest.main()
