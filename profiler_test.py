import unittest
from profiler import profiler

class profiler_test(unittest.TestCase):
    def setUp(self):
		self.prof = profiler()
    def test_success_case(self):
        filename = "test.txt"
        throughput_values = [1,2,3,4,5,6,7]
        latency_values = [1,2,3,4,5,6,7]
        errors = [1,2,3,4,5,6,7]
        values = [1,2,3,4,5,6,7]
        self.assertTrue(self.prof.reporter(filename,throughput_values,latency_values,errors,values))

    def test_latency_bad_data_case(self):
        filename = "test.txt"
        throughput_values = [1,2,3,4,5,6,7]
        latency_values = [3,4,5,6,7]
        errors = [1,2,3,4,5,6,7]
        values = [1,2,3,4,5,6,7]
        self.assertTrue(self.prof.reporter(filename,throughput_values,latency_values,errors,values))

    def test_value_bad_data_case(self):
        filename = "test.txt"
        throughput_values = [1,2,3,4,5,6,7]
        latency_values = [1,2,3,4,5,6,7]
        errors = [1,2,3,4,5,6,7]
        values = [3,4,5,6,7]
        self.assertTrue(self.prof.reporter(filename,throughput_values,latency_values,errors,values))
if __name__ == '__main__':
    unittest.main()
