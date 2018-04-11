#!/usr/bin/env python3
#
# (c) 2017 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#



from    argparse            import RawTextHelpFormatter
from    argparse            import ArgumentParser
import  pudb
import  pfmisc

import  json
import  numpy as np
import  random

str_version = "0.9.9.9"
str_desc = pfmisc.Colors.CYAN + """


  __    _               _          _                       _                     
 / _|  | |             | |        (_)                     | |                    
| |_ __| | __ _     ___| |__  _ __ _ ___ ______ ___  _ __ | |_   _   _ __  _   _ 
|  _/ _` |/ _` |   / __| '_ \| '__| / __|______/ _ \| '_ \| | | | | | '_ \| | | |
| || (_| | (_| |  | (__| | | | |  | \__ \     | (_) | | | | | |_| |_| |_) | |_| |
|_| \__,_|\__, |   \___|_| |_|_|  |_|___/      \___/|_| |_|_|\__, (_) .__/ \__, |
           __/ |_____                                         __/ | | |     __/ |
          |___/______|                                       |___/  |_|    |___/ 



                        Force Directed Graph Creator
                                 ChRIS-only 

                              -- version """ + \
             pfmisc.Colors.YELLOW + str_version + pfmisc.Colors.CYAN + """ --

    'fdg_chris-only.py' uses the FDG class to generate a valid d3 JSON for
    a ChRIS topology.
    
""" + pfmisc.Colors.NO_COLOUR

import fdg_create as FDG

def chain_create(*args, **kwargs):
    """
    Create a node list containg N links, with string-id prefix.
    """
    str_prefix  = "l"
    links       = 7

    N           = FDG.Node()
    d_nodeInfo  = N.d_desc.copy()
    l_chain     = []

    for k,v in kwargs.items():
        if k == 'prefix':   str_prefix  = v
        if k == 'links':    links       = v
        if k == 'nodeInfo': d_nodeInfo  = v

    for n in range(0, links):
        d_nodeInfo['id']  = '%s%d' % (str_prefix, n)
        l_chain.append(d_nodeInfo.copy())

    return l_chain

if __name__ == "__main__":
    
    parser  = ArgumentParser(description = str_desc, formatter_class = RawTextHelpFormatter)

    parser.add_argument(
        '--saveFile',
        action  = 'store',
        dest    = 'str_saveFile',
        default = '',
        help    = 'File containing created mesh (in JSON format).'
    )
    parser.add_argument(
        '--verbosity',
        action  = 'store',
        dest    = 'str_verbosity',
        default = '0',
        help    = 'Verbosity level for app.'
    )
    parser.add_argument(
        '--chains',
        action  = 'store',
        dest    = 'str_chains',
        default = 1,
        help    = 'Number of remote compute env chains.'
    )
    parser.add_argument(
        '--chainLength',
        action  = 'store',
        dest    = 'str_chainLength',
        default = '7',
        help    = 'Number of remote compute env chains.'
    )
    
    args            = parser.parse_args()

    print(str_desc)

    F = FDG.FDG(verbosity = int(args.str_verbosity))

    # Chain to webclient
    l_chain1    = chain_create(
        prefix      = 'w',
        links       = int(args.str_chainLength),
        nodeInfo    = {'score' : 0.5, 'size': 1, 'type': 'circle'}
    )
    F.node_add(nodeList     = l_chain1)
    F.node_connectLinearChain(chain = l_chain1)

    # Chains to RCEs
    d_chainRCE  = {}
    l_chainRCE  = range(0, int(args.str_chains))
    for chain in l_chainRCE:
        d_chainRCE[chain] = chain_create(
            prefix      = str(chain),
            links       = int(args.str_chainLength),
            nodeInfo    = {'score' : 0.5, 'size': 1, 'type': 'circle'}
        )
        F.node_add(nodeList = d_chainRCE[chain])
        # RCE Nodes
        F.node_add(nodeList = [
            {"id": "pman-cloud%d"       % chain,    "score": 0.2,       "size": 100},
            {"id": "pfioh-cloud%d"      % chain,    "score": 0.2,       "size": 100},    
            {"id": "storage-cloud%d"    % chain,    "score": 0.3,       "size": 10},    
            {"id": "openshift%d"        % chain,    "score": 0.3,       "size": 10},
            {"id": "pl-container1%d"    % chain,    "score": 1.0,       "size": 10},
            {"id": "pl-container2%d"    % chain,    "score": 1.0,       "size": 10},
            {"id": "pl-container3%d"    % chain,    "score": 1.0,       "size": 10},
            {"id": "MOC%d"              % chain,    "score": 1.0,       "size": 200}           
        ])

    F.node_add(
        # BCH Nodes
        nodeList = [
            {"id": "BCH",             "score": 0.8,       "size": 200, "type": "circle"},
            {"id": "webclient",       "score": 0.7,       "size": 100},
            {"id": "CUBE",            "score": 0.1,       "size": 250, "type": "circle"},
            {"id": "pfcon",           "score": 0.2,       "size": 250},
            {"id": "pfioh-r1",        "score": 0.2,       "size": 100},    
            {"id": "pman-r1",         "score": 0.2,       "size": 100},
            {"id": "storage-r1",      "score": 0.3,       "size": 10},    
            {"id": "swarm",           "score": 0.3,       "size": 1},
            {"id": "pfdcm",           "score": 1.0,       "size": 1},
            {"id": "pl-pacs",         "score": 1.0,       "size": 1},
            {"id": "PACS",            "score": 1.0,       "size": 20},    
            {"id": "orthanc",         "score": 1.0,       "size": 15}
        ]
    )
    F.node_connect(fromNode = "w0",         toNode = ["webclient"])
    
    # BCH Side
    F.node_connect(fromNode = "BCH",        toNode = ["PACS", "orthanc"])
    F.node_connect(fromNode = "PACS",       toNode = ["pfdcm"])
    F.node_connect(fromNode = "orthanc",    toNode = ["pfdcm"])
    F.node_connect(fromNode = "pfdcm",      toNode = ["pl-pacs"])
    F.node_connect(fromNode = "pl-pacs",    toNode = ["swarm"])
    F.node_connect(fromNode = "swarm",      toNode = ["pman-r1"])
    F.node_connect(fromNode = "swarm",      toNode = ["pfioh-r1"])
    F.node_connect(fromNode = "pfcon",      toNode = ["pfioh-r1", "pman-r1", "CUBE", "storage-r1"])
    F.node_connect(fromNode = "CUBE",       toNode = ["storage-r1"])
    F.node_connect(fromNode = "CUBE",       toNode = ["w6"])

    # Remote Computing Environment
    for chain in l_chainRCE:
        str_nodeEnd     = "%s%d" % (str(chain), int(args.str_chainLength)-1)
        str_nodeStart   = "%s0" % str(chain)
        F.node_connect(fromNode = "pfcon",  toNode = ["%s%d" % \
                    (str(chain), int(args.str_chainLength)-1)])
        F.node_connectLinearChain(chain = d_chainRCE[chain])
        F.node_connect( fromNode    = str_nodeStart,    
                        toNode      = [ "pman-cloud%d"      % chain, 
                                        "pfioh-cloud%d"     % chain])
        F.node_connect( fromNode    =   "storage-cloud%d"   % chain,  
                        toNode      = [ "pman-cloud%d"      % chain, 
                                        "pfioh-cloud%d"     % chain, 
                                        "openshift%d"       % chain])
        F.node_connect( fromNode    =   "openshift%d"       % chain,      
                        toNode      = [ "pman-cloud%d"      % chain, 
                                        "pl-container1%d"   % chain, 
                                        "pl-container2%d"   % chain, 
                                        "pl-container3%d"   % chain])
        F.node_connect( fromNode    =   "MOC%d"             % chain,            
                        toNode      = [ "pl-container1%d"   % chain, 
                                        "pl-container2%d"   % chain, 
                                        "pl-container3%d"   % chain])

    F.FDG_build(saveFile = args.str_saveFile)


