import os
import re
import csv
import json
import traceback
from glob import glob
from datetime import datetime, timedelta
from collections import Counter
from collections import defaultdict

from config import config
from utils import exec_cmd


class LogLineGenerator:
    def __init__(self):
        self.format_string          = config.format_string
        self.format_mappings        = config.format_mappings
        self.log_dir                = glob(config.logs_path)[0]
        self.output_json            = config.output_json
        self.error_codes            = config.error_codes
        self.log_file               = self.log_dir + os.sep + "access_log"
        self.fetch_interval         = config.fetch_interval
        self.re_square_bracket      = re.compile(r'(\[|\])')
        self.field_list             = []

        for directive in self.format_string.split():
            self.field_list.append(self.format_mappings[directive])

    def _quote_translator(self, file_name):
        for line in open(file_name):
            yield self.re_square_bracket.sub('"', line)

    def get_loglines(self):
        reader = csv.DictReader(self._quote_translator(self.log_file), fieldnames=self.field_list, delimiter=' ',skipinitialspace=True)
        return reader


def main():
    log_generator = LogLineGenerator()
    logs = list(log_generator.get_loglines())
    
    last_x_mins = (datetime.now() - timedelta(minutes=log_generator.fetch_interval)).strftime('%d/%b/%Y:%H:%M:%S +0000')
    now = datetime.now().strftime('%d/%b/%Y:%H:%M:%S +0000')
    print("Capturing logs between: %s - %s"%(now.split()[0],last_x_mins.split()[0]))
    print("Log-file:    %s"%(log_generator.log_file))
    print("Output-json-file:    %s"%(log_generator.output_json))

    last_x_mins_data = [x for x in logs if x["date"] <= now and x["date"] >= last_x_mins]
    status_counter = dict(Counter(x['status'] for x in last_x_mins_data if x['status'] in log_generator.error_codes))
    # Counter({200:1, time: now,})
    for code in log_generator.error_codes:
        if code not in status_counter:
            status_counter[code] = 0
    status_counter["time"] = now

    rc,stdout,stderr = exec_cmd("hostname")
    if stdout:
        hostname = stdout.strip()
    json_dict = {}
    if os.path.isfile(log_generator.output_json):    
        with open(log_generator.output_json) as _file:
            json_dict = json.load(_file)
    if hostname not in json_dict:
        json_dict[hostname] = [status_counter]
    else:
        json_dict[hostname].append(status_counter)

    json_object = json.dumps(json_dict, indent = 4)  
    with open(log_generator.output_json, "w+") as _file:
        _file.write(json_object)

    # sorted_date = sorted(log_generator, key=lambda x: datetime.strptime(x['date'], '%d/%b/%Y:%H:%M:%S +0000'), reverse=True)

if __name__ == '__main__':
    try:
        main()
    except Exception:
        exstr = traceback.format_exc()
        print(exstr)    
