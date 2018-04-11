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

        self.verbosity          = -1
        for k,v in kwargs.items():
            if k == 'verbosity':    self.verbosity  = int(v)

        self.d_desc = {
            "id":       "",
            "type":     "circle",
            "score":    0.5,
            "group":    1,
            "size":     10
        }

        self.l_connectedTo      = []

        self.dp                 = pfmisc.debug(    
                                            verbosity   = self.verbosity,
                                            level       = -1,
                                            within      = self.__name__
                                            )

        for k,v in kwargs.items():
            if k == 'id':       self.d_desc["id"]       = v
            if k == 'type':     self.d_desc["type"]     = v
            if k == 'size':     self.d_desc["size"]     = int(v)
            if k == 'score':    self.d_desc["score"]    = float(v)
            if k == 'group':    self.d_desc["group"]    = int(v)
            if k == 'nodeInfo': self.d_desc             = v
        
        self.dp.qprint('Node created: %s' % self, level = 2)

    def __str__(self):
        return """
        %s
        """ % json.dumps(self.d_desc, indent = 4, sort_keys = True)
        
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

        self.verbosity          = -1
        for k,v in kwargs.items():
            if k == 'verbosity':    self.verbosity  = int(v)

        # nodelist vars
        self.d_mesh             = {}                # The whole mesh containing
                                                    # the dict of nodes and 
                                                    # the dict of links

        self.d_nodeNeighbor     = {}                # dict of each node's 
                                                    # neighbors

        self.d_nodes            = {}                # dict containing the...
        self.ld_nodes           = []                # ... list of dict nodes

        self.l_Node             = []                # a list of node objects
        self.lstr_nodeID        = []                # a similarly indexed list
                                                    # of node names
        self.l_nodeID           = []

        self.d_links            = {}                # dict containing the...
        self.ld_links           = []                # ... list of dict links

        # save file
        self.str_saveFile       = ''

        self.dp                 = pfmisc.debug(    
                                            verbosity   = self.verbosity,
                                            level       = -1,
                                            within      = self.__name__
                                            )

        # per-node variables
        NodeDummy               = Node()
        self.d_nodeLine         = NodeDummy.d_desc

    def node_add(self, *args, **kwargs):
        """
        Add a node to the list of nodes.
        """

        self.dp.qprint('Adding node(s) to FDG structure', level = 1)

        l_inputInfo = []
        for k,v in kwargs.items():
            if k == 'nodeInfo': 
                self.d_nodeLine = v
                l_inputInfo.append(v)
            if k == 'nodeList': l_inputInfo     = v

        if len(l_inputInfo):
            for d_nodeInfo in l_inputInfo:
                N   = Node(
                    nodeInfo    = d_nodeInfo,
                    verbosity   = self.verbosity
                )
                self.l_Node.append(N)
                self.lstr_nodeID.append(
                    d_nodeInfo['id']
                )
                self.dp.qprint('(%s)' % d_nodeInfo['id'])
                self.l_nodeID   = list(range(0, len(self.l_Node)))

    def Node_filterOnID(self, *args, **kwargs):
        """
        Return a Node, filtered on a name string.
        """
        d_ret = {
            'status':   False,
            'Node':     None,
            'index':    0
        }
        str_id    = ""
        for k,v in kwargs.items():
            if k == 'id': str_id    = v
        l_Node  = list(filter(
                lambda n: n.d_desc['id'] == str_id, 
                self.l_Node
        ))
        if len(l_Node):
            d_ret['Node']   = l_Node[0]
            d_ret['status'] = True
            d_ret['index']  = [i for i,j in enumerate(self.l_Node) if j.d_desc['id'] == str_id][0]
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
            if k == 'fromNode':         str_parentNode  = v
            if k == 'toNode':           lstr_childNode  = v
        

        # Find parentNode in internal list
        d_nodeParent    = self.Node_filterOnID(id = str_parentNode)
        Nodeparent      = d_nodeParent['Node']
        parentIndex     = d_nodeParent['index']
        if Nodeparent:
            for str_child in lstr_childNode:
                # Find childNode in internal list
                d_nodechild = self.Node_filterOnID(id = str_child)
                Nodechild   = d_nodechild['Node']
                childIndex  = d_nodechild['index']
                if Nodechild:
                    Nodeparent.connectTo(Node = Nodechild)
                    self.ld_links.append({
                        "source": parentIndex,
                        "target": childIndex
                    })
                    self.dp.qprint('Connecting  %10s <---> %s' %\
                            (str_parentNode, lstr_childNode),
                            level = 1)

    def node_connectLinearChain(self, *args, **kwargs):
        """
        Given a list of nodes, connect them one to the next in 
        list order
        """
        l_chain     = []
        for k,v in kwargs.items():
            if k == 'chain':    l_chain = v
        
        for N, M in zip(l_chain[:-1],l_chain[1:]):
            self.node_connect(fromNode = N['id'], toNode = [M['id']])

            
    def FDGnodelist_build(self, *args, **kwargs):
        """
        Build the list of nodes for the FDG.
        
        Group ID can be 'uniform', with all values set to <groupID>,
        or this can be 'linear', starting with <groupID> and
        increasing with <incremenet>. Group ID strings can also
        be prepended with an optional <prefix>.
        """

        self.dp.qprint('Creating node list...')

        for Node in self.l_Node:
            self.ld_nodes.append(Node.d_desc)

        self.d_nodes = {
            'nodes': self.ld_nodes
        }

        return self.d_nodes

    def FDGlinklist_build(self, *args, **kwargs):
        """
        Build the list of links for the FDG
        """            

        self.dp.qprint('Creating link list...')

        self.d_links    = {
            "links": self.ld_links
        }

        return self.d_links

    def FDG_build(self, *args, **kwargs):
        """
        Assemble and save the final force directed graph.
        """

        self.dp.qprint('Assembling FDG...', level = 1)

        for k,v in kwargs.items():
            if k == 'saveFile':   self.str_saveFile    = v

        self.FDGnodelist_build(**kwargs)
        self.FDGlinklist_build(**kwargs)
        self.d_mesh.update(self.d_nodes)
        self.d_mesh.update(self.d_links)

        self.d_mesh['graph']        = []
        self.d_mesh['directed']     = False
        self.d_mesh['multigraph']   = False

        if len(self.str_saveFile):
            self.dp.qprint('Saving mesh to %s...' % self.str_saveFile, level = 1)
            with open(self.str_saveFile, 'w') as f:
                json.dump(self.d_mesh, f, sort_keys = True, indent = 4)


    def run(self, *args, **kwargs):
        """
        Main run method.
        """
        self.FDG_build(**kwargs)

if __name__ == "__main__":
    
    parser  = ArgumentParser(description = str_desc, formatter_class = RawTextHelpFormatter)

    parser.add_argument(
        '--saveFile',
        action  = 'store',
        dest    = 'saveFile',
        default = '',
        help    = 'File containing created mesh (in JSON format).'
    )
    
    args            = parser.parse_args()

    print(str_desc)

