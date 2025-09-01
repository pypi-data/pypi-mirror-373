from collections import OrderedDict
import json as json
import yaml as yaml
import argparse

class noflow_list(list):
    pass

def noflow_list_rep(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=False)

class flow_list(list):
    pass

def flow_list_rep(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data, flow_style=True)

yaml.add_representer(noflow_list, noflow_list_rep)
yaml.add_representer(flow_list, flow_list_rep)

represent_dict_order = lambda self, data:  self.represent_mapping('tag:yaml.org,2002:map', data.items())
yaml.add_representer(OrderedDict, represent_dict_order)

def check_if_sublists_or_dicts(inputlist):
    for l in inputlist:
        if isinstance(l, (list,dict)):
            return True
    return False

def flow_lists(d):
    if isinstance(d, list):
        return [flow_lists(l) for l in d]
    elif isinstance(d, dict):
        for k, v in d.copy().items():
            if isinstance(v, dict):     # For DICT
                d[k] = flow_lists(v)
            elif isinstance(v, list):   # For LIST
                if check_if_sublists_or_dicts(v):
                    d[k] = flow_lists(v)
                else:
                    d[k] = flow_list(v)
    return d

parser = argparse.ArgumentParser(description='JSON to YAML Converter')
parser.add_argument('inputfile')
parser.add_argument('-o', '--outputfile', default='')
args = parser.parse_args()

f = open(args.inputfile, 'r')
jsonData = json.load(f, object_pairs_hook=OrderedDict)
f.close()

if args.outputfile == '':
    args.outputfile = str(args.inputfile).replace('json','yaml')
ff = open(args.outputfile, 'w+')
yaml.dump(flow_lists(jsonData), ff, allow_unicode=True, default_flow_style=False)
ff.close()
