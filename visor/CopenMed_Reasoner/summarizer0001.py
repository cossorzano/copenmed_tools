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
                            self.reasoner.id_dict['Cause'],
                            self.reasoner.id_dict['GroupOfTests'],
                            self.reasoner.id_dict['GroupOfSubstances']]
        self.treatmentTypes = [self.reasoner.id_dict["Treatment"],
                               self.reasoner.id_dict["GroupOfTreatments"],
                               self.reasoner.id_dict["Substance"],
                               self.reasoner.id_dict["GroupOfSubstances"],
                               self.reasoner.id_dict["Activity"]]
    
    def addResources(self, idEntity):
        retval="\n  Recursos:\n"
        for i,row in self.resources_dict[idEntity].iterrows():
            retval+="    "+row.URL+"\n"
        return retval
    
    def addSynonyms(self, idEntity, mainName):
        retval="  Tambien conocido como: "
        i=0
        for _,row in self.details_dict[idEntity].iterrows():
            if i>0:
                retval+=", "
            if row.Entidad!=mainName:
                retval+=row.Entidad+"\n"
                i+=1
        return retval
    
    def getDelta(self, idEntity):
        x = np.zeros(self.reasoner.graph.getNodeMax()+1)
        x[idEntity]=1
        return x
    
    def printList(self, y, idEntity, sameType=0, threshold=0.1, validTypes=None):
        if np.max(y)>0:
            y = y/np.max(y)
        idxSorted = y.argsort()[::-1]
        n=0
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
                    if n>0:
                        retval+=", "
                    if sameType==1:
                        retval+="%s (%d, %f)"%(self.entity_dict[idx][0], idx,
                                                   y[idx])
                    else:
                        retval+="%s (%d, %s, %f)"%(self.entity_dict[idx][0], idx, 
                                                   self.entity_dict[idx][2],
                                                   y[idx])
                    n+=1
                            
        return retval
        
    def addSimilar(self, idEntity):
        y = self.reasoner.propagate(self.reasoner.w['similar'],
                                    self.getDelta(idEntity))
        retval="\n  Es parecido o se suele ver con: %s\n"%self.printList(y, idEntity, 1)
        retval+="\n  Esta relacionado con: %s\n"%self.printList(y, idEntity, -1)
        return retval
        
    def addCausesUp(self, idEntity):
        y = self.reasoner.propagateUp(self.reasoner.w['causas'],
                                       self.getDelta(idEntity))
        retval="\n  Puede ser provocado por: %s\n"%\
            self.printList(y, idEntity, validTypes=self.causesTypes)
        return retval
        
    def addConsequences(self, idEntity):
        y1 = self.reasoner.propagateDown(self.reasoner.w['causas'],
                                         self.getDelta(idEntity))
        y2 = self.reasoner.propagateDown(self.reasoner.w['consecuencias'],
                                         self.getDelta(idEntity))
        if np.max(y1)>0:
            y1 /= np.max(y1)
        if np.max(y2)>0:
            y2 /= np.max(y2)
        retval="\n  Puede provocar: %s\n"%self.printList(y1+y2, idEntity)
        return retval

    def addTreatments(self, idEntity):
        y = self.reasoner.propagate(self.reasoner.w['tratamientos'],
                                    self.getDelta(idEntity))
        retval="\n  Se puede tratar con: %s\n"%\
            self.printList(y, idEntity, validTypes=self.treatmentTypes)
        return retval

    def addPrevention(self, idEntity):
        y = self.reasoner.propagateUp(self.reasoner.w['prevencion'],
                                      self.getDelta(idEntity))
        retval="\n  Se puede prevenir con: %s\n"%\
            self.printList(y, idEntity, validTypes=self.treatmentTypes)
        return retval

    def addAttention(self, idEntity):
        y = self.reasoner.propagate(self.reasoner.w['atencion'],
                                    self.getDelta(idEntity))
        retval="\n  Cuidado con: %s\n"%self.printList(y, idEntity)
        return retval

    def summarizeSymptom(self, idEntity):
        mainName = self.entity_dict[idEntity][0]
        retval = "SINTOMA %d. %s.\n"%(idEntity,mainName)
        retval+=self.addSynonyms(idEntity, mainName)
        retval+=self.addSimilar(idEntity)
        retval+=self.addCausesUp(idEntity)
        retval+=self.addConsequences(idEntity)
        retval+=self.addTreatments(idEntity)
        retval+=self.addPrevention(idEntity)
        retval+=self.addAttention(idEntity)
        retval+=self.addResources(idEntity)
        return retval
    
    def summarize(self, idEntity):
        entityType = self.entity_dict[idEntity][1]
        if entityType == self.reasoner.id_dict['Symptom']:
            return self.summarizeSymptom(idEntity)

summarizer = Summarizer(Reasoner0003())
print(summarizer.summarize(503))
