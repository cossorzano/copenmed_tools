# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 18:18:53 2021

@author: coss
"""

import numpy as np
from copenmed_tools.python.copenmed_tools import *
from reasonerCOSS_0003 import Reasoner0003

class Summarizer():
    def __init__(self, reasoner):
        fnPickle = 'copenmed.pkl'
        _, _, self.entity_type_dict, _, self.entity_dict, _, \
            self.edge_type_dict, _, _, self.edge_dict, _, self.details_dict, \
                _, self.resources_dict, _ = load_database(fnPickle)
        self.reasoner = reasoner
        self.causesTypes = [self.reasoner.id_dict["Disease"],
                            self.reasoner.id_dict["Treatment"],
                            self.reasoner.id_dict["GroupOfDiseases"],
                            self.reasoner.id_dict['Test'],
                            self.reasoner.id_dict['GroupOfTreatments'],
                            self.reasoner.id_dict['Risk'],
                            self.reasoner.id_dict['Substance'],
                            self.reasoner.id_dict['Pathogen'],
                            self.reasoner.id_dict['Activity'],
                            self.reasoner.id_dict['Symptom'],
                            self.reasoner.id_dict['Cause'],
                            self.reasoner.id_dict['GroupOfTests'],
                            self.reasoner.id_dict['GroupOfSubstances']]
        self.treatmentTypes = [self.reasoner.id_dict["Treatment"],
                               self.reasoner.id_dict["GroupOfTreatments"],
                               self.reasoner.id_dict["Substance"],
                               self.reasoner.id_dict["GroupOfSubstances"],
                               self.reasoner.id_dict["Activity"]]
        self.diseaseTypes = [self.reasoner.id_dict["Disease"],
                            self.reasoner.id_dict["GroupOfDiseases"],
                            self.reasoner.id_dict['Pathogen'],
                            self.reasoner.id_dict['Activity'],
                            self.reasoner.id_dict['Cause'],
                            self.reasoner.id_dict['Symptom']]
        self.testTypes = [self.reasoner.id_dict["Test"],
                          self.reasoner.id_dict["GroupOfTests"],
                          self.reasoner.id_dict["TestResult"]]
    
    def addResources(self, idEntity):
        retval=""
        if idEntity in self.resources_dict:
            for i,row in self.resources_dict[idEntity].iterrows():
                retval+="    "+row.URL+"\n"
        if retval!="":
            retval="\n  Recursos:\n"+retval
        return retval
    
    def addSynonyms(self, idEntity, mainName):
        retval=""
        i=0
        for _,row in self.details_dict[idEntity].iterrows():
            if i>0:
                retval+=", "
            if row.Entidad!=mainName:
                retval+=row.Entidad+"\n"
                i+=1
        if retval!="":
            return "  Tambien conocido como: "+retval
        else:
            return ""
    
    def getDelta(self, idEntity):
        x = np.zeros(self.reasoner.graph.getNodeMax()+1)
        x[idEntity]=1
        return x
    
    def printList(self, y, idEntity, sameType=0, threshold=0.1, validTypes=None):
        if np.max(y)>0:
            y = y/np.max(y)
        idxSorted = y.argsort()[::-1]
        retval=""
        for idx in idxSorted:
            if y[idx]>threshold and idx!=idEntity:
                show = False
                if validTypes is not None:
                    if self.entity_dict[idx][1] in validTypes:
                        show = True
                elif sameType==0:
                    show = True
                elif sameType==1 and \
                     self.entity_dict[idEntity][1]==self.entity_dict[idx][1]:
                    show = True
                elif sameType==-1 and \
                    self.entity_dict[idEntity][1]!=self.entity_dict[idx][1]:
                    show = True
                           
                if show:
                    if sameType==1:
                        retval+="    %s (%d, %f)\n"%(self.entity_dict[idx][0], idx,
                                                   y[idx])
                    else:
                        retval+="    %s (%d, %s, %f)\n"%(self.entity_dict[idx][0], idx, 
                                                   self.entity_dict[idx][2],
                                                   y[idx])
                    node = self.reasoner.graph.getNode(idEntity)
                    if idx in node.reachableDown:
                        for path in node.reachableDown[idx]:
                            for iPath in range(len(path.path)):
                                retval+="    Razon: %s\n"%\
                                        path.pretty(self.entity_dict,
                                                    self.edge_type_dict)
                    if idx in node.reachableUp:
                        for path in node.reachableUp[idx]:
                            for iPath in range(len(path.path)):
                                retval+="    Razon: %s\n"%\
                                        path.pretty(self.entity_dict,
                                                    self.edge_type_dict)
                        
                            
        return retval
        
    def addSimilar(self, idEntity):
        y = self.reasoner.propagate(self.reasoner.w['similar'],
                                    self.getDelta(idEntity))
        retval=""
        aux = self.printList(y, idEntity, 1)
        if aux!="":
            retval+="\n  Es parecido o se suele ver con:\n%s\n"%aux
        aux = self.printList(y, idEntity, -1)
        if aux!="":
            retval+="\n  Esta relacionado con:\n%s\n"%aux
        return retval
        
    def addCausesUp(self, idEntity):
        y = self.reasoner.propagateUp(self.reasoner.w['causas'],
                                       self.getDelta(idEntity))
        retval="\n  Puede ser provocado por:\n%s\n"%\
            self.printList(y, idEntity, validTypes=self.causesTypes)
        return retval
        
    def addCauses(self, idEntity):
        y = self.reasoner.propagate(self.reasoner.w['causas'],
                                       self.getDelta(idEntity))
        retval=""
        aux=self.printList(y, idEntity, validTypes=self.causesTypes)
        if aux!="":
            retval="\n  Puede ser provocado por:\n%s\n"%aux            
        return retval
        
    def addConsequences(self, idEntity, msg):
        y1 = self.reasoner.propagateDown(self.reasoner.w['causas'],
                                         self.getDelta(idEntity))
        y2 = self.reasoner.propagateDown(self.reasoner.w['consecuencias'],
                                         self.getDelta(idEntity))
        if np.max(y1)>0:
            y1 /= np.max(y1)
        if np.max(y2)>0:
            y2 /= np.max(y2)
        retval="\n  %s:\n%s\n"%(msg,self.printList(y1+y2, idEntity))
        return retval

    def addTreatments(self, idEntity, msg):
        y = self.reasoner.propagate(self.reasoner.w['tratamientos'],
                                    self.getDelta(idEntity))
        aux=self.printList(y, idEntity, validTypes=self.treatmentTypes)
        retval=""
        if aux!="":
            retval="\n  %s:\n%s\n"%(msg,aux)
        return retval

    def addTreatments2(self, idEntity, msg):
        y = self.reasoner.propagate(self.reasoner.w['tratamientos'],
                                    self.getDelta(idEntity))
        aux=self.printList(y, idEntity, validTypes=self.diseaseTypes)
        retval=""
        if aux!="":
            retval="\n  %s:\n%s\n"%(msg,aux)
        return retval

    def addPrevention(self, idEntity):
        y = self.reasoner.propagateUp(self.reasoner.w['prevencion'],
                                      self.getDelta(idEntity))
        aux=self.printList(y, idEntity, validTypes=self.treatmentTypes)
        retval=""
        if aux!="":
            retval="\n  Se puede prevenir con:\n%s\n"%aux
        return retval

    def addTests(self, idEntity):
        y = self.reasoner.propagateUp(self.reasoner.w['tests'],
                                      self.getDelta(idEntity))
        aux=self.printList(y, idEntity, validTypes=self.diseaseTypes)
        retval=""
        if aux!="":
            retval="\n  Sirve para diagnosticar:\n%s\n"%aux
        return retval

    def addTests2(self, idEntity):
        y = self.reasoner.propagate(self.reasoner.w['tests'],
                                    self.getDelta(idEntity))
        aux=self.printList(y, idEntity,
                           validTypes=self.diseaseTypes+self.testTypes)
        retval=""
        if aux!="":
            retval="\n  Esta ligado a:\n%s\n"%aux
        return retval

    def addAttention(self, idEntity):
        y = self.reasoner.propagate(self.reasoner.w['atencion'],
                                    self.getDelta(idEntity))
        retval=""
        aux=self.printList(y, idEntity)
        if aux!="":
            retval+="\n  Cuidado con:\n%s\n"%aux
        return retval

    def summarize1(self, idEntity, typeName):
        mainName = self.entity_dict[idEntity][0]
        retval = "%s. %d. %s.\n"%(typeName,idEntity,mainName)
        retval+=self.addSynonyms(idEntity, mainName)
        retval+=self.addSimilar(idEntity)
        retval+=self.addCausesUp(idEntity)
        retval+=self.addConsequences(idEntity, "Puede provocar")
        retval+=self.addTreatments(idEntity, "Se puede tratar con")
        retval+=self.addPrevention(idEntity)
        retval+=self.addAttention(idEntity)
        retval+=self.addResources(idEntity)
        return retval
    
    def summarize2(self, idEntity, typeName):
        mainName = self.entity_dict[idEntity][0]
        retval = "%s. %d. %s.\n"%(typeName,idEntity,mainName)
        retval+=self.addSynonyms(idEntity, mainName)
        retval+=self.addSimilar(idEntity)
        retval+=self.addTreatments2(idEntity, "Sirve para tratar o puede causar")
        retval+=self.addConsequences(idEntity, "Sirve para tratar o puede causar")
        retval+=self.addAttention(idEntity)
        retval+=self.addResources(idEntity)
        return retval
    
    def summarize3(self, idEntity, typeName):
        mainName = self.entity_dict[idEntity][0]
        retval = "%s. %d. %s.\n"%(typeName,idEntity,mainName)
        retval+=self.addSynonyms(idEntity, mainName)
        retval+=self.addSimilar(idEntity)
        retval+=self.addTests(idEntity)
        retval+=self.addConsequences(idEntity, "Puede causar")
        retval+=self.addAttention(idEntity)
        retval+=self.addResources(idEntity)
        return retval
    
    def summarize4(self, idEntity, typeName):
        mainName = self.entity_dict[idEntity][0]
        retval = "%s. %d. %s.\n"%(typeName,idEntity,mainName)
        retval+=self.addSynonyms(idEntity, mainName)
        retval+=self.addSimilar(idEntity)
        retval+=self.addCauses(idEntity)
        retval+=self.addTests2(idEntity)
        retval+=self.addAttention(idEntity)
        retval+=self.addResources(idEntity)
        return retval

    def summarize(self, idEntity):
        entityType = self.entity_dict[idEntity][1]
        if entityType == self.reasoner.id_dict['Symptom']:
            return self.summarize1(idEntity, "SINTOMA")
        elif entityType == self.reasoner.id_dict['Disease']:
            return self.summarize1(idEntity, "ENFERMEDAD")
        elif entityType == self.reasoner.id_dict['GroupOfDiseases']:
            return self.summarize1(idEntity, "GRUPO DE ENFERMEDADES")
        elif entityType == self.reasoner.id_dict['Treatment']:
            return self.summarize2(idEntity, "TRATAMIENTO")
        elif entityType == self.reasoner.id_dict['GroupOfTreatments']:
            return self.summarize2(idEntity, "GRUPO DE TRATAMIENTOS")
        elif entityType == self.reasoner.id_dict['Substance']:
            return self.summarize2(idEntity, "SUSTANCIA")
        elif entityType == self.reasoner.id_dict['GroupOfSubstances']:
            return self.summarize2(idEntity, "GRUPO DE SUSTANCIAS")
        elif entityType == self.reasoner.id_dict['Test']:
            return self.summarize3(idEntity, "TEST")
        elif entityType == self.reasoner.id_dict['GroupOfTests']:
            return self.summarize3(idEntity, "GRUPO DE TESTS")
        elif entityType == self.reasoner.id_dict['TestResult']:
            return self.summarize4(idEntity, "RESULTADO DE UNA PRUEBA")
        elif entityType == self.reasoner.id_dict['Pathogen']:
            return self.summarize1(idEntity, "PATOGENO")
        elif entityType == self.reasoner.id_dict['Cause']:
            return self.summarize1(idEntity, "CAUSA")
        elif entityType == self.reasoner.id_dict['Risk']:
            return self.summarize1(idEntity, "RISK")
        return "Tipo no conocido"

summarizer = Summarizer(Reasoner0003())
#print(summarizer.summarize(503)) # Sintoma
#print(summarizer.summarize(11)) # Enfermedad
#print(summarizer.summarize(111)) # Grupo de enfermedades
#print(summarizer.summarize(16)) # Tratamiento
#print(summarizer.summarize(89)) # Grupo de tratamientos
#print(summarizer.summarize(43)) # Substance
#print(summarizer.summarize(574)) # Group of substances
#print(summarizer.summarize(206)) # Test
#print(summarizer.summarize(361)) # Grupo de tests
#print(summarizer.summarize(210)) # Resultado
print(summarizer.summarize(771)) # Patogeno
#print(summarizer.summarize(141)) # Causa
#print(summarizer.summarize(1067)) # Riesgo
