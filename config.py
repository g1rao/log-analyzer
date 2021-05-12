import csv
import re
import os
import configparser


class Config:
    """ Read configuration from the parser.ini file"""

    def __init__(self, config_file):
        all_config = configparser.RawConfigParser()
        with open(config_file) as cfg_file:
            all_config.read_file(cfg_file)

        self.format_string = all_config.get('format', 'log-format')
        self.methods = all_config.get('methods', 'request-methods')
        self.logs_path = all_config.get('logs', 'logs-path')
        self.fetch_interval = int(all_config.get('time-interval', 'fetch-interval'))
        self.output_json = all_config.get('output', 'output-json')
        self.error_codes = all_config.get('http-codes', 'error-codes').split()
        self.format_mappings = {
                                "%h": "host",                
                                "%l": "identd",              
                                "%u": "user",                
                                "%t": "date",                
                                "%r": "request",             
                                "%>s": "status",              
                                "%b": "bytes",               
                                "%D": "response-time",       
                                "%{User-agent}i": "user-agent",          
                                "%{X-UserId}i": "userid",       
                                "%{X-IdentityDomain}i": "oralce-identitydomain",
                                "%{ECID-Context}i": "ecid-context",        
                                "%{X-RealUserId}i": "realuserid",   
                                "%{X-CustomerZone}i": "customerzone", 
                                "%{X-HTTP-Method-Override}i": "http-method-override",
                                "%{X-DMS-ECID}o": "dms-ecid"     
                                }

config = Config('parser.ini')
