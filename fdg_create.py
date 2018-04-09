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

             
  __    _                              _                     
 / _|  | |                            | |                    
| |_ __| | __ _     ___ _ __ ___  __ _| |_ ___   _ __  _   _ 
|  _/ _` |/ _` |   / __| '__/ _ \/ _` | __/ _ \ | '_ \| | | |
| || (_| | (_| |  | (__| | |  __/ (_| | ||  __/_| |_) | |_| |
|_| \__,_|\__, |   \___|_|  \___|\__,_|\__\___(_) .__/ \__, |
           __/ |_____                           | |     __/ |
          |___/______|                          |_|    |___/ 
                                                             
              
                        Force Directed Graph Creator

                              -- version """ + \
             pfmisc.Colors.YELLOW + str_version + pfmisc.Colors.CYAN + """ --

    'fdg_creator.py' generates force directed graphs in JSON format
    suitable for d3 interpretation.
    
""" + pfmisc.Colors.NO_COLOUR

class Node: 
    """
    A node in an FDG has the following properties:

        * str_name
        * size
        * str_type
        * score 
        
        * list of nodes to which it is connected.

    """

    def __init__(self, *args, **kwargs):
        """
        Constructor for FDG node.
        """

        self.__name__           = "node"

        self.str_name           = ""
        self.str_type           = ""
        self.size               = 10
        self.f_score            = 0.5

        self.l_connectedTo      = []

        self.dp                 = pfmisc.debug(    
                                            verbosity   = 0,
                                            level       = -1,
                                            within      = self.__name__
                                            )

        for k,v in kwargs.items():
            if k == 'name':     self.str_name   = v
            if k == 'type':     self.str_type   = v
            if k == 'size':     self.size       = int(v)
            if k == 'score':    self.f_score    = float(v)
        
        self.dp.qprint('Creating node "%s"...' % self.str_name)

    def connectTo(self, *args, **kwargs):
        """
        Connect this node to target (in kwargs)
        """
        b_status    = False
        Node        = None
        for k,v in kwargs.items():
            if k == 'Node':     Node = v

        if Node:
            self.l_connectedTo.append(Node)
            b_status    = True

        return {
            'status':   b_status
        }

class FDG:
    
    def __init__(self, *args, **kwargs):
        """
        Constructor for FDG class -- this is collection of
        nodes that are saved to a JSON representation.
        """

        self.__name__           = 'FDG'


        # nodelist vars
        self.d_mesh             = {}                # The whole mesh containing
                                                    # the dict of nodes and 
                                                    # the dict of links

        self.d_nodeNeighbor     = {}                # dict of each node's 
                                                    # neighbors

        self.d_nodes            = {}                # dict containing the...
        self.ld_nodes           = []                # ... list of dict nodes

        self.l_nodes            = []                # a list of nodes to save

        self.l_Node             = []                # a list of node objects
        self.lstr_nodeName      = []                # a similarly indexed list
                                                    # of node names

        self.d_links            = {}                # dict containing the...
        self.ld_links           = []                # ... list of dict links

        # save file
        self.str_saveFile       = ''

        self.dp                 = pfmisc.debug(    
                                            verbosity   = 0,
                                            level       = -1,
                                            within      = self.__name__
                                            )

        # per-node variables
        self.str_name           = ""
        self.str_type           = ""
        self.size               = 10
        self.f_score            = 0.5

    def node_add(self, *args, **kwargs):
        """
        Add a node to the list of nodes.
        """
        for k,v in kwargs.items():
            if k == 'name':     self.str_name   = v
            if k == 'type':     self.str_type   = v
            if k == 'size':     self.size       = int(v)
            if k == 'score':    self.f_score    = float(v)

        self.l_Node.append(Node(
            name    = self.str_name,
            type    = self.str_type,
            size    = self.size,
            score   = self.f_score
        ))

    def Node_filterOnName(self, *args, **kwargs):
        """
        Return a Node, filtered on a name string.
        """
        d_ret = {
            'status':   False,
            'Node':     None
        }
        str_name    = ""
        for k,v in kwargs.items():
            if k == 'name': str_name    = v
        l_Node  = list(filter(
                lambda n: n.str_name == str_parentNode, 
                self.l_Node
        ))
        if len(l_Node):
            d_ret['Node']   = l_Node[0]
            d_ret['status'] = True
        return d_ret

    def node_connect(self, *args, **kwargs):
        """
        Connect a parent node (kwarg: str_parentNode) to a list of 
        child nodes (lstr_childNode).
        """
        lstr_childNode  = []
        str_parentNode  = ""
        Nodeparent      = None
                
        for k,v in kwargs.items():
            if k == 'parentNode':       str_parentNode  = v
            if k == 'toChildNode':      lstr_childNode  = v
        
        # Find parentNode in internal list
        Nodeparent      = self.Node_filterOnName(name = str_parentNode)['Node']
        if Nodeparent:
            for str_child in lstr_childNode:
                # Find childNode in internal list
                Nodechild   = self.Node_filterOnName(name = str_child)['Node']
                if Nodechild:
                    Nodeparent.connectTo(Node = Nodechild)

    def connect(self, *args, **kwargs):
        """
        Connect each node to a random sample (of size <spoke>)
        drawn from list of all nodes.
        """
        self.dp.qprint('Connecting each node to sample of %d other nodes...' % self.spokes)
        for k,v in self.d_nodeNeighbor.items():
            self.d_nodeNeighbor[k] = random.sample(self.l_nodes, self.spokes)
            
    def FDGnodelist_build(self, *args, **kwargs):
        """
        Build the list of nodes for the FDG.
        
        Group ID can be 'uniform', with all values set to <groupID>,
        or this can be 'linear', starting with <groupID> and
        increasing with <incremenet>. Group ID strings can also
        be prepended with an optional <prefix>.
        """

        self.dp.qprint('Creating node list...')

        for k,v in kwargs.items():
            if k == 'groupSpread': self.str_groupSpread = v
            if k == 'groupID':     self.groupID         = int(v)
            if k == 'prefix':      self.str_prefix      = v
            if k == 'increment':   self.increment       = int(v)

        lstr_ID         = [self.str_prefix] * self.nodes
        l_IDuniform     = [self.groupID] * self.nodes
        l_IDincrement   = list(range(self.groupID, self.groupID + self.nodes*self.increment, self.increment))
        if self.str_groupSpread == 'uniform':
            l_ID        = l_IDuniform
        if self.str_groupSpread == 'increment':
            l_ID        = l_IDincrement
            
        l_fullID        = ['%s%d' % (s, i) for (s, i) in zip(lstr_ID, l_IDincrement)]

        for n in range(self.nodes):
            self.ld_nodes.append({
                "id":       l_fullID[n],
                "group":    l_ID[n]
            })

        self.d_nodes = {
            'nodes': self.ld_nodes
        }

        return self.d_nodes

    def FDGlinklist_build(self, *args, **kwargs):
        """
        Build the list of links for the FDG
        """            

        self.dp.qprint('Creating link list...')

        linkValue = 1
        for k,v in kwargs.items():
            if k == 'linkValue':    linkValue = int(v)

        for k, l_node in self.d_nodeNeighbor.items():
            for neighbor in l_node:
                self.ld_links.append({
                    "source":   self.ld_nodes[k]['id'],
                    "target":   self.ld_nodes[neighbor]['id'],
                    "value":    linkValue
                })
        self.d_links = {
            'links': self.ld_links
        }

        return self.d_links

    def FDG_build(self, *args, **kwargs):
        """
        Assemble and save the final force directed graph.
        """

        self.dp.qprint('Assembling FDG...')

        for k,v in kwargs.items():
            if k == 'saveFile':   self.str_saveFile    = v

        self.FDGnodelist_build(**kwargs)
        self.FDGlinklist_build(**kwargs)
        self.d_mesh.update(self.d_nodes)
        self.d_mesh.update(self.d_links)
        if len(self.str_saveFile):
            self.dp.qprint('Saving mesh to %s...' % self.str_saveFile)
            with open(self.str_saveFile, 'w') as f:
                json.dump(self.d_mesh, f, sort_keys = True, indent = 4)


    def run(self, *args, **kwargs):
        """
        Main run method.
        """

        self.connect()
        self.FDG_build(**kwargs)

if __name__ == "__main__":
    
    parser  = ArgumentParser(description = str_desc, formatter_class = RawTextHelpFormatter)

    parser.add_argument(
        '--spokes',
        action  = 'store',
        dest    = 'spokes',
        default = '3',
        help    = 'Number of spokes (edges) from each node.'
    )
    parser.add_argument(
        '--nodes',
        action  = 'store',
        dest    = 'nodes',
        default = '20',
        help    = 'Number of nodes in mesh graph.'
    )
    parser.add_argument(
        '--prefix',
        action  = 'store',
        dest    = 'prefix',
        default = 'linkm',
        help    = 'Prefix for group name'
    )
    parser.add_argument(
        '--groupSpread',
        action  = 'store',
        dest    = 'groupSpread',
        default = 'uniform',
        help    = 'Group ID spread in graph.'
    )
    parser.add_argument(
        '--groupID',
        action  = 'store',
        dest    = 'groupID',
        default = '1',
        help    = 'Group ID start.'
    )
    parser.add_argument(
        '--increment',
        action  = 'store',
        dest    = 'increment',
        default = '1',
        help    = 'Group ID increment.'
    )
    parser.add_argument(
        '--linkValue',
        action  = 'store',
        dest    = 'linkValue',
        default = '1',
        help    = 'Link connection value.'
    )
    parser.add_argument(
        '--saveFile',
        action  = 'store',
        dest    = 'saveFile',
        default = '',
        help    = 'File containing created mesh (in JSON format).'
    )
    
    args            = parser.parse_args()

    print(str_desc)

    M = FDG(   
                spokes          = int(args.spokes), 
                nodes           = int(args.nodes)
            )

    FDG.run(      
                prefix          = args.prefix,
                groupSpread     = args.groupSpread,
                groupID         = args.groupID,
                increment       = args.increment,
                linkValue       = args.linkValue,
                saveFile        = args.saveFile
        )