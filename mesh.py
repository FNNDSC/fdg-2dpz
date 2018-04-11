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

                     _     
                    | |    
 _ __ ___   ___  ___| |__  
| '_ ` _ \ / _ \/ __| '_ \ 
| | | | | |  __/\__ \ | | |
|_| |_| |_|\___||___/_| |_|
                           
                           



                            Force Directed Graph Mesh 

                              -- version """ + \
             pfmisc.Colors.YELLOW + str_version + pfmisc.Colors.CYAN + """ --

    'mesh.py' generates mesh-type force directed graphs and saves to output
    JSON formatted files, suitable for reading by a web-based client.
    
""" + pfmisc.Colors.NO_COLOUR


class Mesh:
    
    def __init__(self, *args, **kwargs):
        """
        Constructor for Mesh class
        """

        self.__name__           = 'Mesh'

        # General mesh characteristics
        self.spokes             = 2
        self.nodes              = 10

        # nodelist vars
        self.d_mesh             = {}                # The whole mesh containing the ...
                                                    # ... dict of nodes and dict of links

        self.d_nodeNeighbor     = {}                # dict of each node's neighbors

        self.d_nodes            = {}                # dict containing the...
        self.ld_nodes           = []                # ... list of dict nodes
        self.l_nodes            = []                # Just a list of node indices

        self.d_links            = {}                # dict containing the...
        self.ld_links           = []                # ... list of dict links

        self.str_groupSpread    = 'uniform'
        self.str_prefix         = ''
        self.groupID            = 1
        self.increment          = 1

        # save file
        self.str_saveFile       = ''

        self.dp                 = pfmisc.debug(    
                                            verbosity   = 0,
                                            level       = -1,
                                            within      = self.__name__
                                            )


        for k,v in kwargs.items():
            if k == 'spokes': self.spokes = v
            if k == 'nodes':  self.nodes  = v
        
        self.dp.qprint('Creating node list of %d nodes...' % self.nodes)
        self.l_nodes            = list(range(self.nodes))
        self.d_nodeNeighbor     = dict(enumerate(self.l_nodes))


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

    M = Mesh(   
                spokes          = int(args.spokes), 
                nodes           = int(args.nodes)
            )

    M.run(      
                prefix          = args.prefix,
                groupSpread     = args.groupSpread,
                groupID         = args.groupID,
                increment       = args.increment,
                linkValue       = args.linkValue,
                saveFile        = args.saveFile
        )