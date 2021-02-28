# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 12:38:31 2020

@author: coss
"""

import codecs
import numpy as np
import os
import pandas as pd
import pickle
import sys
from visor import load_database, Graph, \
                  separate_entities_by_type, \
                  add_directional_edges, COpenMedReasoner

class Reasoner0003(COpenMedReasoner):
    def __init__(self, fnPickle="", debug=False):
        fnIntermediate = os.path.join(os.getcwd(), "visor", "CopenMed_Reasoner", "reasoning3.pkl")
        if not os.path.exists(fnIntermediate):
            _, _, self.entity_type_dict, self.entity_type_dict_info, \
               self.entity_dict, self.entity_dict_info, \
               self.edge_type_dict, self.edge_type_dict_info, \
               list_bidirectional_relations, \
               self.edge_dict, self.edge_dict_info, _, _, _, _ = \
                   load_database(fnPickle)
            self.define_labels()
            self.entities = separate_entities_by_type(self.entity_type_dict, 
                                                      self.entity_dict)
            add_directional_edges(self.edge_dict, list_bidirectional_relations)
            
            self.graph = Graph(self.entity_dict, self.entity_type_dict, 
                               self.edge_dict, self.id_dict)
            self.graph.createPaths(2,0.25)
        
            self.read_reasoner_weights()
        
            obj = (self.entity_type_dict, self.entity_dict, 
                   self.edge_type_dict, self.edge_dict, self.id_dict, 
                   self.entities, self.graph, self.w)
            fh = open(fnIntermediate,"wb")
            pickle.dump(obj,fh)
            fh.close()
        else:
            fh = open(fnIntermediate,'rb')
            (self.entity_type_dict, self.entity_dict, self.edge_type_dict, 
                   self.edge_dict, self.id_dict, self.entities, 
                   self.graph, self.w) = pickle.load(fh)
            fh.close()

        self.hechos = np.zeros(self.graph.getNodeMax()+1)
        self.Nhechos = 0
        self.score={}
        self.debug = debug
        if debug:
            self.fhLog=codecs.open("reasoning.txt", 'w', encoding='utf8')
        else:
            self.fhLog=None
    
    def __del__(self):
        if self.debug:
            self.fhLog.close()

    def read_reasoner_weights(self):
        def readSheet(sheet):
            retval_dict={}        
            df = pd.read_excel("reasonerCOSS_0003_clasifRelaciones.xlsx",
                              sheet_name=sheet, engine="openpyxl")
            for index, row in df.iterrows():
                weights=np.asarray(row[-4:],dtype=float)
                if sum(np.isnan(weights))!=4:
                    weights[np.isnan(weights)]=0.0
                    retval_dict[row["IdTipoAsociacion"]]=weights
            return retval_dict
        self.w={}
        self.w['causas'] = readSheet("CAUSAS")
        self.w['observables'] = readSheet("OBSERVABLES")
        self.w['consecuencias'] = readSheet("CONSECUENCIAS")
        self.w['tratamientos'] = readSheet("TRATAMIENTOS")
        self.w['tests'] = readSheet("TESTS")
        self.w['prevencion'] = readSheet("PREVENCION")
        self.w['similar'] = readSheet("SIMILAR")
        self.w['atencion'] = readSheet("ATENCION")

    def define_labels(self):
        self.id_dict = {}
        for idEntityType in self.entity_type_dict:
            name, _, _ = self.entity_type_dict[idEntityType]
            self.id_dict[name]=idEntityType
        
        def find_edge(name):
            rightId = None
            for idEdgeType in self.edge_type_dict:
                edgeType = self.edge_type_dict[idEdgeType]
                edgeName = edgeType[3]
                if edgeName==name:
                    rightId = idEdgeType
            self.id_dict[name]=rightId
        find_edge("Disease causes Symptom")
        find_edge("Disease1 may evolve and coexist with Disease2")
        find_edge("Disease belongs to Group")
        find_edge("Symptom is associated to Disease")
        find_edge("Disease is observed in Anatomy")

    def show_vector(self, score):
        idxSorted = np.abs(score).argsort()[::-1]
        for idEntity in idxSorted:
            if abs(score[idEntity])>0:
                msg = "%s (%d) -> %f"%(self.entity_dict[idEntity][0],
                                       idEntity, score[idEntity])
                if not self.fhLog is None:
                    self.fhLog.write("%s\n"%msg)
        if not self.fhLog is None:
            self.fhLog.write("\n")

    def newFacts(self, idEntities):
        for idEntity in [int(token) for token in idEntities.split()]:
            if idEntity>0:
                present=1
                idAux = idEntity
            else:
                present=-1
                idAux=-idEntity
            self.hechos[idAux] = present
            self.Nhechos+=1
            print("  Selected:%d"%idAux)
            if self.debug:
                self.fhLog.write("Selected:%d\n\n"%idAux)
        
    def calculateCauses(self, x=None):
        if x is None:
            x=self.hechos
        if self.debug:
            self.fhLog.write("\nCalculando hechos similares: ======== \n")
        self.hechosSimilar = self.propagate(self.w['similar'],x)
        self.hechosSimilar *= 0.5/np.max(self.hechosSimilar)
        self.hechosSimilar = np.where(np.abs(self.hechosSimilar)>np.abs(self.hechos),
                                      self.hechosSimilar,self.hechos)
        self.hechosSimilar = np.where(np.abs(self.hechosSimilar)>1.0/(self.Nhechos+2),
                                      self.hechosSimilar,0.0)
        if self.debug:
            self.show_vector(self.hechosSimilar)

        if self.debug:
            self.fhLog.write("\nCalculando causas: ======== \n")
        self.score['causas'] = self.propagate(self.w['causas'],
                                              self.hechosSimilar)
        self.score['causas'] *= 0.5/np.max(self.score['causas'])
        self.score['causas'] = np.where(np.abs(x)>0,x,self.score['causas'])
        if self.debug:
            self.show_vector(self.score['causas'])

    def calculateObservables(self, x=None):
        """ Calculate causes first """
        if x is None:
            x=self.score['causas']
        if self.debug:
            self.fhLog.write("\nCalculando observables: ======== \n")
        self.score['observables'] = self.propagate(self.w['observables'], x)
        self.score['observables'] += 0.5*self.propagate(self.w['similar'],
                                                        self.score['observables'])
        self.score['observables'] *= 1.0/np.max(self.score['observables'])

    def calculateTests(self, x=None, mode='addObservables'):
        """ Calculate causes first """
        if x is None:
            x=self.score['causas']
        if self.debug:
            self.fhLog.write("\nCalculando tests: ======== \n")
        self.score['tests'] = self.propagate(self.w['tests'],x)
        self.score['tests'] *= 1.0/np.max(self.score['tests'])
        if mode=="addObservables":
            aux = self.propagate(self.w['tests'], self.score['observables'])
            aux *= 1.0/np.max(aux)
            self.score['tests'] += aux
        self.score['tests'] *= 1.0/np.max(self.score['tests'])            

    def calculateConsequences(self, x=None):
        """ Calculate causes first """
        if x is None:
            x=self.score['causas']
        if self.debug:
            self.fhLog.write("\nCalculando consecuencias: ======== \n")
        self.score['consecuencias'] = self.propagate(self.w['consecuencias'], x)
        self.score['consecuencias'] *= 1.0/np.max(self.score['consecuencias'])

    def calculateTreatments(self, x=None):
        """ Calculate causes first """
        if x is None:
            x=self.score['causas']
        if self.debug:
            self.fhLog.write("\nCalculando tratamientos: ======== \n")
        self.score['tratamientos'] = self.propagate(self.w['tratamientos'], x)
        self.score['tratamientos'] *= 1.0/np.max(self.score['tratamientos'])
        aux = self.propagate(self.w['prevencion'], x)
        aux *= 1.0/np.max(aux)
        self.score['tratamientos'] += aux
        self.score['tratamientos'] *= 1.0/np.max(self.score['tratamientos'])            

    def calculateAttention(self, x=None):
        """ Calculate causes and treatments first """
        if x is None:
            x=self.score['causas']
        if self.debug:
            self.fhLog.write("\nCalculando atencion: ======== \n")
        self.score['atencion'] = self.propagate(self.w['atencion'], x)
        self.score['atencion'] *= 1.0/np.max(self.score['atencion'])
        aux = self.propagate(self.w['atencion'], self.score['tratamientos'])
        aux *= 1.0/np.max(aux)
        self.score['atencion'] += aux
        self.score['atencion'] *= 1.0/np.max(self.score['atencion'])            

    def propagateDown(self, weight, scoreIn, tol=1e-4):
        scoreOut=np.zeros(scoreIn.shape[0])
        for idEntity in range(scoreIn.shape[0]):
            x = scoreIn[idEntity]
            if abs(x)<tol:
                continue
            node = self.graph.getNode(idEntity)
            if self.fhLog is not None:
                self.fhLog.write("\nSpreading %s(%d) scoreIn=%f\n\n"%(node.entityName,
                                                                      idEntity, x))
    
            # For all outgoing edges
            for idEntityTo in node.reachableDown:
                toSum = 0.0
                for path in node.reachableDown[idEntityTo]:
                    xInter=x
                    for iPath in range(len(path.path)):
                        _, idEntityToInter, idEdgeType, edgeStrength = path.path[iPath]
                        if idEdgeType is None: # Terminal node
                            break
                        if not idEdgeType in weight: # The relation cannot be processed by this weight
                            xInter=0
                            break
                        weightRow = weight[idEdgeType]
                        if xInter>0:
                            wDown = weightRow[0]
                        else:
                            wDown = weightRow[1]
                        xInter=abs(xInter)*wDown*edgeStrength
                    if abs(xInter)>abs(toSum):
                        toSum=xInter
                        if self.fhLog is not None:
                            self.fhLog.write(path.pretty(self.entity_dict,
                                                         self.edge_type_dict))
                            self.fhLog.write("Updating %s (%d) with %f\n"%\
                                  (self.graph.getNode(idEntityTo).entityName,
                                   idEntityTo, xInter))
                if abs(toSum)>0:
                    scoreOut[idEntityTo]+=toSum
                    if self.fhLog is not None:
                        self.fhLog.write("\nNew score %s (%d)= %f\n"%\
                              (self.graph.getNode(idEntityTo).entityName,
                               idEntityTo, scoreOut[idEntityTo]))
        return scoreOut

    def propagateUp(self, weight, scoreIn, tol=1e-4):
        scoreOut=np.zeros(scoreIn.shape[0])
        for idEntity in range(scoreIn.shape[0]):
            x = scoreIn[idEntity]
            if abs(x)<tol:
                continue
            node = self.graph.getNode(idEntity)
            if self.fhLog is not None:
                self.fhLog.write("\nSpreading %s(%d) scoreIn=%f\n\n"%(node.entityName,
                                                                      idEntity, x))

            # For all incoming edges
            for idEntityFrom in node.reachableUp:
                toSum = 0.0
                for path in node.reachableUp[idEntityFrom]:
                    xInter=x
                    for iPath in reversed(range(len(path.path)-1)):
                        _, idEntityFromInter, idEdgeType, edgeStrength = path.path[iPath]
                        if not idEdgeType in weight: # The relation cannot be processed by this weight
                            xInter=0
                            break
                        weightRow = weight[idEdgeType]
                        if xInter>0:
                            wUp = weightRow[2]
                        else:
                            wUp = weightRow[3]
                        xInter=abs(xInter)*wUp*edgeStrength
                    if abs(xInter)>abs(toSum):
                        toSum=xInter
                        if self.fhLog is not None:
                            self.fhLog.write(path.pretty(self.entity_dict,
                                                         self.edge_type_dict))
                            self.fhLog.write("Updating %s (%d) with %f\n"%\
                                  (self.graph.getNode(idEntityFrom).entityName,
                                   idEntityFrom, xInter))
    
                if abs(toSum)>0:
                    scoreOut[idEntityFrom]+=toSum
                    if self.fhLog is not None:
                        self.fhLog.write("\nNew score %s (%d)= %f\n"%\
                              (self.graph.getNode(idEntityFrom).entityName,
                               idEntityFrom, scoreOut[idEntityFrom]))
        return scoreOut
    

    def propagate(self, weight, scoreIn):
        tol=1e-4
        return self.propagateDown(weight, scoreIn, tol)+\
               self.propagateUp(weight, scoreIn, tol)

class Reasoner0003Viewer():
    def __init__(self, reasoner):
        self.reasoner = reasoner
        self.combine = False

    def printScore(self, groupList, score):
        def printList(Nmax, score):
            N=0
            for idx in idxSorted:
                idEntity = entities_this_type[idx]
                if hechos[idEntity]==0 and score[idEntity]>0:
                    print("%s (%d) -> %f"%(self.reasoner.entity_dict[idEntity][0], 
                                           idEntity, score[idEntity]))
                    N+=1
                    if N==Nmax:
                        break
            print(" ")
        
        entities = self.reasoner.entities
        entity_type_dict = self.reasoner.entity_type_dict
        hechos = self.reasoner.hechos
        hechosSimilar = self.reasoner.hechosSimilar
        if self.combine:
            entities_this_type = []
            for idEntityType in groupList:
                entities_this_type+=entities[idEntityType]

            similar_this_type = hechosSimilar[entities_this_type]
            idxSorted = similar_this_type.argsort()[::-1]
            printList(3, hechosSimilar)

            scores_this_type = score[entities_this_type]
            idxSorted = scores_this_type.argsort()[::-1]
            printList(20, score)
        else:
            for idEntityType in groupList:
                print(entity_type_dict[idEntityType][0].upper())
                
                entities_this_type = entities[idEntityType]

                similar_this_type = hechosSimilar[entities_this_type]
                idxSorted = similar_this_type.argsort()[::-1]
                printList(3, hechosSimilar)

                scores_this_type = score[entities_this_type]
                idxSorted = scores_this_type.argsort()[::-1]
                printList(20, score)
    
    def showCauses(self):
        reasoner.calculateCauses()
        id_dict = self.reasoner.id_dict
        score = self.reasoner.score
        print("POSSIBLE CAUSES --------------------")
        self.printScore([id_dict["Disease"],id_dict["Treatment"],
                        id_dict["GroupOfDiseases"],id_dict['Test'],
                        id_dict['GroupOfTreatments'],id_dict['Risk'],
                        id_dict['Substance'],id_dict['Pathogen'],
                        id_dict['Activity'],id_dict['Cause'],
                        id_dict['GroupOfTests'],
                        id_dict['GroupOfSubstances']], score['causas'])

    def showObservables(self):
        reasoner.calculateObservables()
        id_dict = self.reasoner.id_dict
        score = self.reasoner.score
        print("POSSIBLE OBSERVATIONS --------------")
        self.printScore([id_dict["Symptom"],id_dict["Anatomy"],
                         id_dict['Population'], id_dict['TestResult']],
                        score['observables'])
        print(" ")

    def showTests(self):
        reasoner.calculateTests()
        id_dict = self.reasoner.id_dict
        score = self.reasoner.score
        print("POSSIBLE TESTS --------------")
        self.printScore([id_dict["Test"],id_dict["GroupOfTests"]],
                        score['tests'])
        print(" ")

    def showConsequences(self):
        reasoner.calculateConsequences()
        id_dict = self.reasoner.id_dict
        score = self.reasoner.score
        print("POSSIBLE CONSEQUENCES --------------")
        self.printScore([id_dict["Disease"],id_dict["GroupOfDiseases"],
                         id_dict["Symptom"],id_dict["Activity"],
                         id_dict["Pathogen"],id_dict["Cause"],
                         id_dict["Risk"],id_dict["Function"]],
                        score['consecuencias'])
        print(" ")

    def showTreatments(self):
        reasoner.calculateTreatments()
        id_dict = self.reasoner.id_dict
        score = self.reasoner.score
        print("POSSIBLE TREATMENTS --------------")
        self.printScore([id_dict["Treatment"],id_dict["GroupOfTreatments"],
                         id_dict["Substance"],id_dict["GroupOfSubstances"],
                         id_dict["Activity"]],
                        score['tratamientos'])
        print(" ")

    def showAttention(self):
        reasoner.calculateAttention()
        id_dict = self.reasoner.id_dict
        score = self.reasoner.score
        print("PAY ATTENTION TO --------------")
        self.printScore([id_dict["Treatment"],id_dict["GroupOfTreatments"],
                         id_dict["Test"],id_dict["GroupOfTests"],
                         id_dict["Disease"],id_dict["GroupOfDiseases"],
                         id_dict["Activity"],id_dict["Anatomy"],
                         id_dict["Symptom"],id_dict["Population"]],
                        score['tratamientos'])
        print(" ")

    def showFacts(self):
        entity_dict = self.reasoner.entity_dict
        hechos = self.reasoner.hechos
        print("KNOWN FACTS ------------------------")
        for idEntity in range(hechos.shape[0]):
            if hechos[idEntity]!=0:
                print("%s (%d) = %f"%(entity_dict[idEntity][0],idEntity,
                                      hechos[idEntity]))

if __name__=="__main__":
    reasoner = Reasoner0003(sys.argv[1])
    viewer = Reasoner0003Viewer(reasoner)
    
    action = input("Elige tu siguiente accion (select, help, show):")
    
    while action!="":
        if action=="alergia":
            action="select 294 296 297 -101 713 -481 -871 -445 4242 -4504 -28 -5171 -3914"
        
        if action.startswith("select"):
            reasoner.newFacts(" ".join(action.split()[1:]))
        elif action=="show all":
            viewer.showCauses()
            viewer.showObservables()
            viewer.showTests()
            viewer.showConsequences()
            viewer.showFacts()
        elif action=="show causes":
            viewer.showCauses()
        elif action=="show observables":
            viewer.showObservables()
        elif action=="show tests":
            viewer.showTests()
        elif action=="show consequences":
            viewer.showConsequences()
        elif action=="show treatments":
            viewer.showTreatments()
        elif action=="show attention":
            viewer.showAttention()
        elif action=="show facts":
            viewer.showFacts()
        elif action=="help":
            print("Actions:")
            print("   select <N>")
            print("   show all")
            print("   show causes")
            print("   show observables")
            print("   show facts")
            print("   help")
    
        action = input("Elige tu siguiente accion (select, help, show):")
