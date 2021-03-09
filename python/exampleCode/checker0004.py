# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 17:17:27 2021

@author: coss
"""

from copenmed_tools.python.copenmed_tools import *

class Checker():
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
        self.graph.createPaths(2,0.25)

    def checkRedundancy(self):
        print("Analisis de enlaces redundantes: =============================")
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
                        #print(idEntity,idEntityTo,maxWeight1)
                #0.8 como argumento
                if maxWeight1>0.8:
                    for path in node.reachableDown[idEntityTo]:
                        if len(path.path)==2:
                            direct_path=[]
                            redundant_list = []
                            direct_path.append(path)
                            directEdgeType = path.returnEdgeType()
                        if len(path.path)>2:
                            print("Enlace directo:", direct_path[-1])
                            print("Posible path redundante entre %d %d: %s"%\
                                  (idEntity,idEntityTo,
                                   path.pretty(self.entity_dict, 
                                               self.edge_type_dict,redundant_list,directEdgeType)))

    def checkSpecialty(self):
        specialty_dict = {}
        DISEASE = self.id_dict['Disease']
        GROUPOFDISEASES = self.id_dict['GroupOfDiseases']
        for idEdge in self.edge_dict:
            edge = self.edge_dict[idEdge]
            idEntity = edge[0]
            entityType = self.entity_dict[idEntity][1]
            if not entityType==DISEASE and not entityType==GROUPOFDISEASES:
                continue
            if not idEntity in specialty_dict:
                specialty_dict[idEntity]  = 0
            edge_name = edge[3]
            inTheDomain = "Specialty" in edge_name
            if inTheDomain:
                specialty_dict[idEntity] = 1
        print("Entidades sin especialidad: =============================")
        toPrint=""
        Ncount=0
        for idEntity, value in specialty_dict.items():
            if value==0:
                toPrint+="%d, "%idEntity
                Ncount+=1
        print(toPrint)
        print("Numero de entidades sin especialidad: %d"%Ncount)
        return specialty_dict
    
    def checkPrevalence(self):
        prevalence_dict = {}
        DISEASE = self.id_dict['Disease']
        GROUPOFDISEASES = self.id_dict['GroupOfDiseases']
        for idEdge in self.edge_dict:
            edge = self.edge_dict[idEdge]
            idEntity = edge[0]
            entityType = self.entity_dict[idEntity][1]
            if not entityType==DISEASE and not entityType==GROUPOFDISEASES:
                continue
            if not idEntity in prevalence_dict:
                prevalence_dict[idEntity]  = 0
            edge_name = edge[3]
            disease = " Disease " in edge_name
            disease_group = " Group " in edge_name
            if disease or disease_group:
                prevalent_disease = " prevalence of this Disease in this Population is " in edge_name
                prevalent_group = " prevalence of this Group in this Population is " in edge_name
                if prevalent_disease or prevalent_group:
                    prevalence_dict[idEntity] = 1
        print("Entidades sin prevalencia: =============================")
        toPrint=""
        Ncount=0
        for idEntity, value in prevalence_dict.items():
            if value==0:
                toPrint+="%d, "%idEntity
                Ncount+=1
        print(toPrint)
        print("Numero de entidades sin prevalencia: %d"%Ncount)
        return prevalence_dict
    
    def checkDescriptionLevel(self):
        description_dict = {}
        SYMPTOM = self.id_dict['Symptom']
        for idEntity in self.details_dict:
            entityType = self.entity_dict[idEntity][1]
            if not entityType==SYMPTOM:
                continue
            if not idEntity in description_dict:
                description_dict[idEntity]  = 0
            names = self.details_dict[idEntity]
            if (names['Nivel'] == 0).any():
                description_dict[idEntity]  = 1
        print("Entidades sin descripcion de nivel 0: =================")
        toPrint=""
        Ncount=0
        for idEntity, value in description_dict.items():
            if value==0:
                toPrint+="%d, "%idEntity
                Ncount+=1
        print(toPrint)
        print("Numero de sintomas sin descripcion de nivel 0: %d"%Ncount)
        return description_dict
    
    def checkNumberOfEdges(self):
        print("Analisis de entidades aisladas: =============================")
        toPrint=""
        Ncount=0
        for idEntity in range(self.graph.getNodeMax()):
            node = self.graph.getNode(idEntity)
            if node is None:
                continue
            if (len(node.reachableDown)+len(node.reachableUp))==0:
                toPrint+="%d, "%idEntity
                Ncount+=1
        print(toPrint)
        print("Numero de entidades aisladas: %d"%Ncount)
        
    def checkEdgeMistakes(self):
        print("Analisis de enlaces mal formados: =============================")
        Ncount = 0
        for keyEdge in self.edge_dict:
            edge = self.edge_dict[keyEdge]
            edgeType = edge[2]
            edgeType1 = self.edge_type_dict[edgeType][0]
            edgeType2 = self.edge_type_dict[edgeType][1]
        
            idEntity1 = edge[0]
            idEntity2 = edge[1]
            entityType1 = self.entity_dict[idEntity1][1]
            entityType2 = self.entity_dict[idEntity2][1]
            ok=False
            if entityType1==edgeType1 and entityType2==edgeType2:
                ok=True
            if edgeType in self.list_bidirectional_relations and \
               entityType1==edgeType2 and entityType2==edgeType1:
               ok=True
            if not ok:
                print("%s (%d) -> %s (%d) [%s]"%(self.entity_dict[idEntity1][0],
                                                 idEntity1,
                                                 self.entity_dict[idEntity2][0],
                                                 idEntity2,
                                                 edge[3]))
                Ncount+=1
        print("Numero de relaciones mal formadas: %d"%Ncount)

    def checkNoUsar(self):
        print("Analisis de relaciones NO USAR: =============================")
        Ncount = 0
        for keyEdge in self.edge_dict:
            edge = self.edge_dict[keyEdge]
            if "NO USAR" in edge[3]:
                idEntity1 = edge[0]
                idEntity2 = edge[1]
                print("%s (%d) -> %s (%d) [%s]"%(self.entity_dict[idEntity1][0],
                                                 idEntity1,
                                                 self.entity_dict[idEntity2][0],
                                                 idEntity2,
                                                 edge[3]))
                Ncount+=1
        print("Numero de relaciones que no deben usarse: %d"%Ncount)
            
if __name__=="__main__":                                
    checker = Checker()
    #checker.checkRedundancy()
    checker.checkSpecialty()
    #checker.checkPrevalence()
    #checker.checkDescriptionLevel()
    #checker.checkNumberOfEdges()
    #checker.checkEdgeMistakes()
    #checker.checkNoUsar()
