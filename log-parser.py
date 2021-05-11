import os
import re
import csv
import json
import traceback
from datetime import datetime, timedelta
from collections import Counter
from collections import defaultdict



from config import config
from utils import exec_cmd


class LogLineGenerator:
    def __init__(self):
        self.format_string          = config.format_string
        self.format_mappings        = config.format_mappings
        self.log_dir                = config.logs_path
        self.output_json            = config.output_json
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
    print(now, last_x_mins)
    last_x_mins_data = [x for x in logs if x["date"] <= now and x["date"] >= last_x_mins]
    status_counter = Counter(x['status'] for x in last_x_mins_data)
    
    stats_dict = {}
    stats_dict["time"] = now
    stats_dict["500"] = status_counter["500"]
    stats_dict["501"] = status_counter["501"]
    stats_dict["502"] = status_counter["502"]
    stats_dict["503"] = status_counter["503"]
    stats_dict["400"] = status_counter["400"]
    stats_dict["404"] = status_counter["404"]
    stats_dict["403"] = status_counter["403"]

    rc,stdout,stderr = exec_cmd("hostname")
    if stdout:
        hostname = stdout.strip()
    json_dict = {}
    if os.path.isfile(log_generator.output_json):    
        with open(log_generator.output_json) as _file:
            json_dict = json.load(_file)
    if hostname not in json_dict:
        json_dict[hostname] = [stats_dict]
    else:
        json_dict[hostname].append(stats_dict)

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
        