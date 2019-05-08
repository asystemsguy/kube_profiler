from profiler import profiler
import yaml

prof = profiler()

with open("testfiles/station.yaml", 'r') as stream:
    try:
        config = yaml.safe_load(stream)
        #total_req = config['num_req']
        for service_i in config:
             
             service = service_i['service']['name']
             port = service_i['service']['port']
             
             # generate 10000 json lines containing elements  
             schema = service_i['service']['data'][0]['type']
             for endpoint in service_i['service']['endpoints']:
                 method = endpoint['endpoint'][0]['method']
                 API = endpoint['endpoint'][1]['name']
                 headers_str = " -H '"+endpoint['endpoint'][2]['header']+"'"
                 target_throughput = endpoint['endpoint'][3]['target_throughput']
                 target_latency = endpoint['endpoint'][4]['target_latency']
                 max_throughput = prof.profile_max_throughput(headers_str,method,service,port,API,schema,10000)
#                 max_cpu = prof.profile_cpu(headers_str,method,service,port,API,schema,10000,max_throughput,target_throughput,target_latency)
#                 max_mem = prof.profile_mem(headers_str,method,service,port,API,schema,10000,max_throughput,target_throughput,target_latency,max_cpu)
#                 print("for service "+service+" and "+method+" max throughput ",max_throughput," CPU ",max_cpu," MEM ",max_mem)
    
    except yaml.YAMLError as exc:
        print(exc)




