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
        default = 0,
        help    = 'Verbosity level for app.'
    )
    
    args            = parser.parse_args()

    print(str_desc)

    F = FDG.FDG(verbosity = args.str_verbosity)

    l_chain1    = chain_create(
        prefix      = 'l',
        links       = 7,
        nodeInfo    = {'score' : 0.5, 'size': 1, 'type': 'circle'}
    )
    l_chain2    = chain_create(
        prefix      = 'n',
        links       = 7,
        nodeInfo    = {'score' : 0.5, 'size': 1, 'type': 'circle'}
    )
    l_chain3    = chain_create(
        prefix      = 'm',
        links       = 7,
        nodeInfo    = {'score' : 0.5, 'size': 1, 'type': 'circle'}
    )

    F.node_add(
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
            {"id": "orthanc",         "score": 1.0,       "size": 15},
            {"id": "pman-cloud",      "score": 0.2,       "size": 100},
            {"id": "pfioh-cloud",     "score": 0.2,       "size": 100},    
            {"id": "storage-cloud",   "score": 0.3,       "size": 10},    
            {"id": "openshift",       "score": 0.3,       "size": 10},
            {"id": "pl-container1",   "score": 1.0,       "size": 10},
            {"id": "pl-container2",   "score": 1.0,       "size": 10},
            {"id": "pl-container3",   "score": 1.0,       "size": 10},
            {"id": "MOC",             "score": 1.0,       "size": 200}           
        ]
    )
    F.node_add(nodeList     = l_chain1)
    F.node_add(nodeList     = l_chain2)
    # F.node_add(nodeList     = l_chain3)
    
    F.node_connect(fromNode = "BCH",        toNode = ["PACS", "orthanc"])
    F.node_connect(fromNode = "PACS",       toNode = ["pfdcm"])
    F.node_connect(fromNode = "orthanc",    toNode = ["pfdcm"])
    F.node_connect(fromNode = "pfdcm",      toNode = ["pl-pacs"])
    F.node_connect(fromNode = "pl-pacs",    toNode = ["swarm"])
    F.node_connect(fromNode = "swarm",      toNode = ["pman-r1"])
    F.node_connect(fromNode = "swarm",      toNode = ["pfioh-r1"])
    F.node_connect(fromNode = "pfcon",      toNode = ["pfioh-r1", "pman-r1", "CUBE", "storage-r1"])
    F.node_connect(fromNode = "CUBE",       toNode = ["storage-r1"])
    F.node_connect(fromNode = "CUBE",       toNode = ["l6"])
    F.node_connect(fromNode = "pfcon",      toNode = ["n6"])
    # F.node_connect(fromNode = "pfcon",      toNode = ["m6"])

    F.node_connectLinearChain(chain = l_chain1)
    F.node_connectLinearChain(chain = l_chain2)
    # F.node_connectLinearChain(chain = l_chain3)
    
    F.node_connect(fromNode = "l0",             toNode = ["webclient"])
    F.node_connect(fromNode = "n0",             toNode = ["pman-cloud", "pfioh-cloud"])
    F.node_connect(fromNode = "storage-cloud",  toNode = ["pman-cloud", "pfioh-cloud", "openshift"])
    F.node_connect(fromNode = "openshift",      toNode = ["pman-cloud", "pl-container1", "pl-container2", "pl-container3"])
    F.node_connect(fromNode = "MOC",            toNode = ["pl-container1", "pl-container2", "pl-container3"])

    F.FDG_build(saveFile = args.str_saveFile)


