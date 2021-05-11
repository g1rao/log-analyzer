import os
from subprocess import Popen, PIPE


def exec_cmd(cmd):    
    print("Executing the command:", cmd)
    process = Popen(cmd, stdout=PIPE, shell=True)
    stdout, stderr = process.communicate()
    stdout = stdout.decode('utf-8') if stdout else None
    stderr = stderr.decode('utf-8') if stderr else None
    return process.returncode, stdout, stderr