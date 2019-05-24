import unittest
from reporter import *

class reporter_test(unittest.TestCase):
    def setUp(self):
         self.report = reporter(1000)  
    def test_calculate_limits(self):
         self.report.throughput_values = [138.155,529.7939,606.8245,630.1807,710.1668]
         self.report.errors = [0.0,0.0,0.0,0.0]
         self.report.latency_values = [0.0074,0.0816,0.1133,0.1522,0.1757]
         self.report.keys = [1,21,41,61,81]
         self.assertTrue(self.report.get_value_for_target(5,0.5) == 1)
         self.assertTrue(self.report.get_value_for_target(150,0.5) == 21)

if __name__ == '__main__':
    unittest.main()
