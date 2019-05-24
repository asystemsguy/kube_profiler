from profiler import profiler
import yaml

prof = profiler()
prof.load_config("testfiles/profile.yaml")
prof.run()

