
import os
import sys
import subprocess
import json
from .utils import rule_to_list, default_binpath, get_config, clr, exec_cmd


class Iptables:

    def __init__(self, **kwargs):
        self.binpath = kwargs.get('binpath', default_binpath)
        self.rules = []
        self.chains = get_chains(self.binpath)
        self.policy = 'DROP'

    def add(self, obj):
        self.rules.append(obj)
        return self.rules
    
    def commit(self):
        for rule in self.rules:
            curule = [self.binpath]
            for parameter in rule.get():
                curule.append(parameter)
            exec_cmd(curule)
        return True
    
    def flush(self):
        chains = ['INPUT', 'OUTPUT']
        for chain in chains:
            command = [self.binpath]
            command.append('-F')
            command.append(chain)
            exec_cmd(command)
    
    def change_policy(self, policy):
        policies_list = ['ACCEPT', 'DROP', 'REJECT']
        if policy in policies_list:
            self.policy = policy
        self.write_policy()
    
    def write_policy(self):
        rules_types = ['INPUT', 'OUTPUT']
        for rule_type in rules_types:
            command = [self.binpath, '-P', rule_type, self.policy]
            exec_cmd(command)

    def show(self):
        return get_config(binpath=self.binpath)
    
    def export_to(self, file_path):
        raw_rules_list = []
        for rule in self.rules:
            rule_list = rule.get()
            raw_rules_list.append(rule_list)
        with open(file_path, 'w') as json_file:
            json.dump(raw_rules_list, json_file, indent=4)


    def import_from(self, file_path, ip=None):
        with open(file_path) as json_file:  
            raw_rules_list = json.load(json_file)
            for rule in raw_rules_list:
                curule = [self.binpath]
                for parameter in rule:
                    if parameter == '{{client_ip}}':
                        if ip:
                            curule.append(ip)
                        else:
                            curule.pop()
                    else:
                        curule.append(parameter)
                exec_cmd(curule)
        self.write_policy()

    def optimize(self):
        for c in self.chains:
            for r in c.rules:
                # Must be int later
                if r.hits == '0':
                    txt = "[{}] You can remove this rule: ".format(clr('*', 'G'))
                    print(txt, r.get())
class Rule:

    def __init__(self, **kwargs):
        self.position = kwargs.get('position', 'bottom')
        self.action = kwargs.get('action', 'ACCEPT')
        self.chain = Chain(name=kwargs.get('chain', 'INPUT'))
        self.comment = kwargs.get('comment', '')
        self.match = kwargs.get('match', '')
        self.dports = kwargs.get('dports', [])
        self.states = kwargs.get('states', [])
        self.src = kwargs.get('src', '')
        self.dst = kwargs.get('dst', '')
        self.proto = kwargs.get('proto', '')
        self.in_if = kwargs.get('in_if', '')
        self.out_if = kwargs.get('out_if', '')
        self.hits = 0

    def get(self):
        return rule_to_list(self)



class Chain:

    def __init__(self, **kwargs):
        self.binpath = kwargs.get('binpath', default_binpath)
        self.name = kwargs.get('name', '')
        self.rules = get_rules(self.binpath, self.name)


""" Rules functions """

def get_rules(binpath, chain_name):
        try:
            rules = []
            output = exec_cmd([binpath, "-vnL", chain_name])

            for line in output.splitlines():
                line = line.strip()

                if not line.startswith("Chain"):
                    if not line.startswith('pkts'):

                        linesplit = line.split()

                        if len(linesplit) > 0:
                            hits = linesplit[1]
                            action= line.split()[2]
                            in_if = linesplit[5]
                            out_if = linesplit[6]
                            src = linesplit[7]
                            dst = linesplit[8]
                            proto = line.split()[3]

                            rule = Rule(chain=chain_name,
                                        action=action,
                                        proto = proto
                                        )
                            
                            if len(linesplit) >= 11:
                                if 'multiport' in linesplit:
                                    dports = linesplit[11]
                                    dports = dports.split(',')
                                    rule.dports = dports

                                if any('dpt:' in term for term in linesplit):
                                    port = linesplit[10]
                                    port = port.split(':')[1]
                                    rule.dports = [port]


                            if in_if != '*':
                                rule.in_if = in_if

                            if out_if != '*':
                                rule.out_if = out_if

                            if src != '0.0.0.0/0':
                                rule.src = src     

                            if dst != '0.0.0.0/0':
                                rule.dst = dst

                            rule.hits = hits


                            rules.append(rule)

            for r in rules:
                yield r
        except:
            print('####DEBUG####:', linesplit)
            raise

""" Chains functions """
def get_chains(binpath):
    chains = []
    output = exec_cmd([binpath, "-vnL"])
    for line in output:
        line = line.split()
        if len(line) > 0:
            if line[0] == 'Chain':
                c = Chain(name=line.split()[1])
                chains.append(c)
    return chains