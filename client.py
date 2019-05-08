from profiler import profiler
import yaml

prof = profiler()


prof.load_config("testfiles/station.yaml")
prof.run()

