<<<<<<< HEAD
import codecs
import copy
import os
import math
import numpy as np
import pandas as pd
import pickle
import sys

def make_dict(sheetName, varName, multiple=False):
    if not os.path.exists(fnExcel):
        raise Exception("Cannot find %s"%fnExcel)
    out1 = pd.read_excel(fnExcel, sheet_name=sheetName, engine="openpyxl")
    df = out1.dropna(axis=1, how="all")
    if multiple:
        final_dict = {Id: group for Id, group in df.groupby(varName)}
        return final_dict, {'dict_key': varName, 'dict_columns': None}
    else:
        df_aux = df.loc[:, df.columns != varName]
        id_list = df[varName].values.tolist()
        attribute_list = df_aux.values.tolist()
        final_dict = dict(zip(id_list, attribute_list))
        dict_names = [n for n in df_aux][0:]
        return final_dict, {'dict_key': varName, 'dict_columns': dict_names}

def bidirectional_relations(edge_type_dict):
    list_bidirectional_relations = []
    for idEdge in edge_type_dict.keys():
        edge = edge_type_dict[idEdge]
        edge_name = edge[3]
        bidirectional = " is related to " in edge_name or \
                        " is similar to " in edge_name or \
                        " is also " in edge_name or \
                        " is seen with " in edge_name or \
                        " can be seen also with " in edge_name or \
                        "Substance is Treatment" in edge_name
        if bidirectional:
            if idEdge!=180: # Pathogen is also Cause
                list_bidirectional_relations.append(idEdge)
    return list_bidirectional_relations
            
def load_database(fn):
    infile = open(fn,'rb')
    (lang_dict, lang_dict_info, entity_type_dict, entity_type_dict_info, 
     entity_dict, entity_dict_info,
     edge_type_dict, edge_type_dict_info, list_bidirectional_relations,
     edge_dict, edge_dict_info, details_dict, details_dict_info,
     resources_dict, resources_dict_info) = \
       pickle.load(infile)
    infile.close()
    return (lang_dict, lang_dict_info, entity_type_dict, entity_type_dict_info, 
            entity_dict, entity_dict_info,
            edge_type_dict, edge_type_dict_info, list_bidirectional_relations,
            edge_dict, edge_dict_info, details_dict, details_dict_info,
            resources_dict, resources_dict_info)

def separate_entities_by_type(entity_type_dict, entity_dict):
    entities = {}
    for idEntity in entity_dict:
        idEntityType = entity_dict[idEntity][1]
        if idEntityType not in entities:
            entities[idEntityType]=[]
        entities[idEntityType].append(idEntity)
    return entities

def count_edges(edge_dict):
    entities_count = {}
    for idEdge in edge_dict:
        idEntity1 = edge_dict[idEdge][0]
        idEntity2 = edge_dict[idEdge][1]
        if not idEntity1 in entities_count:
            entities_count[idEntity1] = [0,0,0] # Outgoing, incoming
        if not idEntity2 in entities_count:
            entities_count[idEntity2] = [0,0,0]
        entities_count[idEntity1][0]+=1
        entities_count[idEntity2][1]+=1
    for idEntity in entities_count:
        entities_count[idEntity][2]=entities_count[idEntity][0]+entities_count[idEntity][1]
    return entities_count

def add_directional_edges(edge_dict, list_bidirectional_relations):
    edges_present = {}
    for keyEdge in edge_dict:
        edge = edge_dict[keyEdge]
        edgeType = edge[2]

        if edgeType in list_bidirectional_relations:
            idEntity1 = edge[0]
            idEntity2 = edge[1]
            edges_present[(idEntity1,idEntity2,edgeType)] = 1

    toAdd = []
    for keyEdge in edge_dict:
        edge = edge_dict[keyEdge]
        edgeType = edge[2]

        if edgeType in list_bidirectional_relations:
            idEntity1 = edge[0]
            idEntity2 = edge[1]
            if idEntity1!=idEntity2 and \
               not (idEntity2,idEntity1,edgeType) in edges_present:
                toAdd.append([idEntity2,idEntity1,edgeType,edge[3],
                                      edge[4],edge[5]])

    nextKey = np.max([key for key in edge_dict])+1
    N=0
    for edge in toAdd:
        edge_dict[nextKey]=edge
        nextKey+=1
        N+=1
    print("%d new edges added"%N)

def define_labels(entity_type_dict, edge_type_dict):
    id_dict = {}
    for idEntityType in entity_type_dict:
        name, _, _ = entity_type_dict[idEntityType]
        id_dict[name]=idEntityType
    
    def find_edge(name):
        rightId = None
        for idEdgeType in edge_type_dict:
            edgeType = edge_type_dict[idEdgeType]
            edgeName = edgeType[3]
            if edgeName==name:
                rightId = idEdgeType
        id_dict[name]=rightId
    find_edge("Disease causes Symptom")
    find_edge("Disease1 may evolve and coexist with Disease2")
    find_edge("Disease belongs to Group")
    find_edge("Symptom is associated to Disease")
    find_edge("Disease is observed in Anatomy")
    return id_dict


class Node():
    def __init__(self, idEntity, idEntityType, entityName, id_dict):
        self.idEntity = idEntity
        self.idEntityType = idEntityType
        self.entityName = entityName
        self.incomingEdges = {}
        self.outgoingEdges = {}
        self.reachableDown = {}
        self.reachableUp = {}
        self.id_dict = id_dict
    
    def addOutgoingEdge(self, idEntityTo, idEdgeType, strength, idEdge):
        edgeKey = (idEntityTo, idEdgeType, idEdge)
        if not edgeKey in self.outgoingEdges:
            self.outgoingEdges[edgeKey] = 0.0
        self.outgoingEdges[edgeKey] += strength

    def addIncomingEdge(self, idEntityFrom, idEdgeType, strength, idEdge):
        edgeKey = (idEntityFrom, idEdgeType, idEdge)
        if not edgeKey in self.incomingEdges:
            self.incomingEdges[edgeKey] = 0.0
        self.incomingEdges[edgeKey] += strength
    
    def createPathsDown(self, distance, graph, weight, threshold):
        if distance==0 and weight>threshold:
            return [Path(self.idEntity, weight)]
        
        paths = []
        for idEntityTo, idEdgeType, idEdge in self.outgoingEdges:
            strength = self.outgoingEdges[(idEntityTo, idEdgeType, idEdge)]
            weightStrength = weight*strength
            if weightStrength>threshold:
                if idEntityTo in graph:
                    pathsTo = graph[idEntityTo].createPathsDown(distance-1, graph,
                                                                weightStrength,
                                                                threshold)
                    for path in pathsTo:
                        path.prependNode(self.idEntity, weight, idEdgeType,
                                         strength, idEdge)
                        if path.originEntity!=path.terminalEntity:
                            paths.append(path)
        
        return paths

    def createPaths(self, distance, graph, threshold=0.25):
        for d in range(1,distance+1):
            paths = self.createPathsDown(d, graph, 1, threshold)
            for path in paths:
                if not path.terminalEntity in self.reachableDown:
                    self.reachableDown[path.terminalEntity] = []
                self.reachableDown[path.terminalEntity].append(copy.copy(path))
    
    def getPrevalence(self, idPopulation=None):
        DISEASE=self.id_dict["Disease"]
        GROUPOFDISEASES=self.id_dict["GroupOfDiseases"]
        PATHOGEN=self.id_dict["Pathogen"]
        if self.idEntityType!=DISEASE and \
           self.idEntityType!=GROUPOFDISEASES and \
           self.idEntityType!=PATHOGEN:
           return 0.0
        if idPopulation is None:
            idPopulation = self.id_dict['Población general']
        PREVALENCE_DISEASE = self.id_dict['The prevalence of this Disease in this Population is ...']
        PREVALENCE_GROUP = self.id_dict['The prevalence of this Group in this Population is ...']
        PREVALENCE_PATHOGEN = self.id_dict['The probability of observing this Pathogen in this Population is ...']
        for (idEntityTo, idEdgeType, idEdge) in self.outgoingEdges:
            if idEntityTo==idPopulation:
                if self.idEntityType==DISEASE and idEdgeType==PREVALENCE_DISEASE or \
                   self.idEntityType==GROUPOFDISEASES and idEdgeType==PREVALENCE_GROUP or \
                   self.idEntityType==PATHOGEN and idEdgeType==PREVALENCE_PATHOGEN:
                    return self.outgoingEdges[(idEntityTo, idEdgeType, idEdge)]
        return 0.0

class Path():
    def __init__(self, idEntity=None, weight=1):
        self.path = []
        self.originEntity = None
        self.terminalEntity = None
        if idEntity is not None:
            self.originEntity = idEntity
            self.addTerminalNode(idEntity, weight)
    
    def addTerminalNode(self, idEntity, weight):
        self.path.append((weight, None, None, None, None))
        self.terminalEntity = idEntity

    def prependNode(self, idEntity, weight, idEdgeType, edgeStrength, idEdge):
        self.path.insert(0,(weight, self.originEntity, idEdgeType, edgeStrength, idEdge))
        self.originEntity = idEntity
    
    def appendNode(self, idEntity, weight, idEdgeType, edgeStrength, idEdge):
        self.path.append((weight, idEntity, idEdgeType, edgeStrength, idEdge))
        self.terminalEntity = idEntity
    
    def getLastWeight(self):
        if len(self.path)==0:
            return None, 0.0
        else:
            return self.terminalEntity, self.path[-1][0]
        
    def getFirstComment(self, edge_dict):
        if len(self.path)==0:
            return None
        else:
            _, _, _, _, idEdge = self.path[0]
            if idEdge is None:
                return None
            comment = edge_dict[idEdge][4]
            if isinstance(comment,str):
                return comment
            else:
                return ""
    
    def __str__(self):
        retval = "%d --> %d: [%d"%(self.originEntity, self.terminalEntity,
                                   self.originEntity)
        for weight, idEntity, idEdgeType, edgeStrength, idEdge in self.path:
            retval += " (w=%f)"%weight
            if idEntity is not None:
                retval+=" --(%d,%f,%d)--> %d"%(idEdgeType, edgeStrength, idEdge, idEntity)
        retval+="]"
        return retval

    def pretty(self, entity_dict, edge_type_dict):
        strOrigin = entity_dict[self.originEntity][0]
        strTerminal = entity_dict[self.terminalEntity][0]
        retval = "%s (%d) --> %s (%d): [%s (%d)"%(strOrigin,
                                                  self.originEntity, 
                                                  strTerminal,
                                                  self.terminalEntity,
                                                  strOrigin,
                                                  self.originEntity)
        for weight, idEntity, idEdgeType, edgeStrength, idEdge in self.path:
            retval += " (w=%f)"%weight
            if idEntity is not None:
                retval+=" --(%s (%d),%f,%d)--> %s (%d)"%\
                    (edge_type_dict[idEdgeType][3], idEdgeType,
                     edgeStrength, idEdge, entity_dict[idEntity][0], idEntity)
        retval+="]"
        return retval
    
    def getEdgeTypes(self):
        edgeTypes = []
        for _, _, idEdgeType, _, _ in self.path:
            if idEdgeType is not None:
                edgeTypes.append(idEdgeType)
        return edgeTypes
          

class Graph():
    def __init__(self, entity_dict, entity_type_dict,
                 edge_dict, edge_type_dict):
        self.entity_dict = entity_dict
        self.entity_type_dict = entity_type_dict
        self.edge_dict = edge_dict
        self.edge_type_dict = edge_type_dict
        self.graph = {}
        self.node_max = 0
        self.define_labels()

        # Create all nodes
        for idEntity in entity_dict:
            self.graph[idEntity]=Node(idEntity, entity_dict[idEntity][1], 
                                      entity_dict[idEntity][0], self.id_dict)
            self.node_max = max(self.node_max, idEntity)
        
        # Create all edges
        for idEdge in edge_dict:
            edge = edge_dict[idEdge]
            idEntityFrom = edge[0]
            idEntityTo = edge[1]
            idEdgeType = edge[2]
            strength = edge[5]
            
            if idEntityFrom in self.graph:
                self.graph[idEntityFrom].addOutgoingEdge(idEntityTo, idEdgeType,
                                                         strength, idEdge)
            if idEntityTo in self.graph:
                self.graph[idEntityTo].addIncomingEdge(idEntityFrom, idEdgeType,
                                                       strength, idEdge)
        # Get prevalences in the general population
        self.getPrevalences()
    
    def define_labels(self):
        self.id_dict = {}
        # Add all entity types
        for idEntityType in self.entity_type_dict:
            name, _, _ = self.entity_type_dict[idEntityType]
            self.id_dict[name]=idEntityType
        
        # Add all edge types
        for idEdgeType in self.edge_type_dict:
            edgeType = self.edge_type_dict[idEdgeType]
            edgeName = edgeType[3]
            self.id_dict[edgeName]=idEdgeType
        
        # Add specific entities
        def find_entity(entityName):
            for idEntity in self.entity_dict:
                name, _, _, _ = self.entity_dict[idEntity]
                if name==entityName:
                    self.id_dict[name]=idEntity
                    break
        find_entity("Población general")

    def createPaths(self, distance=2, threshold=0.25):
        for idEntity in self.graph:
            self.graph[idEntity].createPaths(distance, self.graph, threshold)
            for idEntityReachable in self.graph[idEntity].reachableDown:
                entityReachable = self.graph[idEntityReachable]
                for path in self.graph[idEntity].reachableDown[idEntityReachable]:
                    if not idEntity in entityReachable.reachableUp:
                        entityReachable.reachableUp[idEntity] = []
                    entityReachable.reachableUp[idEntity].append(path)
    
    def getNodeMax(self):
        return self.node_max
    
    def getNode(self, idEntity):
        if idEntity in self.graph:
            return self.graph[idEntity]
        else:
            return None
    
    def getNodeType(self, idEntity):
        if idEntity in self.graph:
            _, nodeType, _, _ = self.entity_dict[idEntity]
            return nodeType
        else:
            return None        

    def getNodePrevalence(self, idEntity, default=0.0):
        if idEntity in self.graph:
            prevalence = self.prevalence_dict[idEntity]
            if prevalence == 0.0:
                prevalence = default
            return prevalence
        else:
            return default
    
    def getPrevalences(self):
        self.prevalence_dict={}
        for idEntity in self.graph:
            self.prevalence_dict[idEntity] = self.graph[idEntity].getPrevalence()
        p=np.asarray([x for x in self.prevalence_dict.values()],dtype=np.float64)
        self.avgPrevalence = math.exp(np.mean(np.log(p[p>0])))

class COpenMedAlgorithm():
    def __init__(self, fnLog, debug=False):
        self.debug = debug
        if debug:
            self.fhLog=codecs.open(fnLog, 'w', encoding='utf8')
        else:
            self.fhLog=None

    def __del__(self):
        if self.debug:
            self.fhLog.close()
    
    def constructGraph(self, fnPickle, distance=2, threshold=0.25):
        _, _, self.entity_type_dict, self.entity_type_dict_info, \
           self.entity_dict, self.entity_dict_info, \
           self.edge_type_dict, self.edge_type_dict_info, \
           list_bidirectional_relations, \
           self.edge_dict, self.edge_dict_info, _, _, _, _ = \
               load_database(fnPickle)
        self.entities = separate_entities_by_type(self.entity_type_dict, 
                                                  self.entity_dict)
        add_directional_edges(self.edge_dict, list_bidirectional_relations)
        
        self.graph = Graph(self.entity_dict, self.entity_type_dict, 
                           self.edge_dict, self.edge_type_dict)
        self.graph.createPaths(distance, threshold)
    
    def propagateDown(self, weight, scoreIn, tol=1e-4):
        scoreOut=np.zeros(scoreIn.shape[0])
        for idEntity in range(scoreIn.shape[0]):
            x = scoreIn[idEntity]
            if abs(x)<tol:
                continue
            node = self.graph.getNode(idEntity)
            if self.debug:
                self.fhLog.write("\nSpreading %s(%d) scoreIn=%f\n\n"%(node.entityName,
                                                                      idEntity, x))
    
            # For all outgoing edges
            for idEntityTo in node.reachableDown:
                toSum = 0.0
                for path in node.reachableDown[idEntityTo]:
                    xInter=x
                    for iPath in range(len(path.path)):
                        _, idEntityToInter, idEdgeType, edgeStrength, _ = path.path[iPath]
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
                        if self.debug:
                            self.fhLog.write(path.pretty(self.entity_dict,
                                                         self.edge_type_dict))
                            self.fhLog.write("Updating %s (%d) with %f\n"%\
                                  (self.graph.getNode(idEntityTo).entityName,
                                   idEntityTo, xInter))
                if abs(toSum)>0:
                    scoreOut[idEntityTo]+=toSum
                    if self.debug:
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
            if self.debug:
                self.fhLog.write("\nSpreading %s(%d) scoreIn=%f\n\n"%(node.entityName,
                                                                      idEntity, x))

            # For all incoming edges
            for idEntityFrom in node.reachableUp:
                toSum = 0.0
                for path in node.reachableUp[idEntityFrom]:
                    xInter=x
                    for iPath in reversed(range(len(path.path)-1)):
                        _, idEntityFromInter, idEdgeType, edgeStrength, _ = path.path[iPath]
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
                        if self.debug:
                            self.fhLog.write(path.pretty(self.entity_dict,
                                                         self.edge_type_dict))
                            self.fhLog.write("Updating %s (%d) with %f\n"%\
                                  (self.graph.getNode(idEntityFrom).entityName,
                                   idEntityFrom, xInter))
    
                if abs(toSum)>0:
                    scoreOut[idEntityFrom]+=toSum
                    if self.debug:
                        self.fhLog.write("\nNew score %s (%d)= %f\n"%\
                              (self.graph.getNode(idEntityFrom).entityName,
                               idEntityFrom, scoreOut[idEntityFrom]))
        return scoreOut

    def propagate(self, weight, scoreIn, tol=1e-4):
        return self.propagateDown(weight, scoreIn, tol)+\
               self.propagateUp(weight, scoreIn, tol)

if __name__=="__main__":
    if len(sys.argv) <= 1:
        print("Usage: python3 copenmed_tools excel2pkl <excelfile>")
        print("   <excelfile> must contain the Excel sheets of COpenMed")
        sys.exit(1)
    
    if sys.argv[1]=="excel2pkl":
        fnExcel = sys.argv[2]
        
        # Read all sheets
        lang_dict, lang_dict_info               = make_dict('idiomas',          'IdIdioma')
        entity_type_dict, entity_type_dict_info = make_dict('tipos_entidad',    'IdTipoEntidad')
        entity_dict, entity_dict_info           = make_dict('entidades',        'IdEntidad')
        edge_type_dict, edge_type_dict_info     = make_dict('tipos_relaciones', 'IdTipoAsociacion')
        edge_dict, edge_dict_info               = make_dict('relaciones',       'IdAsociacion')
        
        # Details and resources have several entries per idEntity
        details_dict, details_dict_info         = make_dict('detalles', 'IdEntidad', True)
        resources_dict, resources_dict_info     = make_dict('recursos', 'IdEntidad', True)
        
        list_bidirectional_relations = bidirectional_relations(edge_type_dict)
        
        # Pickle file
        filename = 'copenmed.pkl'
        outfile = open(filename,'wb')
        obj = (lang_dict, lang_dict_info, entity_type_dict, entity_type_dict_info, 
               entity_dict, entity_dict_info,
               edge_type_dict, edge_type_dict_info, list_bidirectional_relations,
               edge_dict, edge_dict_info, details_dict, details_dict_info,
        	   resources_dict, resources_dict_info)
        pickle.dump(obj,outfile)
        outfile.close()
=======
import codecs
import copy
import os
import math
import numpy as np
import pandas as pd
import pickle
import sys

def make_dict(sheetName, varName, multiple=False):
    if not os.path.exists(fnExcel):
        raise Exception("Cannot find %s"%fnExcel)
    out1 = pd.read_excel(fnExcel, sheet_name=sheetName, engine="openpyxl")
    df = out1.dropna(axis=1, how="all")
    if multiple:
        final_dict = {Id: group for Id, group in df.groupby(varName)}
        return final_dict, {'dict_key': varName, 'dict_columns': None}
    else:
        df_aux = df.loc[:, df.columns != varName]
        id_list = df[varName].values.tolist()
        attribute_list = df_aux.values.tolist()
        final_dict = dict(zip(id_list, attribute_list))
        dict_names = [n for n in df_aux][0:]
        return final_dict, {'dict_key': varName, 'dict_columns': dict_names}

def bidirectional_relations(edge_type_dict):
    list_bidirectional_relations = []
    for idEdge in edge_type_dict.keys():
        edge = edge_type_dict[idEdge]
        edge_name = edge[3]
        bidirectional = " is related to " in edge_name or \
                        " is similar to " in edge_name or \
                        " is also " in edge_name or \
                        " is seen with " in edge_name or \
                        " can be seen also with " in edge_name or \
                        "Substance is Treatment" in edge_name
        if bidirectional:
            if idEdge!=180: # Pathogen is also Cause
                list_bidirectional_relations.append(idEdge)
    return list_bidirectional_relations
            
def load_database(fn):
    infile = open(fn,'rb')
    (lang_dict, lang_dict_info, entity_type_dict, entity_type_dict_info, 
     entity_dict, entity_dict_info,
     edge_type_dict, edge_type_dict_info, list_bidirectional_relations,
     edge_dict, edge_dict_info, details_dict, details_dict_info,
     resources_dict, resources_dict_info) = \
       pickle.load(infile)
    infile.close()
    return (lang_dict, lang_dict_info, entity_type_dict, entity_type_dict_info, 
            entity_dict, entity_dict_info,
            edge_type_dict, edge_type_dict_info, list_bidirectional_relations,
            edge_dict, edge_dict_info, details_dict, details_dict_info,
            resources_dict, resources_dict_info)

def separate_entities_by_type(entity_type_dict, entity_dict):
    entities = {}
    for idEntity in entity_dict:
        idEntityType = entity_dict[idEntity][1]
        if idEntityType not in entities:
            entities[idEntityType]=[]
        entities[idEntityType].append(idEntity)
    return entities

def count_edges(edge_dict):
    entities_count = {}
    for idEdge in edge_dict:
        idEntity1 = edge_dict[idEdge][0]
        idEntity2 = edge_dict[idEdge][1]
        if not idEntity1 in entities_count:
            entities_count[idEntity1] = [0,0,0] # Outgoing, incoming
        if not idEntity2 in entities_count:
            entities_count[idEntity2] = [0,0,0]
        entities_count[idEntity1][0]+=1
        entities_count[idEntity2][1]+=1
    for idEntity in entities_count:
        entities_count[idEntity][2]=entities_count[idEntity][0]+entities_count[idEntity][1]
    return entities_count

def add_directional_edges(edge_dict, list_bidirectional_relations):
    edges_present = {}
    for keyEdge in edge_dict:
        edge = edge_dict[keyEdge]
        edgeType = edge[2]

        if edgeType in list_bidirectional_relations:
            idEntity1 = edge[0]
            idEntity2 = edge[1]
            edges_present[(idEntity1,idEntity2,edgeType)] = 1

    toAdd = []
    for keyEdge in edge_dict:
        edge = edge_dict[keyEdge]
        edgeType = edge[2]

        if edgeType in list_bidirectional_relations:
            idEntity1 = edge[0]
            idEntity2 = edge[1]
            if idEntity1!=idEntity2 and \
               not (idEntity2,idEntity1,edgeType) in edges_present:
                toAdd.append([idEntity2,idEntity1,edgeType,edge[3],
                                      edge[4],edge[5]])

    nextKey = np.max([key for key in edge_dict])+1
    N=0
    for edge in toAdd:
        edge_dict[nextKey]=edge
        nextKey+=1
        N+=1
    print("%d new edges added"%N)

def define_labels(entity_type_dict, edge_type_dict):
    id_dict = {}
    for idEntityType in entity_type_dict:
        name, _, _ = entity_type_dict[idEntityType]
        id_dict[name]=idEntityType
    
    def find_edge(name):
        rightId = None
        for idEdgeType in edge_type_dict:
            edgeType = edge_type_dict[idEdgeType]
            edgeName = edgeType[3]
            if edgeName==name:
                rightId = idEdgeType
        id_dict[name]=rightId
    find_edge("Disease causes Symptom")
    find_edge("Disease1 may evolve and coexist with Disease2")
    find_edge("Disease belongs to Group")
    find_edge("Symptom is associated to Disease")
    find_edge("Disease is observed in Anatomy")
    return id_dict


class Node():
    def __init__(self, idEntity, idEntityType, entityName, id_dict):
        self.idEntity = idEntity
        self.idEntityType = idEntityType
        self.entityName = entityName
        self.incomingEdges = {}
        self.outgoingEdges = {}
        self.reachableDown = {}
        self.reachableUp = {}
        self.id_dict = id_dict
    
    def addOutgoingEdge(self, idEntityTo, idEdgeType, strength, idEdge):
        edgeKey = (idEntityTo, idEdgeType, idEdge)
        if not edgeKey in self.outgoingEdges:
            self.outgoingEdges[edgeKey] = 0.0
        self.outgoingEdges[edgeKey] += strength

    def addIncomingEdge(self, idEntityFrom, idEdgeType, strength, idEdge):
        edgeKey = (idEntityFrom, idEdgeType, idEdge)
        if not edgeKey in self.incomingEdges:
            self.incomingEdges[edgeKey] = 0.0
        self.incomingEdges[edgeKey] += strength
    
    def createPathsDown(self, distance, graph, weight, threshold):
        if distance==0 and weight>threshold:
            return [Path(self.idEntity, weight)]
        
        paths = []
        for idEntityTo, idEdgeType, idEdge in self.outgoingEdges:
            strength = self.outgoingEdges[(idEntityTo, idEdgeType, idEdge)]
            weightStrength = weight*strength
            if weightStrength>threshold:
                if idEntityTo in graph:
                    pathsTo = graph[idEntityTo].createPathsDown(distance-1, graph,
                                                                weightStrength,
                                                                threshold)
                    for path in pathsTo:
                        path.prependNode(self.idEntity, weight, idEdgeType,
                                         strength, idEdge)
                        if path.originEntity!=path.terminalEntity:
                            paths.append(path)
        
        return paths

    def createPaths(self, distance, graph, threshold=0.25):
        for d in range(1,distance+1):
            paths = self.createPathsDown(d, graph, 1, threshold)
            for path in paths:
                if not path.terminalEntity in self.reachableDown:
                    self.reachableDown[path.terminalEntity] = []
                self.reachableDown[path.terminalEntity].append(copy.copy(path))
    
    def getPrevalence(self, idPopulation=None):
        DISEASE=self.id_dict["Disease"]
        GROUPOFDISEASES=self.id_dict["GroupOfDiseases"]
        PATHOGEN=self.id_dict["Pathogen"]
        if self.idEntityType!=DISEASE and \
           self.idEntityType!=GROUPOFDISEASES and \
           self.idEntityType!=PATHOGEN:
           return 0.0
        if idPopulation is None:
            idPopulation = self.id_dict['Población general']
        PREVALENCE_DISEASE = self.id_dict['The prevalence of this Disease in this Population is ...']
        PREVALENCE_GROUP = self.id_dict['The prevalence of this Group in this Population is ...']
        PREVALENCE_PATHOGEN = self.id_dict['The probability of observing this Pathogen in this Population is ...']
        for (idEntityTo, idEdgeType, idEdge) in self.outgoingEdges:
            if idEntityTo==idPopulation:
                if self.idEntityType==DISEASE and idEdgeType==PREVALENCE_DISEASE or \
                   self.idEntityType==GROUPOFDISEASES and idEdgeType==PREVALENCE_GROUP or \
                   self.idEntityType==PATHOGEN and idEdgeType==PREVALENCE_PATHOGEN:
                    return self.outgoingEdges[(idEntityTo, idEdgeType, idEdge)]
        return 0.0

class Path():
    def __init__(self, idEntity=None, weight=1):
        self.path = []
        self.originEntity = None
        self.terminalEntity = None
        if idEntity is not None:
            self.originEntity = idEntity
            self.addTerminalNode(idEntity, weight)
    
    def addTerminalNode(self, idEntity, weight):
        self.path.append((weight, None, None, None, None))
        self.terminalEntity = idEntity

    def prependNode(self, idEntity, weight, idEdgeType, edgeStrength, idEdge):
        self.path.insert(0,(weight, self.originEntity, idEdgeType, edgeStrength, idEdge))
        self.originEntity = idEntity
    
    def appendNode(self, idEntity, weight, idEdgeType, edgeStrength, idEdge):
        self.path.append((weight, idEntity, idEdgeType, edgeStrength, idEdge))
        self.terminalEntity = idEntity
    
    def getLastWeight(self):
        if len(self.path)==0:
            return None, 0.0
        else:
            return self.terminalEntity, self.path[-1][0]
        
    def getFirstComment(self, edge_dict):
        if len(self.path)==0:
            return None
        else:
            _, _, _, _, idEdge = self.path[0]
            if idEdge is None:
                return None
            comment = edge_dict[idEdge][4]
            if isinstance(comment,str):
                return comment
            else:
                return ""
    
    def __str__(self):
        retval = "%d --> %d: [%d"%(self.originEntity, self.terminalEntity,
                                   self.originEntity)
        for weight, idEntity, idEdgeType, edgeStrength, idEdge in self.path:
            retval += " (w=%f)"%weight
            if idEntity is not None:
                retval+=" --(%d,%f,%d)--> %d"%(idEdgeType, edgeStrength, idEdge, idEntity)
        retval+="]"
        return retval

    def pretty(self, entity_dict, edge_type_dict):
        strOrigin = entity_dict[self.originEntity][0]
        strTerminal = entity_dict[self.terminalEntity][0]
        retval = "%s (%d) --> %s (%d): [%s (%d)"%(strOrigin,
                                                  self.originEntity, 
                                                  strTerminal,
                                                  self.terminalEntity,
                                                  strOrigin,
                                                  self.originEntity)
        for weight, idEntity, idEdgeType, edgeStrength, idEdge in self.path:
            retval += " (w=%f)"%weight
            if idEntity is not None:
                retval+=" --(%s (%d),%f,%d)--> %s (%d)"%\
                    (edge_type_dict[idEdgeType][3], idEdgeType,
                     edgeStrength, idEdge, entity_dict[idEntity][0], idEntity)
        retval+="]"
        return retval
    
    def getEdgeTypes(self):
        edgeTypes = []
        for _, _, idEdgeType, _, _ in self.path:
            if idEdgeType is not None:
                edgeTypes.append(idEdgeType)
        return edgeTypes
          

class Graph():
    def __init__(self, entity_dict, entity_type_dict,
                 edge_dict, edge_type_dict):
        self.entity_dict = entity_dict
        self.entity_type_dict = entity_type_dict
        self.edge_dict = edge_dict
        self.edge_type_dict = edge_type_dict
        self.graph = {}
        self.node_max = 0
        self.define_labels()

        # Create all nodes
        for idEntity in entity_dict:
            self.graph[idEntity]=Node(idEntity, entity_dict[idEntity][1], 
                                      entity_dict[idEntity][0], self.id_dict)
            self.node_max = max(self.node_max, idEntity)
        
        # Create all edges
        for idEdge in edge_dict:
            edge = edge_dict[idEdge]
            idEntityFrom = edge[0]
            idEntityTo = edge[1]
            idEdgeType = edge[2]
            strength = edge[5]
            
            if idEntityFrom in self.graph:
                self.graph[idEntityFrom].addOutgoingEdge(idEntityTo, idEdgeType,
                                                         strength, idEdge)
            if idEntityTo in self.graph:
                self.graph[idEntityTo].addIncomingEdge(idEntityFrom, idEdgeType,
                                                       strength, idEdge)
        # Get prevalences in the general population
        self.getPrevalences()
    
    def define_labels(self):
        self.id_dict = {}
        # Add all entity types
        for idEntityType in self.entity_type_dict:
            name, _, _ = self.entity_type_dict[idEntityType]
            self.id_dict[name]=idEntityType
        
        # Add all edge types
        for idEdgeType in self.edge_type_dict:
            edgeType = self.edge_type_dict[idEdgeType]
            edgeName = edgeType[3]
            self.id_dict[edgeName]=idEdgeType
        
        # Add specific entities
        def find_entity(entityName):
            for idEntity in self.entity_dict:
                name, _, _, _ = self.entity_dict[idEntity]
                if name==entityName:
                    self.id_dict[name]=idEntity
                    break
        find_entity("Población general")

    def createPaths(self, distance=2, threshold=0.25):
        for idEntity in self.graph:
            self.graph[idEntity].createPaths(distance, self.graph, threshold)
            for idEntityReachable in self.graph[idEntity].reachableDown:
                entityReachable = self.graph[idEntityReachable]
                for path in self.graph[idEntity].reachableDown[idEntityReachable]:
                    if not idEntity in entityReachable.reachableUp:
                        entityReachable.reachableUp[idEntity] = []
                    entityReachable.reachableUp[idEntity].append(path)
    
    def getNodeMax(self):
        return self.node_max
    
    def getNode(self, idEntity):
        if idEntity in self.graph:
            return self.graph[idEntity]
        else:
            return None
    
    def getNodeType(self, idEntity):
        if idEntity in self.graph:
            _, nodeType, _, _ = self.entity_dict[idEntity]
            return nodeType
        else:
            return None        

    def getNodePrevalence(self, idEntity, default=0.0):
        if idEntity in self.graph:
            prevalence = self.prevalence_dict[idEntity]
            if prevalence == 0.0:
                prevalence = default
            return prevalence
        else:
            return default
    
    def getPrevalences(self):
        self.prevalence_dict={}
        for idEntity in self.graph:
            self.prevalence_dict[idEntity] = self.graph[idEntity].getPrevalence()
        p=np.asarray([x for x in self.prevalence_dict.values()],dtype=np.float64)
        self.avgPrevalence = math.exp(np.mean(np.log(p[p>0])))

class COpenMedAlgorithm():
    def __init__(self, fnLog, debug=False):
        self.debug = debug
        if debug:
            self.fhLog=codecs.open(fnLog, 'w', encoding='utf8')
        else:
            self.fhLog=None

    def __del__(self):
        if self.debug:
            self.fhLog.close()
    
    def constructGraph(self, fnPickle, distance=2, threshold=0.25):
        _, _, self.entity_type_dict, self.entity_type_dict_info, \
           self.entity_dict, self.entity_dict_info, \
           self.edge_type_dict, self.edge_type_dict_info, \
           list_bidirectional_relations, \
           self.edge_dict, self.edge_dict_info, _, _, _, _ = \
               load_database(fnPickle)
        self.entities = separate_entities_by_type(self.entity_type_dict, 
                                                  self.entity_dict)
        add_directional_edges(self.edge_dict, list_bidirectional_relations)
        
        self.graph = Graph(self.entity_dict, self.entity_type_dict, 
                           self.edge_dict, self.edge_type_dict)
        self.graph.createPaths(distance, threshold)
    
    def propagateDown(self, weight, scoreIn, tol=1e-4):
        scoreOut=np.zeros(scoreIn.shape[0])
        for idEntity in range(scoreIn.shape[0]):
            x = scoreIn[idEntity]
            if abs(x)<tol:
                continue
            node = self.graph.getNode(idEntity)
            if self.debug:
                self.fhLog.write("\nSpreading %s(%d) scoreIn=%f\n\n"%(node.entityName,
                                                                      idEntity, x))
    
            # For all outgoing edges
            for idEntityTo in node.reachableDown:
                toSum = 0.0
                for path in node.reachableDown[idEntityTo]:
                    xInter=x
                    for iPath in range(len(path.path)):
                        _, idEntityToInter, idEdgeType, edgeStrength, _ = path.path[iPath]
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
                        if self.debug:
                            self.fhLog.write(path.pretty(self.entity_dict,
                                                         self.edge_type_dict))
                            self.fhLog.write("Updating %s (%d) with %f\n"%\
                                  (self.graph.getNode(idEntityTo).entityName,
                                   idEntityTo, xInter))
                if abs(toSum)>0:
                    scoreOut[idEntityTo]+=toSum
                    if self.debug:
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
            if self.debug:
                self.fhLog.write("\nSpreading %s(%d) scoreIn=%f\n\n"%(node.entityName,
                                                                      idEntity, x))

            # For all incoming edges
            for idEntityFrom in node.reachableUp:
                toSum = 0.0
                for path in node.reachableUp[idEntityFrom]:
                    xInter=x
                    for iPath in reversed(range(len(path.path)-1)):
                        _, idEntityFromInter, idEdgeType, edgeStrength, _ = path.path[iPath]
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
                        if self.debug:
                            self.fhLog.write(path.pretty(self.entity_dict,
                                                         self.edge_type_dict))
                            self.fhLog.write("Updating %s (%d) with %f\n"%\
                                  (self.graph.getNode(idEntityFrom).entityName,
                                   idEntityFrom, xInter))
    
                if abs(toSum)>0:
                    scoreOut[idEntityFrom]+=toSum
                    if self.debug:
                        self.fhLog.write("\nNew score %s (%d)= %f\n"%\
                              (self.graph.getNode(idEntityFrom).entityName,
                               idEntityFrom, scoreOut[idEntityFrom]))
        return scoreOut

    def propagate(self, weight, scoreIn, tol=1e-4):
        return self.propagateDown(weight, scoreIn, tol)+\
               self.propagateUp(weight, scoreIn, tol)

if __name__=="__main__":
    if len(sys.argv) <= 1:
        print("Usage: python3 copenmed_tools excel2pkl <excelfile>")
        print("   <excelfile> must contain the Excel sheets of COpenMed")
        sys.exit(1)
    
    if sys.argv[1]=="excel2pkl":
        fnExcel = sys.argv[2]
        
        # Read all sheets
        lang_dict, lang_dict_info               = make_dict('idiomas',          'IdIdioma')
        entity_type_dict, entity_type_dict_info = make_dict('tipos_entidad',    'IdTipoEntidad')
        entity_dict, entity_dict_info           = make_dict('entidades',        'IdEntidad')
        edge_type_dict, edge_type_dict_info     = make_dict('tipos_relaciones', 'IdTipoAsociacion')
        edge_dict, edge_dict_info               = make_dict('relaciones',       'IdAsociacion')
        
        # Details and resources have several entries per idEntity
        details_dict, details_dict_info         = make_dict('detalles', 'IdEntidad', True)
        resources_dict, resources_dict_info     = make_dict('recursos', 'IdEntidad', True)
        
        list_bidirectional_relations = bidirectional_relations(edge_type_dict)
        
        # Pickle file
        filename = 'copenmed.pkl'
        outfile = open(filename,'wb')
        obj = (lang_dict, lang_dict_info, entity_type_dict, entity_type_dict_info, 
               entity_dict, entity_dict_info,
               edge_type_dict, edge_type_dict_info, list_bidirectional_relations,
               edge_dict, edge_dict_info, details_dict, details_dict_info,
        	   resources_dict, resources_dict_info)
        pickle.dump(obj,outfile)
        outfile.close()
>>>>>>> c79b8ea472b68ecb4fb2b58da2699dc3ca20083d
        