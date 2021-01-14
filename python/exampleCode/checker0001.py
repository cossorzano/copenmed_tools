# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 17:17:27 2021

@author: coss
"""

import pickle
from copenmed_tools.python.copenmed_tools import *

class Checker():
    def __init__(self):
        fnIntermediate = "reasoning3.pkl"
        fh = open(fnIntermediate,'rb')
        (self.entity_type_dict, self.entity_dict, self.edge_type_dict, 
               self.edge_dict, self.id_dict, self.entities, 
               self.graph, self.w) = pickle.load(fh)
        fh.close()

    def checkRedundancy(self):
        for idEntity in range(self.graph.getNodeMax()):
            node = self.graph.getNode(idEntity)
            if node is None:
                continue
    
            # For all outgoing edges
            for idEntityTo in node.reachableDown:
                maxWeight1=0.0
                for path in node.reachableDown[idEntityTo]:
                    if len(path.path)==2:
                        maxWeight1=max(maxWeight1,path.getLastWeight()[-1])
                # print(idEntity,idEntityTo,maxWeight1)
            
                if maxWeight1>0.8:
                    for path in node.reachableDown[idEntityTo]:
                        if len(path.path)>2:
                            print("Posible path redundante entre %d %d: %s"%\
                                  (idEntity,idEntityTo,
                                   path.pretty(self.entity_dict, 
                                               self.edge_type_dict)))

checker = Checker()
checker.checkRedundancy()
