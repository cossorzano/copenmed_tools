# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 12:38:31 2020

@author: coss
"""

import numpy as np
import os
import pandas as pd
import pickle
import sys
from copenmed_tools.python.copenmed_tools import COpenMedAlgorithm

class Reasoner0004(COpenMedAlgorithm):
    def __init__(self, fnPickle="", debug=False):
        COpenMedAlgorithm.__init__(self, "reasoning.txt", debug)

        if not os.path.exists("reasoning4.pkl"):
            self.constructGraph(fnPickle)
            self.read_reasoner_weights()
            self.construct_reference_score()
        
            obj = (self.entity_type_dict, self.entity_dict, 
                   self.edge_type_dict, self.edge_dict, 
                   self.entities, self.graph, self.w,
                   self.refCausas, self.refObservables)
            fh = open("reasoning4.pkl","wb")
            pickle.dump(obj,fh)
            fh.close()
        else:
            fh = open("reasoning4.pkl",'rb')
            (self.entity_type_dict, self.entity_dict, self.edge_type_dict, 
                   self.edge_dict, self.entities, self.graph, self.w,
                   self.refCausas, self.refObservables) = pickle.load(fh)
            fh.close()
        if self.debug:
            self.show_vector(self.refCausas)
            self.show_vector(self.refObservables)

        self.hechos = np.zeros(self.graph.getNodeMax()+1)
        self.Nhechos = 0

        self.score={}

    def read_reasoner_weights(self):
        def readSheet(sheet):
            retval_dict={}        
            df = pd.read_excel("reasonerCOSS_0004_clasifRelaciones.xlsx",
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
        self.w['especialidades'] = readSheet("ESPECIALIDAD")
        self.w['equipo'] = readSheet("EQUIPO")

    def construct_reference_score(self):
        # Collect all prevalences
        self.refCausas = np.zeros(self.graph.getNodeMax()+1)
        id_dict = self.graph.id_dict
        id_causes = [id_dict["Disease"],id_dict["Treatment"],
                     id_dict["GroupOfDiseases"],id_dict['Test'],
                     id_dict['GroupOfTreatments'],id_dict['Risk'],
                     id_dict['Substance'],id_dict['Pathogen'],
                     id_dict['Activity'],id_dict['Cause'],
                     id_dict['GroupOfTests'],
                     id_dict['GroupOfSubstances']]
        for idEntity in self.graph.graph:
            entityType = self.graph.getNodeType(idEntity)
            if entityType in id_causes:
                self.refCausas[idEntity] = self.graph.getNodePrevalence(idEntity,
                                            self.graph.avgPrevalence)
        self.score["causas"]=self.refCausas
        self.calculateObservables()
        self.refObservables=self.score['observables']

    def show_vector(self, score):
        idxSorted = np.abs(score).argsort()[::-1]
        for idEntity in idxSorted:
            if abs(score[idEntity])>0:
                msg = "%s (%d) -> %f"%(self.entity_dict[idEntity][0],
                                       idEntity, score[idEntity])
                if self.debug:
                    self.fhLog.write("%s\n"%msg)
                else:
                    print(msg)
        if self.debug:
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
    
    def calculateSimilarFacts(self, x):
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
        
    def calculateCauses(self, x=None):
        if x is None:
            x=self.hechos
        self.calculateSimilarFacts(x)
        if self.debug:
            self.fhLog.write("\nCalculando causas: ======== \n")
        self.score['causas'] = self.propagate(self.w['causas'],
                                              self.hechosSimilar)
        self.score['causas'] *= 1/np.max(self.score['causas'])
        
        # Moderate by prevalence
        self.score['causas'] = np.multiply(self.score['causas'],
                                           self.refCausas)

        # Keep facts as true causes (score=1), 
        # the other ones as likely causes (maxScore=0.5)
        self.score['causas'] *= 0.5/np.max(self.score['causas'])        
        self.score['causas'] = np.where(np.abs(x)>0,x,self.score['causas'])
        
        if self.debug:
            self.show_vector(self.score['causas'])

    def calculateBasic(self, message, wList, xList, addSimilar=False):
        """ Calculate causes first """
        if self.debug:
            self.fhLog.write("\nCalculando %s: ======== \n"%message)
        yFinal=None
        for w,x in zip(wList,xList):
            y=self.propagate(self.w[w], x)
            if addSimilar:
                y+=0.5*self.propagate(self.w[w],y)
            y*= 1.0/np.max(y)
            if yFinal is None:
                yFinal=np.copy(y)
            else:
                yFinal+=y
        self.score[message] = yFinal/np.max(yFinal)
        if self.debug:
            self.show_vector(self.score[message])

    def calculateTreatments(self):
        self.calculateBasic("tratamientos",
                            ["tratamientos","prevencion"],
                            [self.score['causas'],self.score['causas']])

    def calculateConsequences(self):
        self.calculateBasic("consecuencias",
                            ["consecuencias"],[self.score['causas']])

    def calculateSpecialty(self):
        self.calculateBasic("especialidades",
                            ["especialidades"],[self.score['causas']])

    def calculateEquipment(self):
        self.calculateBasic("equipo",
                            ["equipo"],[self.score['causas']])

    def calculateAttention(self):
        self.calculateBasic("atencion",
                            ["atencion","atencion"],
                            [self.score['causas'],self.score['tratamientos']])

    def calculateTests(self):
        self.calculateBasic("tests",
                            ["tests","tests"],
                            [self.score['causas'],self.score['observables']])

    def calculateObservables(self):
        self.calculateBasic("observables",
                            ["observables"],[self.score['causas']], True)

class Reasoner0004Viewer():
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
        id_dict = self.reasoner.graph.id_dict
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
        id_dict = self.reasoner.graph.id_dict
        score = self.reasoner.score
        print("POSSIBLE OBSERVATIONS --------------")
        self.printScore([id_dict["Symptom"],id_dict["Anatomy"],
                         id_dict['Population'], id_dict['TestResult']],
                        score['observables'])
        print(" ")

    def showRefObservables(self, Nmax=20):
        id_dict = self.reasoner.graph.id_dict
        print("POSSIBLE OBSERVATIONS --------------")
        groupList = [id_dict["Symptom"],id_dict["Anatomy"],
                     id_dict['Population'], id_dict['TestResult']]

        entities = self.reasoner.entities
        entities_this_type = []
        for idEntityType in groupList:
            entities_this_type+=entities[idEntityType]

        score = self.reasoner.refObservables
        idxSorted = score.argsort()[::-1]
        N=0
        for idEntity in idxSorted:
            if (idEntity in entities_this_type) and score[idEntity]>0:
                print("%s (%d) -> %f"%(self.reasoner.entity_dict[idEntity][0], 
                                       idEntity, score[idEntity]))
                N+=1
                if N==Nmax:
                    break
        print(" ")

    def showTests(self):
        reasoner.calculateTests()
        id_dict = self.reasoner.graph.id_dict
        score = self.reasoner.score
        print("POSSIBLE TESTS --------------")
        self.printScore([id_dict["Test"],id_dict["GroupOfTests"]],
                        score['tests'])
        print(" ")

    def showConsequences(self):
        reasoner.calculateConsequences()
        id_dict = self.reasoner.graph.id_dict
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
        id_dict = self.reasoner.graph.id_dict
        score = self.reasoner.score
        print("POSSIBLE TREATMENTS --------------")
        self.printScore([id_dict["Treatment"],id_dict["GroupOfTreatments"],
                         id_dict["Substance"],id_dict["GroupOfSubstances"],
                         id_dict["Activity"]],
                        score['tratamientos'])
        print(" ")

    def showAttention(self):
        reasoner.calculateAttention()
        id_dict = self.reasoner.graph.id_dict
        score = self.reasoner.score
        print("PAY ATTENTION TO --------------")
        self.printScore([id_dict["Treatment"],id_dict["GroupOfTreatments"],
                         id_dict["Test"],id_dict["GroupOfTests"],
                         id_dict["Disease"],id_dict["GroupOfDiseases"],
                         id_dict["Activity"],id_dict["Anatomy"],
                         id_dict["Symptom"],id_dict["Population"]],
                        score['tratamientos'])
        print(" ")

    def showSpecialties(self):
        reasoner.calculateSpecialty()
        id_dict = self.reasoner.graph.id_dict
        score = self.reasoner.score
        print("SPECIALTIES --------------")
        self.printScore([id_dict["Specialty"]],
                        score['especialidades'])
        print(" ")

    def showEquipment(self):
        reasoner.calculateEquipment()
        id_dict = self.reasoner.graph.id_dict
        score = self.reasoner.score
        print("EQUIPMENT --------------")
        self.printScore([id_dict["Instrument/Device"]],
                        score['equipo'])
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
    reasoner = Reasoner0004(sys.argv[1], debug=True)
    viewer = Reasoner0004Viewer(reasoner)
    viewer.showRefObservables()
    
    action = input("Elige tu siguiente accion (select, help, show):")
    
    while action!="":
        if action=="alergia":
            action="select 294 296 297 -101 713 -5171 -10863 -481 -871 -445 4242 -4504 -28 -5171 -3914"
        elif action=="vesicula":
            action="select 168 49 1135"
        elif action=="espalda":
            action="select 498 499 3345"
        elif action=="hinchazon":
            action="select 2689 832 4776 7486 7487"
        
        if action.startswith("select"):
            reasoner.newFacts(" ".join(action.split()[1:]))
        elif action=="show all":
            viewer.showCauses()
            viewer.showObservables()
            viewer.showTests()
            viewer.showConsequences()
            viewer.showTreatments()
            viewer.showAttention()
            viewer.showSpecialties()
            viewer.showEquipment()
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
        elif action=="show specialties":
            viewer.showSpecialties()
        elif action=="help":
            print("Actions:")
            print("   select <N>")
            print("   show all")
            print("   show causes")
            print("   show observables")
            print("   show tests")
            print("   show consequences")
            print("   show treatments")
            print("   show attention")
            print("   show specialties")
            print("   show facts")
            print("   help")
    
        action = input("Elige tu siguiente accion (select, help, show):")

# Path: hechos -> hechos (similar)
#       hechos -> causas
#       causas -> prevencion, observables, consecuencias, tratamientos, tests
#                 observables -> observables (similar)
#       tratamientos -> atencion