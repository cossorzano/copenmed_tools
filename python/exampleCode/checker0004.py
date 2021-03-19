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

    def checkRedundancy(self, weightThreshold=0.9):
        nonRedundant1 = [4,   # Anatomy1 is related to Anatomy2
                         6,   # Treatment1 enhances the effect of Treatment2
                         8,   # Disease1 is similar to Disease2
                         9,   # Disease1 may evolve to Disease2
                         10,  # Disease is observed in Anatomy
                         17,  # Symptom1 is similar to Symptom2
                         18,  # Symptom1 cannot be seen with Symptom2
                         19,  # Symptom1 implies Symptom2
                         20,  # Symptom1 may evolve and coexist with Symptom2
                         22,  # Disease1 may evolve and coexist with Disease2
                         29,  # Symptom can never be observed in Disease
                         30,  # Disease is diagnosed with this Test
                         31,  # Disease can be treated with Treatment
                         32,  # Disease can be treated with this Group
                         46,  # Risk is associated to Disease
                         49,  # Substance can cause Disease
                         51,  # Substance can cause Symptom
                         56,  # Pathogen causes disease
                         57,  # Pathogen does not cause Disease
                         60,  # Activity may cause Symptom
                         62,  # Cause may cause Disease
                         63,  # Cause may cause Symptom
                         64,  # Activity1 is similar to Activity2
                         65,  # Substance1 is similar to Substance2
                         66,  # Symptom can be treated with Treatment
                         67,  # Symptom can be treated with Group
                         73,  # A positive testResult implies Symptom
                         79,  # Cause can cause this Group
                         83,  # Symptom is characterized by TestResult
                         84,  # Group may cause symptom
                         86,  # Test is useful to diagnose this Group
                         93,  # Disease may evolve and coexist with Group
                         94,  # Group1 may evolve and cause Group2
                         101, # Group may evolve to Disease
                         104, # Treatment may cause Group
                         108, # Treatment1 is precursor of Treatment2
                         125, # Group belongs to the domain of Specialty
                         128, # Treatment1 is similar to Treatment2
                         129, # Group can be treated with Treatment 
                         133, # Test1 is similar to Test2
                         134, # Anatomy may cause Symptom
                         144, # Group is produced by Anatomy
                         147, # Treatment is related to substance
                         154, # Test is used in Anatomy
                         157, # Cause1 is similar to Cause2
                         158, # Symptom may evolve to Disease
                         163, # Disease may evolve to Group
                         164, # Substance is related to Disease
                         174, # Pathogen can cause Group
                         176, # Treatment is applied in Anatomy
                         179, # Disease causes Symptom
                         181, # Substance increases this Function
                         183, # Symptom increases Substance
                         190, # If Function1 decreases, Function2 increases
                         209, # Treatment prevents Disease
                         214, # Symptom is related to Anatomy
                         215, # Treatment should be avoided if Disease is present
                         216, # Treatment should be avoided if Group is present
                         221, # Disease is treated by Activity
                         224, # Treatment1 can be complemented with Treatment2
                         232, # Disease1 should be prevented from evolving to Disease2
                         236, # Disease1 may cause Disease2 to get worse
                         238, # Group may cause Disease to get worse
                         241, # Group of treatments may cause Group of diseases
                         247, # Cause promotes Pathogen
                         251, # Group may evolve and coexist with Disease
                         259, # Symptom is related to Activity
                         263, # Treatment is used in Test
                         266, # Cause may require Test
                         272, # Group1 is similar to Group2
                         289, # Cause can be treated with Treatment
                         290, # Cause can be treated by Group
                         291, # Disease1 is seen with Disease2
                         292, # Disease is seen with Group
                         293, # Group is seen with Disease
                         298, # Substance is related to Cause
                         305, # Activity involves Anatomy
                         315, # Disease is related to Substance
                         316, # Substance is related to Anatomy
                         324, # Diseases affects Anatomy
                         334, # Group implies TestResult
                         339, # Disease seldom causes Symptom
                         344, # Treatment prevents Activity
                         347, # Pathogen1 transmits or promotes Pathogen2
                         351, # Treatment can be used against Pathogen 
                         374, # Pathogen gives TestResult
                         ]
        nonRedundant2 = [4,   # Anatomy1 is related to Anatomy2
                         6,   # Treatment1 enhances the effect of Treatment2
                         8,   # Disease1 is similar to Disease2
                         16,  # Disease is in the domain of Specialty 
                         17,  # Symptom1 is similar to Symptom2
                         18,  # Symptom1 cannot be seen with Symptom2
                         19,  # Symptom1 implies Symptom2
                         20,  # Symptom1 may evolve and coexist with Symptom2
                         29,  # Symptom can never be observed in Disease
                         31,  # Disease can be treated with Treatment
                         32,  # Disease can be treated with this Group
                         45,  # Result is measured with Test
                         56,  # Pathogen causes disease
                         57,  # Pathogen does not cause Disease
                         60,  # Activity may cause Symptom
                         63,  # Cause may cause Symptom
                         64,  # Activity1 is similar to Activity2
                         65,  # Substance1 is similar to Substance2
                         66,  # Symptom can be treated with Treatment
                         67,  # Symptom can be treated with Group
                         78,  # GroupOfDiseases can be treated with GroupOfTreatments
                         79,  # Cause can cause this Group
                         84,  # Group may cause symptom
                         94,  # Group1 may evolve and cause Group2
                         96,  # Activity may prevent Group
                         101, # Group may evolve to Disease
                         104, # Treatment may cause Group
                         117, # Symptom requires Test
                         125, # Group belongs to the domain of Specialty
                         126, # Disease is more observed in Population
                         127, # Disease is less observed in Population
                         128, # Treatment1 is similar to Treatment2
                         129, # Group can be treated with Treatment
                         131, # Group can be observed in Anatomy
                         133, # Test1 is similar to Test2
                         134, # Anatomy may cause Symptom
                         144, # Group is produced by Anatomy
                         147, # Treatment is related to substance
                         148, # Group can be diagnosed with Test
                         154, # Test is used in Anatomy
                         157, # Cause1 is similar to Cause2
                         174, # Pathogen can cause Group
                         176, # Treatment is applied in Anatomy
                         177, # Treatment1 is a subtype of Treatment2
                         183, # Symptom increases Substance
                         185, # Function is performed by Anatomy
                         186, # Function increase causes Symptom
                         209, # Treatment prevents Disease
                         214, # Symptom is related to Anatomy
                         215, # Treatment should be avoided if Disease is present
                         219, # Group should be avoided if Treatment is given
                         224, # Treatment1 can be complemented with Treatment2
                         232, # Disease1 should be prevented from evolving to Disease2
                         234, # Group should be prevented from evolving to Disease
                         236, # Disease1 may cause Disease2 to get worse
                         247, # Cause promotes Pathogen
                         259, # Symptom is related to Activity
                         266, # Cause may require Test
                         272, # Group1 is similar to Group2
                         289, # Cause can be treated with Treatment
                         290, # Cause can be treated by Group
                         291, # Disease is related to Substance
                         292, # Disease is seen with Group
                         293, # Group is seen with Disease
                         299, # Group is more observed in Population
                         305, # Activity involves Anatomy
                         315, # Disease is related to Substance
                         316, # Substance is related to Anatomy
                         339, # Disease seldom causes Symptom
                         344, # Treatment prevents Activity
                         347, # Pathogen1 transmits or promotes Pathogen2
                         351, # Treatment can be used against Pathogen 
                         374, # Pathogen gives TestResult
                         ]
        whiteList = [(11,   # Disease can only be observed in Anatomy
                      77,   # Disease belongs to Group
                      131), # Group can be observed in Anatomy
                     (14,   # Disease can only be seen in Population
                      324,  # Diseases affects Anatomy
                      213   # Anatomy can only be seen in Population
                      ),
                     (16,   # Disease is in the domain of Specialty
                      77,   # Disease belongs to Group
                      125), # Group belongs to the domain of Specialty
                     (25,   # Symptom can only be observed in Anatomy
                      178,  # Symptom1 is a subtype of Symptom2
                      24),  # Symptom can be observed in Anatomy
                     (56,   # Pathogen causes disease
                      56,
                      47),  # Disease1 is a subtype of Disease2
                     (66,   # Symptom can be treated with Treatment
                      66,
                      5),   # Treatment belongs to the GroupOfTreatments
                     (67,   # Symptom can be treated with Group
                      66,   # Symptom can be treated with Treatment
                      5),   # Treatment belongs to the GroupOfTreatments
                     (131,  # Group can be observed in Anatomy
                      131,
                      3),   # Anatomy1 is part of Anatomy2
                     (154,  # Test is used in Anatomy
                      116,  # Test belongs to Group
                      341), # Group is used in Anatomy
                     (192,  # Treatment has effect on Anatomy
                      5,    # Treatment belongs to the GroupOfTreatments
                      204), # Group has effect on Anatomy
                     (192,  # Treatment has effect on Anatomy
                      192,  
                      3),   # Anatomy1 is part of Anatomy2
                     (269,  # Pathogen is more observed in Population
                      56,   # Pathogen causes disease
                      126), # Disease is more observed in Population
                     (324,  # Diseases affects Anatomy
                      324,
                      3),   # Anatomy1 is part of Anatomy2
                     ]
        blackList = [(3,    # Anatomy1 is part of Anatomy2
                      3,
                      3),
                     (4,    # Anatomy1 is related to Anatomy2
                      3,    # Anatomy1 is part of Anatomy2
                      3),
                     (5,    # Treatment belongs to the GroupOfTreatments
                      5,
                      74),  # Group1 is a subgroup of Group2
                     (5,    # Treatment belongs to the GroupOfTreatments
                      177,  # Treatment1 is a subtype of Treatment2
                      5),
                     (10,   # Disease is observed in Anatomy
                      11,   # Disease can only be observed in Anatomy
                      3),   # Anatomy1 is part of Anatomy2
                     (10,   # Disease is observed in Anatomy
                      47,   # Disease1 is a subtype of Disease2
                      10),
                     (10,   # Disease is observed in Anatomy
                      77,   # Disease belongs to Group
                      130), # Group can only be observed in Anatomy
                     (10,   # Disease is observed in Anatomy
                      77,   # Disease belongs to Group
                      325), # Group affects Anatomy
                     (11,   # Disease can only be observed in Anatomy
                      11,   
                      3),   # Anatomy1 is part of Anatomy2
                     (11,   # Disease can only be observed in Anatomy
                      47,   # Disease1 is a subtype of Disease2
                      10),  # Disease is observed in Anatomy
                     (11,   # Disease can only be observed in Anatomy
                      47,   # Disease1 is a subtype of Disease2
                      11),  
                     (11,   # Disease can only be observed in Anatomy
                      77,   # Disease belongs to Group,
                      130), # Group can only be observed in Anatomy
                     (13,   # Disease can be seen in Population
                      11,   # Disease can only be observed in Anatomy
                      213), # Anatomy can only be seen in Population
                     (13,   # Disease can be seen in Population
                      47,   # Disease1 is a subtype of Disease2
                      14),  # Disease can only be seen in Population
                     (14,   # Disease can only be seen in Population
                      11,   # Disease can only be observed in Anatomy
                      213), # Anatomy can only be seen in Population
                     (14,   # Disease can only be seen in Population
                      77,   # Disease belongs to Group
                      260), # Group can only be observed in Population
                     (24,   # Symptom can be observed in Anatomy
                      24,
                      3),   # Anatomy1 is part of Anatomy2
                     (24,   # Symptom can be observed in Anatomy
                      25,   # Symptom can only be observed in Anatomy
                      3),   # Anatomy1 is part of Anatomy2
                     (24,   # Symptom can be observed in Anatomy
                      178,  # Symptom1 is a subtype of Symptom2
                      24),
                     (24,   # Symptom can be observed in Anatomy
                      178,  # Symptom1 is a subtype of Symptom2
                      25),  # Symptom can only be observed in Anatomy
                     (25,   # Symptom can only be observed in Anatomy
                      24,   # Symptom can be observed in Anatomy
                      3),   # Anatomy1 is part of Anatomy2
                     (25,   # Symptom can only be observed in Anatomy
                      25,
                      3),   # Anatomy1 is part of Anatomy2
                     (30,   # Disease is diagnosed with this Test
                      47,   # Disease1 is a subtype of Disease2
                      30),
                     (47,   # Disease1 is a subtype of Disease2
                      77,   # Disease belongs to Group
                      257), # Group is a subtype of Disease
                     (47,   # Disease1 is a subtype of Disease2
                      47,
                      47),
                     (47,   # Disease1 is a subtype of Disease2
                      47,
                      77),  # Disease belongs to Group
                     (66,   # Symptom can be treated with Treatment
                      97,   # Symptom is also a Group of diseases
                      129), # Group can be treated with Treatment
                     (74,   # Group1 is a subgroup of Group2
                      74,
                      74),
                     (76,   # Group1 is a subgroup of Group2
                      76,
                      74),  # Group1 is a subgroup of Group2
                     (76,   # Group1 is a subgroup of Group2
                      76,
                      76),
                     (76,   # Group1 is a subgroup of Group2
                      257,  # Group is a subtype of Disease
                      77),  # Disease belongs to Group
                     (77,   # Disease belongs to Group
                      47,   # Disease1 is a subtype of Disease2
                      77),
                     (77,   # Disease belongs to Group
                      77, 
                      74),  # Group1 is a subgroup of Group2
                     (77,   # Disease belongs to Group
                      77, 
                      76),  # Group1 is a subgroup of Group2
                     (77,   # Disease belongs to Group
                      77, 
                      77),
                     (100,  # Pathogen1 is a subtype of Pathogen2
                      100,
                      100),
                     (118,  # Symptom requires Group
                      117,  # Symptom requires Test
                      116), # Test belongs to Group
                     (124,  # Test can measure Substance
                      342,  # Test1 is a subtype of Test2
                      124),
                     (130,  # Group can only be observed in Anatomy
                      76,   # Group1 is a subgroup of Group2
                      130),
                     (130,  # Group can only be observed in Anatomy
                      130,
                      3),   # Anatomy1 is part of Anatomy2
                     (130,  # Group can only be observed in Anatomy
                      131,  # Group can be observed in Anatomy 
                      3),   # Anatomy1 is part of Anatomy2
                     (131,  # Group can be observed in Anatomy
                      76,   # Group1 is a subgroup of Group2
                      130), # Group can only be observed in Anatomy
                     (131,  # Group can be observed in Anatomy
                      325,  # Group affects Anatomy
                      3),   # Anatomy1 is part of Anatomy2
                     (135,  # Substance is in this group of substances
                      135,
                      143), # Group1 is part of Group2
                     (136,  # Treatment is in this group of substances
                      136,
                      143), # Group1 is part of Group2
                     (143,  # Group1 is part of Group2
                      170,  # Group of substances is part of the group of treatments
                      137), # The group of treatments is in the group of substances
                     (150,  # Symptom is observed in Population
                      25,   # Symptom can only be observed in Anatomy
                      213), # Anatomy can only be seen in Population
                     (160,  # Substance is produced by Anatomy
                      135,  # Substance is in this group of substances
                      144), # Group is produced by Anatomy
                     (160,  # Substance is produced by Anatomy
                      160,  # Substance is produced by Anatomy
                      3),   # Anatomy1 is part of Anatomy2
                     (169,  # Substance is included in Group
                      169,
                      74),  # Group1 is a subgroup of Group2
                     (178,  # Symptom1 is a subtype of Symptom2
                      178,
                      178),
                     (179,  # Disease causes Symptom
                      47,   # Disease1 is a subtype of Disease2
                      179),
                     (195,  # Treatment is produced by Anatomy
                      136,  # Treatment is in this group of substances
                      144), # Group is produced by Anatomy
                     (200,  # Population1 is a subgroup of Population2
                      200,
                      200),
                     (204,  # Group has effect on Anatomy
                      74,   # Group1 is a subgroup of Group2
                      204),
                     (212,  # Symptom can only be observed in Population
                      24,   # Symptom can be observed in Anatomy
                      213), # Anatomy can only be seen in Population
                     (212,  # Symptom can only be observed in Population
                      25,   # Symptom can only be observed in Anatomy
                      213), # Anatomy can only be seen in Population
                     (213,  # Anatomy can only be seen in Population
                      3,    # Anatomy1 is part of Anatomy2
                      213),
                     (246,  # Cause1 is a subtype of Cause2
                      246,
                      246),
                     (271,  # Cause occurs in Anatomy
                      271,
                      3),   # Anatomy1 is part of Anatomy2
                     (324,  # Diseases affects Anatomy
                      77,   # Disease belongs to Group
                      131), # Group can be observed in Anatomy
                     (324,  # Diseases affects Anatomy
                      77,   # Disease belongs to Group
                      130), # Group can only be observed in Anatomy
                     (324,  # Diseases affects Anatomy
                      47,   # Disease1 is a subtype of Disease2
                      10),  # Disease is observed in Anatomy
                     (325,  # Group affects Anatomy
                      76,   # Group1 is a subgroup of Group2
                      130), # Group can only be observed in Anatomy
                     (334,  # Group implies TestResult
                      334,
                      365), # Result1 is a subtype of Result2
                     (334,  # Group implies TestResult
                      76,   # Group1 is a subgroup of Group2
                      334), 
                     (355,  # Pathogen can be confirmed with Test
                      100,  # Pathogen1 is a subtype of Pathogen2
                      355),
                     (375,  # Pathogen affects Anatomy
                      100,  # Pathogen1 is a subtype of Pathogen2
                      375)
                     ]
        
        print("Analisis de enlaces redundantes: =============================")
        count = 0
        for idEntity in range(self.graph.getNodeMax()):
            node = self.graph.getNode(idEntity)
            if node is None:
                continue
    
            # For all outgoing edges
            for idEntityTo in node.reachableDown:
                maxWeight1=0.0
                directPathsTypes = []
                directPaths = []
                for path in node.reachableDown[idEntityTo]:
                    if len(path.path)==2:
                        maxWeight1=max(maxWeight1,path.getLastWeight()[-1])
                        edgeType = path.getEdgeTypes()[0]
                        directPathsTypes.append(edgeType)
                        directPaths.append(path)
                if maxWeight1>weightThreshold:
                    directPathShown = False
                    for path in node.reachableDown[idEntityTo]:
                        if len(path.path)>2 and \
                            path.getLastWeight()[-1]>weightThreshold:
                            pathTypes = path.getEdgeTypes()
                            if pathTypes[0] in nonRedundant1 or \
                               pathTypes[1] in nonRedundant2:
                                continue
                            redundant=0
                            prefix="Posible "
                            for directType in directPathsTypes:
                                triplet = tuple([directType]+pathTypes)
                                if triplet in whiteList:
                                    redundant=-1
                                    break
                                elif triplet in blackList:
                                    redundant=1
                                    prefix=""
                            if redundant<0:
                                continue
                            if not directPathShown:
                                print("Enlaces directos:")
                                for directPath in directPaths:
                                    print(directPath.pretty(self.entity_dict,self.edge_type_dict))
                                directPathShown = True
                            print("%s path redundante entre %d %d: %s"%\
                                  (prefix,idEntity,idEntityTo,
                                   path.pretty(self.entity_dict, 
                                               self.edge_type_dict)))
                            count+=1
        print("Count of redundancies=%d"%count)

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
    checker.checkRedundancy()
    checker.checkSpecialty()
    checker.checkPrevalence()
    checker.checkDescriptionLevel()
    checker.checkNumberOfEdges()
    checker.checkEdgeMistakes()
    checker.checkNoUsar()
