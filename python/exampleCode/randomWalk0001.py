# -*- coding: utf-8 -*-
"""
@author: coss
"""
import random

from copenmed_tools.python.copenmed_tools import *

class RandomWalk():
    def __init__(self, fnPickle="copenmed.pkl", debug=False):
        _, _, self.entity_type_dict, self.entity_type_dict_info, \
           self.entity_dict, self.entity_dict_info, \
           self.edge_type_dict, self.edge_type_dict_info, \
           self.list_bidirectional_relations, \
           self.edge_dict, self.edge_dict_info, \
           self.details_dict, self.details_dict_info, _, _ = \
               load_database(fnPickle)

        self.id_dict = define_labels(self.entity_type_dict,
                                     self.edge_type_dict)
        add_directional_edges(self.edge_dict, 
                              self.list_bidirectional_relations)
        
        self.graph = Graph(self.entity_dict, self.entity_type_dict, 
                           self.edge_dict, self.id_dict)

        self.accesible={}
        for idEntity in range(self.graph.getNodeMax()):
            node = self.graph.getNode(idEntity)
            if node is None:
                continue
            self.accesible[idEntity] = [x for x in node.outgoingEdges.keys()]+\
                                       [x for x in node.incomingEdges.keys()]


    def randomWalkSingleNode(self, idEntity, walkLength):
        if len(self.accesible[idEntity])==0:
            return []
        selected = random.choice(self.accesible[idEntity])
        if walkLength==1:
            return [selected]
        else:
            
            return [selected]+self.randomWalkSingleNode(selected[0],
                                                        walkLength-1)

    def randomWalkAllNodes(self, fnRoot="randomWalk", Nwalks=1, walkLength=2):
        fhOut = open(fnRoot+"_walks.txt","w")
        vocab = {}
        for idEntity in self.accesible:
            for iwalk in range(Nwalks):
                randomWalkList = self.randomWalkSingleNode(idEntity, walkLength)
                if len(randomWalkList)==0:
                    continue
                entityKey = "e%d"%idEntity
                if not entityKey in vocab:
                    vocab[entityKey]=1
                toPrint = entityKey+" "
                for idEntityTo, idEdge in randomWalkList:
                    entityToKey = "e%d"%idEntityTo
                    if not entityToKey in vocab:
                        vocab[entityToKey]=1
                    
                    edgeKey = "r%d"%idEdge
                    if not edgeKey in vocab:
                        vocab[edgeKey]=1

                    toPrint+="%s %s "%(edgeKey,entityToKey)
                fhOut.write("%s <eol>\n"%toPrint)
        fhOut.close()
        
        fhOut = open(fnRoot+"_vocab.txt","w")
        for word in sorted(vocab):
            fhOut.write("%s\n"%word)
        fhOut.close()

if __name__=="__main__":                                
    randomWalk = RandomWalk()
    randomWalk.randomWalkAllNodes("randomWalk",100,30)
