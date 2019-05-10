import subprocess
def run_cmd(cmd,timeout):
     try:
       return subprocess.check_output([cmd], shell=True,timeout=timeout) 
     except Exception as e:
       print(e)
       return ""
