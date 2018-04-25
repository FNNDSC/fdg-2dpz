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



  __    _            __                 _                 _                    _                                 
 / _|  | |          / _|               | |               | |                  | |                                
| |_ __| | __ _    | |_ _ __  _ __   __| |___  ___ ______| |_ ___  _ __   ___ | | ___   __ _ _   _   _ __  _   _ 
|  _/ _` |/ _` |   |  _| '_ \| '_ \ / _` / __|/ __|______| __/ _ \| '_ \ / _ \| |/ _ \ / _` | | | | | '_ \| | | |
| || (_| | (_| |   | | | | | | | | | (_| \__ \ (__       | || (_) | |_) | (_) | | (_) | (_| | |_| |_| |_) | |_| |
|_| \__,_|\__, |   |_| |_| |_|_| |_|\__,_|___/\___|       \__\___/| .__/ \___/|_|\___/ \__, |\__, (_) .__/ \__, |
           __/ |_____                                             | |                   __/ | __/ | | |     __/ |
          |___/______|                                            |_|                  |___/ |___/  |_|    |___/ 



                        Force Directed Graph Creator
                             FNNDSC-topology 

                              -- version """ + \
             pfmisc.Colors.YELLOW + str_version + pfmisc.Colors.CYAN + """ --

    'fdg_fnndsc-topoloy.py' uses the FDG class to generate a valid d3 JSON for
    the FNNDSC computer backend topology.
    
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
    parser.add_argument(
        '--topology',
        action  = 'store',
        dest    = 'str_topology',
        default = '1',
        help    = 'Topology type.'
    )
    
    args            = parser.parse_args()

    print(str_desc)

    F = FDG.FDG(verbosity = int(args.str_verbosity))

    F.node_add(
        # FNNDSC Nodes
        nodeList = [
            {"id": "fnndsc",            "score": 0.1,       "size": 20},
            {"id": "pretoria",          "score": 0.3,       "size": 400, "type": "circle"},
            {"id": "capetown",          "score": 0.3,       "size": 400},
            {"id": "goldreef",          "score": 0.3,       "size": 400},    
            {"id": "rc-fs-tautona",     "score": 0.8,       "size": 400},
            {"id": "santorini",         "score": 0.9,       "size": 200},    
            {"id": "seville",           "score": 0.1,       "size": 200},
            {"id": "hercules",          "score": 0.1,       "size": 400},
            {"id": "hippocrates",       "score": 0.9,       "size": 400},
            {"id": "zeus",              "score": 0.9,       "size": 400},
            {"id": "athena",            "score": 0.1,       "size": 400},
            {"id": "ChRIS",             "score": 0.1,       "size": 200}   
        ]
    ) 

    if args.str_topology == '1':
        F.node_add(
            # FNNDSC Nodes
            nodeList = [
            {"id": "tautona",           "score": 0.9,       "size": 800},    
            ]
        )

    if args.str_topology == '2':
        F.node_add(
            # FNNDSC Nodes
            nodeList = [
            {"id": "tautona-users",     "score": 0.9,       "size": 500},    
            {"id": "tautona-research",  "score": 0.9,       "size": 500},    
            {"id": "fnndsc-map",        "score": 0.1,       "size": 20},    
            {"id": "fnndsc-mri",        "score": 0.1,       "size": 20},    
            {"id": "fnndsc-nirs",       "score": 0.1,       "size": 20},    
            {"id": "fnndsc-meg",        "score": 0.1,       "size": 20},    
            {"id": "fnndsc-cbd",        "score": 0.1,       "size": 20},    
            {"id": "fnndsc-cel",        "score": 0.1,       "size": 20}
            ]
        )

    if args.str_topology == '2':
        # Chains to RCEs
        d_chainRCE  = {}
        l_chainRCE  = range(0, int(args.str_chains))
        for chain in l_chainRCE:
            d_chainRCE[chain] = chain_create(
                prefix      = str(chain),
                links       = 5,
                nodeInfo    = {'score' : 0.5, 'size': 1, 'type': 'circle'}
            )
            F.node_add(nodeList = d_chainRCE[chain])
            F.node_connectLinearChain(chain = d_chainRCE[chain])

    # Client workstations
    d_clientGroups  = { 'fnndsc-cbd' :  [], 
                        'fnndsc-meg' :  [], 
                        'fnndsc-cel' :  [], 
                        'fnndsc-mri' :  [], 
                        'fnndsc-nirs' : []}
    for workstationGroup in d_clientGroups.keys():
        d_clientGroups[workstationGroup] = chain_create(
            prefix      = workstationGroup,
            links       = int(args.str_chainLength),
            nodeInfo    = {'score' : 0.5, 'size': 10, 'type': 'circle'}
        )
        # pudb.set_trace()
        F.node_add(     
                        nodeList    = d_clientGroups[workstationGroup]
                    )
        F.node_connectLinearChain(
                        chain       = d_clientGroups[workstationGroup]
                        )
        if args.str_topology == '1':
            F.node_connect( 
                            fromNode    = "fnndsc",     
                            toNode      = d_clientGroups[workstationGroup]
                        )
        if args.str_topology == '2':
            F.node_connect( 
                            fromNode    = workstationGroup,     
                            toNode      = d_clientGroups[workstationGroup]
                        )

    # Connect main core nodes together
    F.node_connect(     fromNode = "ChRIS",         toNode = ["fnndsc"])
    F.node_connect(     fromNode = "athena",        toNode = ["zeus"])
    F.node_connect(     fromNode = "seville",       toNode = ["santorini"])
    F.node_connect(     fromNode = "hippocrates",   toNode = ["hercules"])

    if args.str_topology == '1':
        F.node_connect( fromNode    = "tautona",       
                        toNode          = [ "fnndsc", 
                                            "pretoria", 
                                            "capetown", 
                                            "goldreef", 
                                            "rc-fs-tautona"])
        F.node_connect( fromNode    = "fnndsc",        
                        toNode          = [ "pretoria", 
                                            "capetown", 
                                            "goldreef", 
                                            "rc-fs-tautona", 
                                            "santorini", 
                                            "seville", 
                                            "zeus", 
                                            "athena", 
                                            "hercules", 
                                            "hippocrates"])

    if args.str_topology == '2':
        F.node_connect( fromNode    = "fnndsc-map",    
                        toNode          = [ "fnndsc", 
                                            "fnndsc-cbd", 
                                            "fnndsc-cel", 
                                            "fnndsc-meg"])
        F.node_connect( fromNode    = "fnndsc",        
                        toNode          = [ "00"])

        F.node_connect( fromNode    = "04",    
                        toNode          = [ "tautona-research", 
                                            "tautona-users"])

        F.node_connect( fromNode    = "fnndsc",        
                        toNode          = [ "fnndsc-mri", 
                                            "fnndsc-nirs"])

        F.node_connect( fromNode    = "fnndsc-cbd",    
                        toNode          = [ "santorini", 
                                            "seville"])

        F.node_connect( fromNode    = "fnndsc-cel",    
                        toNode          = [ "hippocrates", 
                                            "hercules"])

        F.node_connect( fromNode    = "fnndsc-meg",    
                        toNode          = [ "zeus", 
                                            "athena"])

        F.node_connect( fromNode    = "tautona-users", 
                        toNode          = [ "pretoria", 
                                            "rc-fs-tautona"])
        F.node_connect( fromNode    = "tautona-research", 
                        toNode          = [ "capetown", 
                                            "goldreef"])
        F.node_connect( fromNode = "00",    
                        toNode          = [ "pretoria", 
                                            "capetown", 
                                            "goldreef", 
                                            "rc-fs-tautona"])

    F.FDG_build(saveFile = args.str_saveFile)


