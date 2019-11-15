import os
import sys
import subprocess

default_binpath = "/sbin/iptables"

def rule_to_list(rule):
    listrule = []
    if rule.chain:
        if rule.position == 'top':
            listrule.append("-I")
        else:
            listrule.append("-A")
        listrule.append(rule.chain.name)
    
    if len(rule.states) > 0:
        listrule.append("-m")
        listrule.append("state")
        listrule.append("--state")
        states = ""
        for s in rule.states:
            states += s + ','
        states = states[:-1]
        listrule.append(states)

    if rule.in_if:
        listrule.append("-i")
        listrule.append(rule.in_if)

    if rule.out_if:
        listrule.append("-o")
        listrule.append(rule.out_if)

    if rule.src:
        listrule.append("-s")
        listrule.append(rule.src)

    if rule.dst:
        listrule.append("-d")
        listrule.append(rule.dst)

    if rule.proto:
        listrule.append("-p")
        listrule.append(rule.proto)

    if len(rule.dports) > 0:
        listrule.append("-m")
        listrule.append("multiport")
        listrule.append("--dports")
        dports = ""
        for p in rule.dports:
            dports += str(p) + ','
        dports = dports[:-1]
        listrule.append(dports)

    if len(rule.comment) > 0:
        listrule.append("-m")
        listrule.append("comment")
        listrule.append("--comment")
        listrule.append(rule.comment)

    if len(rule.action) > 0:
        listrule.append("-j")
        listrule.append(rule.action)      
    
    return listrule



def get_config(**kwargs):
    binpath = kwargs.get('binpath', default_binpath)
    output = subprocess.Popen([binpath+'-save'],
                          stdout=subprocess.PIPE).communicate()[0]
    return output


def exec_cmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    result = p.communicate()[0].decode("utf-8")
    result = str(result)
    return result
