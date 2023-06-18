# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 17:17:27 2021

@author: coss

# Comprobar si hay dos entidades con la misma relacion
# Comprobar si hay redudancia, pero hay un comentario
# Comprobar si hay dos relaciones entre las dos mismas entidades
# Comprobar enfermedades con muchas relaciones del tipo "can be seen"
# Convertir fracturas en enfermedades

"""

from copenmed_tools.python.copenmed_tools import Graph, load_database,\
    add_directional_edges

class Checker():
    def __init__(self, fnPickle="copenmed.pkl", debug=False):
        self.lang_dict, self.lang_dict_info, \
           self.entity_type_dict, self.entity_type_dict_info, \
           self.entity_dict, self.entity_dict_info, \
           self.edge_type_dict, self.edge_type_dict_info, \
           self.list_bidirectional_relations, \
           self.edge_dict, self.edge_dict_info, \
           self.details_dict, self.details_dict_info, \
           self.resources_dict, self.resources_dict_info = \
               load_database(fnPickle)

        add_directional_edges(self.edge_dict, 
                              self.list_bidirectional_relations)
        
        self.graph = Graph(self.entity_dict, self.entity_type_dict, 
                           self.edge_dict, self.edge_type_dict)
        self.graph.createPaths(2,0.25)

    def checkRedundancy(self, weightThreshold=0.9):
        nonRedundant1 = [4,   # Anatomy1 is related to Anatomy2
                         6,   # Treatment1 enhances the effect of Treatment2
                         7,   # Treatment1 inhibits the effect of Treatment2
                         8,   # Disease1 is similar to Disease2
                         9,   # Disease1 may evolve to Disease2
                         10,  # Disease is observed in Anatomy
                         17,  # Symptom1 is similar to Symptom2
                         18,  # Symptom1 cannot be seen with Symptom2
                         19,  # Symptom1 implies Symptom2
                         20,  # Symptom1 may evolve and coexist with Symptom2
                         22,  # Disease1 may evolve and coexist with Disease2
                         24,  # Symptom can be observed in Anatomy
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
                         68,  # Symptom1 can be seen also with Symptom2
                         69,  # Treatment1 can interact with Treatment2
                         70,  # Group1 can interact with Group2
                         71,  # Group can interact with Treatment
                         73,  # A positive testResult implies Symptom
                         78,  # GroupOfDiseases can be treated with GroupOfTreatments
                         79,  # Cause can cause this Group
                         80,  # Group1 is similar to Group2
                         83,  # Symptom is characterized by TestResult
                         84,  # Group may cause symptom
                         85,  # Test is useful to better study this Symptom
                         86,  # Test is useful to diagnose this Group
                         92,  # Risk is associated to Group
                         93,  # Disease may evolve and coexist with Group
                         94,  # Group1 may evolve and cause Group2
                         95,  # Activity may cause Group
                         96,  # Activity may prevent Group
                         97,  # Symptom is also a Group of diseases
                         99,  # Group can cause Symptom
                         101, # Group may evolve to Disease
                         102, # Group1 may evolve to Group2
                         103, # Substance is Treatment
                         104, # Treatment may cause Group
                         105, # Treatment prevents Group
                         108, # Treatment1 is precursor of Treatment2
                         117, # Symptom requires Test
                         125, # Group belongs to the domain of Specialty
                         126, # Disease is more observed in Population
                         128, # Treatment1 is similar to Treatment2
                         129, # Group can be treated with Treatment 
                         133, # Test1 is similar to Test2
                         134, # Anatomy may cause Symptom
                         144, # Group is produced by Anatomy
                         147, # Treatment is related to substance
                         148, # Group can be diagnosed with Test
                         149, # Result can be observed in Anatomy
                         154, # Test is used in Anatomy
                         157, # Cause1 is similar to Cause2
                         158, # Symptom may evolve to Disease
                         159, # Symptom may evolve to Group
                         160, # Substance is produced by Anatomy
                         162, # Substance is related to Group
                         163, # Disease may evolve to Group
                         164, # Substance is related to Disease
                         165, # Group does not cause Symptom
                         167, # Treatment1 suspends Treatment2
                         168, # Treatment1 suspends Group
                         171, # Activity1 is similar to Activity2
                         173, # Activity is related to Substance
                         174, # Pathogen can cause Group
                         176, # Treatment is applied in Anatomy
                         179, # Disease causes Symptom
                         181, # Substance increases this Function
                         183, # Symptom increases Substance
                         185, # Function is performed by Anatomy
                         190, # If Function1 decreases, Function2 increases
                         192, # Treatment has effect on Anatomy
                         194, # Substance has effect on Anatomy
                         201, # GroupOfTreatments is similar to Treatment
                         204, # Group has effect on Anatomy
                         208, # Treatment may cause Disease
                         209, # Treatment prevents Disease
                         214, # Symptom is related to Anatomy
                         215, # Treatment should be avoided if Disease is present
                         216, # Treatment should be avoided if Group is present
                         217, # Treatment1 should be avoided if Treatment2 is given
                         218, # Treatment should be avoided if Group is given
                         220, # Group1 should be avoided if Group2 is given
                         221, # Disease is treated by Activity
                         224, # Treatment1 can be complemented with Treatment2
                         225, # Treatment can be complemented with Group
                         226, # Group can be complemented with Treatment
                         232, # Disease1 should be prevented from evolving to Disease2
                         234, # Group should be prevented from evolving to Disease
                         235, # Group1 should be prevented from evolving to Group2
                         236, # Disease1 may cause Disease2 to get worse
                         238, # Group may cause Disease to get worse
                         241, # Group of treatments may cause Group of diseases
                         242, # Group of treatments may prevent Group of diseases
                         243, # Disease is similar to Group
                         247, # Cause promotes Pathogen
                         251, # Group may evolve and coexist with Disease
                         259, # Symptom is related to Activity
                         260, # Group can only be observed in Population
                         262, # Group1 may cause Group2
                         263, # Treatment is used in Test
                         266, # Cause may require Test
                         268, # Group may cause Cause
                         271, # Cause occurs in Anatomy
                         272, # Group1 is similar to Group2
                         273, # Treatment may prevent Symptom
                         274, # Treatment may cause Symptom
                         278, # Symptom is more observed in Population
                         289, # Cause can be treated with Treatment
                         290, # Cause can be treated by Group
                         291, # Disease1 is seen with Disease2
                         292, # Disease is seen with Group
                         293, # Group is seen with Disease
                         294, # Group1 is seen with Group2
                         298, # Substance is related to Cause
                         301, # GroupOfDiseases requires GroupOfTests
                         303, # Symptom can be the result of Test
                         305, # Activity involves Anatomy
                         313, # This Substance is harmful for this Anatomy
                         315, # Disease is related to Substance
                         316, # Substance is related to Anatomy
                         317, # Feature occurs in Anatomy
                         318, # Feature is related to Anatomy
                         321, # The prevalence of this Disease in this Population is
                         322, # The prevalence of this Group in this Population is
                         324, # Diseases affects Anatomy
                         325, # Group affects Anatomy
                         327, # Group increases Risk
                         334, # Group implies TestResult
                         335, # Substance is used in Test
                         337, # Activity should be avoided with this Disease
                         339, # Disease seldom causes Symptom
                         340, # Group seldom causes Symptom
                         344, # Treatment prevents Activity
                         347, # Pathogen1 transmits or promotes Pathogen2
                         351, # Treatment can be used against Pathogen
                         355, # Pathogen can be confirmed with Test
                         357, # Test is contraindicated if this Disease is present
                         366, # Test1 can be used in combination with Test2
                         368, # Group1 can be used in combination with Group2
                         369, # Group can be used in combination with Test
                         374, # Pathogen gives TestResult
                         376, # GroupOfTreatments should be avoided with this Disease
                         384, # Symptom is related to Substance
                         385, # Cause may cause condition
                         387, # Disease is seen with Condition
                         388, # Disease may evolve to Condition
                         394, # Condition causes Symptom
                         403, # Condition can be treated with Treatment
                         407, # Condition may cause Group
                         421, # Treatment should be avoided if Condition is present
                         431, # Treatment prevents Cause
                         435, # Function may cause Disease
                         441, # Symptom is related to Function
                         445, # Symptom is never observed in Group
                         456, # Group is similar to Disease
                         467, # Group is caused by malfunction of Anatomy
                         468, # Group is related to Substance
                         471, # Group has standard Code
                         485, # Molecule is related to Disease
                         493, # Molecule is underexpressed in Disease
                         503, # CellType is seen in Anatomy
                         504, # CellType is altered in Disease
                         505, # CellType is altered in Group
                         506, # CellType1 interacts with CellType2
                         512, # Pathogen affects CellType
                         520, # Gene is related to Molecule
                         521, # Gene mutation may cause Disease
                         525, # Function is performed by CellType
                         526, # Test may be used to analyze CellType
                         531, # CellType regulates Feature
                         533, # Disease is caused by malfunction of CellType
                         534, # Disease affects CellType
                         535, # Group affects CellType
                         539, # CellType is involved in Disease
                         541, # Substance is related to CellType
                         543, # Anatomy is related to CellType
                         ]
        nonRedundant2 = [4,   # Anatomy1 is related to Anatomy2
                         6,   # Treatment1 enhances the effect of Treatment2
                         8,   # Disease1 is similar to Disease2
                         10,  # Disease is observed in Anatomy
                         11,  # Disease can only be observed in Anatomy
                         16,  # Disease is in the domain of Specialty 
                         17,  # Symptom1 is similar to Symptom2
                         18,  # Symptom1 cannot be seen with Symptom2
                         19,  # Symptom1 implies Symptom2
                         20,  # Symptom1 may evolve and coexist with Symptom2
                         29,  # Symptom can never be observed in Disease
                         30,  # Disease is diagnosed with this Test
                         31,  # Disease can be treated with Treatment
                         32,  # Disease can be treated with this Group
                         45,  # Result is measured with Test
                         49,  # Substance can cause Disease 
                         56,  # Pathogen causes disease
                         57,  # Pathogen does not cause Disease
                         60,  # Activity may cause Symptom
                         63,  # Cause may cause Symptom
                         64,  # Activity1 is similar to Activity2
                         65,  # Substance1 is similar to Substance2
                         66,  # Symptom can be treated with Treatment
                         67,  # Symptom can be treated with Group
                         68,  # Symptom1 can be seen also with Symptom2
                         71,  # Group can interact with Treatment
                         78,  # GroupOfDiseases can be treated with GroupOfTreatments
                         79,  # Cause can cause this Group
                         80,  # Group1 is similar to Group2
                         84,  # Group may cause symptom
                         85,  # Test is useful to better study this Symptom
                         86,  # Test is useful to diagnose this Group
                         92,  # Risk is associated to Group
                         94,  # Group1 may evolve and cause Group2
                         96,  # Activity may prevent Group
                         97,  # Symptom is also a Group of diseases
                         99,  # Group can cause Symptom
                         101, # Group may evolve to Disease
                         102, # Group1 may evolve to Group2
                         104, # Treatment may cause Group
                         117, # Symptom requires Test
                         124, # Test can measure Substance
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
                         149, # Result can be observed in Anatomy
                         154, # Test is used in Anatomy
                         157, # Cause1 is similar to Cause2
                         160, # Substance is produced by Anatomy
                         162, # Substance is related to Group
                         164, # Substance is related to Disease
                         174, # Pathogen can cause Group
                         175, # Anatomy is affected by treatment
                         176, # Treatment is applied in Anatomy
                         177, # Treatment1 is a subtype of Treatment2
                         179, # Disease causes Symptom
                         183, # Symptom increases Substance
                         185, # Function is performed by Anatomy
                         186, # Function increase causes Symptom
                         201, # GroupOfTreatments is similar to Treatment
                         202, # Group has similar effect as Substance
                         204, # Group has effect on Anatomy
                         207, # Disease is caused by malfunction of Anatomy
                         209, # Treatment prevents Disease
                         214, # Symptom is related to Anatomy
                         215, # Treatment should be avoided if Disease is present
                         219, # Group should be avoided if Treatment is given
                         224, # Treatment1 can be complemented with Treatment2
                         232, # Disease1 should be prevented from evolving to Disease2
                         234, # Group should be prevented from evolving to Disease
                         235, # Group1 should be prevented from evolving to Group2
                         236, # Disease1 may cause Disease2 to get worse
                         238, # Group may cause Disease to get worse
                         241, # Group of treatments may cause Group of diseases
                         243, # Disease is similar to Group
                         247, # Cause promotes Pathogen
                         251, # Group may evolve and coexist with Disease
                         259, # Symptom is related to Activity
                         260, # Group can only be observed in Population
                         262, # Group1 may cause Group2
                         266, # Cause may require Test
                         268, # Group may cause Cause
                         271, # Cause occurs in Anatomy
                         272, # Group1 is similar to Group2
                         277, # GroupOfTests is useful to diagnose GroupOfDiseases
                         282, # Test may cause Disease
                         289, # Cause can be treated with Treatment
                         290, # Cause can be treated by Group
                         291, # Disease is related to Substance
                         292, # Disease is seen with Group
                         293, # Group is seen with Disease
                         294, # Group1 is seen with Group2
                         297, # Probability of Group is increased by Risk
                         298, # Substance is related to Cause
                         299, # Group is more observed in Population
                         300, # Population is under the domain of Specialty
                         301, # GroupOfDiseases requires GroupOfTests
                         305, # Activity involves Anatomy
                         313, # This Substance is harmful for this Anatomy
                         315, # Disease is related to Substance
                         316, # Substance is related to Anatomy
                         318, # Feature is related to Anatomy
                         322, # The prevalence of this Group in this Population is
                         324, # Diseases affects Anatomy
                         325, # Group affects Anatomy
                         327, # Group increases Risk
                         339, # Disease seldom causes Symptom
                         340, # Group seldom causes Symptom
                         344, # Treatment prevents Activity
                         347, # Pathogen1 transmits or promotes Pathogen2
                         350, # Group is applied to Population
                         351, # Treatment can be used against Pathogen 
                         355, # Pathogen can be confirmed with Test
                         369, # Group can be used in combination with Test
                         374, # Pathogen gives TestResult
                         375, # Pathogen affects Anatomy
                         394, # Condition causes Symptom
                         425, # Cause1 may cause Cause2
                         426, # Cause is in the domain of Specialty
                         431, # Treatment prevents Cause
                         433, # GroupOfTests is used in Test
                         441, # Symptom is related to Function
                         448, # Group of Tests is similar to Test
                         449, # Group is less observed in Population
                         456, # Group is similar to Disease
                         461, # Device is in the domain of Specialty
                         466, # Symptom is seen with Group
                         467, # Group is caused by malfunction of Anatomy
                         468, # Group is related to Substance
                         471, # Group has standard Code
                         472, # Group can be seen in Population
                         486, # Molecule is related to Group
                         502, # Type1 is a subtype of Type2
                         503, # CellType is seen in Anatomy
                         504, # CellType is altered in Disease
                         505, # CellType is altered in Group
                         506, # CellType1 interacts with CellType2
                         521, # Gene mutation may cause Disease
                         526, # Test may be used to analyze CellType
                         535, # Group affects CellType
                         536, # Group is observed in CellType
                         537, # Symptom is related to CellType
                         541, # Substance is related to CellType
                         543, # Anatomy is related to CellType
                         544, # CellType is involved in Group
                         548, # Anatomy produces Substance
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
                     (73,   # A positive testResult implies Symptom
                      45,   # Result is measured with Test
                      85),  # Test is useful to better study this Symptom
                     (93,   # Disease may evolve and coexist with Group,
                      77,   # Disease belongs to Group
                      76),  # Group1 is a subgroup of Group2
                     (118,  # Symptom requires Group
                      117,  # Symptom requires Test
                      116), # Test belongs to Group
                     (130,  # Group can only be observed in Anatomy
                      131,  # Group can be observed in Anatomy
                      3),   # Anatomy1 is part of Anatomy2
                     (131,  # Group can be observed in Anatomy
                      131,
                      3),   # Anatomy1 is part of Anatomy2
                     (154,  # Test is used in Anatomy
                      116,  # Test belongs to Group
                      341), # Group is used in Anatomy
                     (176,  # Treatment is applied in Anatomy
                      192,  # Treatment has effect on Anatomy
                      3),   # Anatomy1 is part of Anatomy2
                     (179,  # Disease causes Symptom
                      77,   # Disease belongs to Group
                      97),  # Symptom is also a Group of diseases
                     (185,  # Function is performed by Anatomy
                      186,  # Function increase causes Symptom
                      24),  # Symptom can be observed in Anatomy
                     (192,  # Treatment has effect on Anatomy
                      5,    # Treatment belongs to the GroupOfTreatments
                      204), # Group has effect on Anatomy
                     (192,  # Treatment has effect on Anatomy
                      192,  
                      3),   # Anatomy1 is part of Anatomy2
                     (207,  # Disease is caused by malfunction of Anatomy
                      77,   # Disease belongs to Group
                      130), # Group can only be observed in Anatomy
                     (209,  # Treatment prevents Disease
                      5,    # Treatment belongs to the GroupOfTreatments
                      206), # Group may cause Disease
                     (269,  # Pathogen is more observed in Population
                      56,   # Pathogen causes disease
                      126), # Disease is more observed in Population
                     (293,  # Group is seen with Disease
                      333,  # Disease implies TestResult
                      88),  # Result is only observed in this Group
                     (324,  # Diseases affects Anatomy
                      324,
                      3),   # Anatomy1 is part of Anatomy2
                     (325,  # Group affects Anatomy
                      131,  # Group can be observed in Anatomy
                      3),   # Anatomy1 is part of Anatomy2
                     (373,  # Cause cannot be treated with Group
                      372,  # Cause cannot be treated by Treatment
                      5),   # Treatment belongs to the GroupOfTreatments
                     (467,  # Group is caused by malfunction of Anatomy
                      76,   # Group1 is a subgroup of Group2
                      130), # Group can only be observed in Anatomy
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
                     (242,  # Group of treatments may prevent Group of diseases
                      447,  # Group prevents Disease
                      77),  # Disease belongs to Group
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
                     (340,  # Group seldom causes Symptom
                      76,   # Group1 is a subgroup of Group2
                      340), # Group seldom causes Symptom
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
                        edgeType = path.getEdgeTypes()[0]
                        comment = path.getFirstComment(self.edge_dict)
                        if not comment:                        
                            directPathsTypes.append(edgeType)
                            directPaths.append(path)
                            maxWeight1=max(maxWeight1,path.getLastWeight()[-1])
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
        DISEASE = self.graph.id_dict['Disease']
        GROUPOFDISEASES = self.graph.id_dict['GroupOfDiseases']
        for idEdge in self.edge_dict:
            edge = self.edge_dict[idEdge]
            idEntity = edge[0]
            if idEntity in self.entity_dict:
                entityType = self.entity_dict[idEntity][1]
                if not entityType==DISEASE and not entityType==GROUPOFDISEASES:
                    continue
                if not idEntity in specialty_dict:
                    specialty_dict[idEntity]  = 0
                edge_name = edge[3]
                inTheDomain = "Specialty" in edge_name
                if inTheDomain:
                    specialty_dict[idEntity] = 1
            else:
                print("Problema inespecifico con id=%d"%idEntity)
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
        DISEASE = self.graph.id_dict['Disease']
        GROUPOFDISEASES = self.graph.id_dict['GroupOfDiseases']
        for idEdge in self.edge_dict:
            edge = self.edge_dict[idEdge]
            idEntity = edge[0]
            if idEntity in self.entity_dict:
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
            else:
                print("Problema inespecifico con id=%d"%idEntity)
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
        SYMPTOM = self.graph.id_dict['Symptom']
        for idEntity in self.details_dict:
            if idEntity in self.entity_dict:
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
            if not idEntity1 in self.entity_dict or \
               not idEntity2 in self.entity_dict:
                   continue
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
        whiteList = [
            (169,11329, "Symptom is seen with Group"),
            (9830, 14557, "Symptom is seen with Group"),
            (10746, 14557, "Symptom is seen with Group"),
            (9902, 14561, "Symptom is seen with Group")
            ]
        def checkWhiteList(idEntity1, idEntity2, relationName):
            inList = False
            for id1, id2, relName in whiteList:
                if relName in relationName and \
                    (id1==idEntity1 and id2==idEntity2 or \
                     id1==idEntity2 and id2==idEntity1):
                    inList = True
                    break
                
            return inList
        
        print("Analisis de relaciones NO USAR: =============================")
        Ncount = 0
        for keyEdge in self.edge_dict:
            edge = self.edge_dict[keyEdge]
            if "NO USAR" in edge[3]:
                idEntity1 = edge[0]
                idEntity2 = edge[1]
                if idEntity1 in self.entity_dict and idEntity2 in self.entity_dict:
                    if not checkWhiteList(idEntity1, idEntity2, edge[3]):
                        print("%s (%d) -> %s (%d) [%s]"%(self.entity_dict[idEntity1][0],
                                                         idEntity1,
                                                         self.entity_dict[idEntity2][0],
                                                         idEntity2,
                                                         edge[3]))
                        Ncount+=1
        print("Numero de relaciones que no deben usarse: %d"%Ncount)

    def checkImageData(self):
        Ncount=0
        print("Analisis de data:image =============================")
        toPrint = ""
        for idEntity in self.resources_dict:
            resources=self.resources_dict[idEntity]
            for url in resources.URL:
                if "data:image" in url:
                    toPrint+="%d "%idEntity
                    Ncount+=1
        print(toPrint)
        print("Numero de data:image: %d"%Ncount)
            
    def checkHighlightedText(self):
        Ncount=0
        print("Analisis de highlighted text =============================")
        for idEntity in self.resources_dict:
            resources=self.resources_dict[idEntity]
            for idResource, url in resources.URL.iteritems():
                if "#:~:text" in url:
                    idx=url.index("#:~:text")
                    cleanUrl=url[0:idx]
                    sql = "UPDATE recurso SET URL='%s' WHERE IdEntidad=%d and URL LIKE '%%%s%%';"%\
                          (cleanUrl, idEntity, url)
                    print(sql)
                    Ncount+=1
        print("Numero de highlighted text: %d"%Ncount)
    
    def checkRelationsToPoblacionGeneral(self):
        POP_GENERAL = 641 # Poblacion general
        PREVALENCE_DISEASE = 321
        PREVALENCE_GROUP = 322
        PROBABILITY = 323
        IS_SUBGROUP = 200
        Ncount=0
        
        whiteList = [47, 499, 1127, 1661, 2002, 3629, 3681, 7796, 10086]
        
        print("Analisis de relaciones con poblacion general =============================")
        nodeGeneral = self.graph.getNode(POP_GENERAL)
        for idEntityTo, idEdgeType, idEdge in nodeGeneral.outgoingEdges:
            print("Poblacion general (641) -> %s (%d)"%(
                                             self.entity_dict[idEntityTo][0],
                                             idEntityTo))
        for idEntityFrom, idEdgeType, idEdge in nodeGeneral.incomingEdges:
            ok = idEdgeType==PREVALENCE_DISEASE or idEdgeType==PREVALENCE_GROUP or \
                 idEdgeType==PROBABILITY
            if idEdgeType==IS_SUBGROUP:
                ok = ok or (self.entity_dict[idEntityFrom][2]=="Population")
            ok = ok or idEntityFrom in whiteList
            if not ok:
                print("%s (%d)"%(self.entity_dict[idEntityFrom][0],
                                 idEntityFrom))
                Ncount+=1
        print("Numero de relaciones incorrectas con poblacion general: %d"%Ncount)
    
    def checkHighPrevalences(self):
        PREVALENCE_DISEASE = 321
        PREVALENCE_GROUP = 322
        Ncount=0
        
        whiteList = [ (2158, 435), (18, 641), (125, 5441), (268, 641),
            (3038, 1707), (3043, 3647), (3039, 4407), (341, 641), (3314, 641),
            (2019, 641), (2064, 1725), (401, 641), (3606, 641), (3614, 641),
            (3627, 641), (2155, 435), (3696, 641), (2575, 641), (3708, 641),
            (3718, 641), (3721, 641), (3730, 641), (2165, 435), (2580, 641),
            (2582, 641), (192, 3587), (192, 1707), (184, 7602), (184, 1483),
            (2335, 641), (1060, 5477), (2342, 1901), (345, 5637), (3938, 641),
            (671, 1725), (4021, 641), (4109, 5637), (4122, 641), (4146, 641),
            (701, 5299), (4166, 641), (1103, 1483), (4257, 641), (895, 3842),
            (895, 641), (1183, 434), (4830, 2184), (4857, 1483), (4492, 641),
            (5524, 1483), (2775, 641), (1193, 641), (1712, 8791), (1805, 3246),
            (1880, 641), (1927, 3246), (1928, 435), (1945, 1483), (1991, 434),
            (5842, 641), (1912, 439), (1912, 5298), (252, 641), (184, 641),
            (184, 4099), (1880, 1901), (500, 3519), (500, 3647), (500, 641),
            (512, 1707), (770, 641), (959, 641), (1785, 641), (1913, 641),
            (1964, 641), (1971, 641), (2598, 641), (1374, 641), (2615, 641),
            (2617, 641), (1785, 1707), (2756, 641), (2773, 641), (2793, 641),
            (533, 641), (1448, 641), (7041, 10222), (5244, 641), (5275, 10331),
            (5402, 10352), (2591, 641), (116, 641), (6096, 641), (10163, 1073),
            (7199, 641), (6553, 641), (6801, 641), (7234, 641), (1060, 1820),
            (1060, 10579), (8883, 641), (8904, 641), (8992, 435), (9204, 641),
            (8252, 435), (10161, 3273), (8970, 641), (10304, 10321),
            (9802, 3988), (10285, 641), (663, 641), (9260, 641), (7539, 641),
            (7249, 641), (8591, 641), (7358, 641), (10269, 435), (10269, 3521),
            (774, 641), (3320, 10322), (9802, 641), (9920, 641), (5349, 641),
            (6124, 641), (10685, 641), (10229, 641), (10891, 641),
            (10751, 641), (10756, 641), (11257, 641), (11271, 641),
            (10373, 641), (4381, 1901), (4381, 3246), (6436, 3246),
            (6436, 1901), (11374, 641), (11404, 641), (11413, 5615),
            (11579, 3273), (11638, 641), (11931, 641), (12025, 641),
            (12166, 641), (345, 641), (5137, 641), (111, 641), (125, 641),
            (251, 641), (188, 641), (2155, 641), (1991, 641), (1928, 641),
            (838, 641), (2342, 641), (1103, 435), (1103, 4099), (1042, 10363),
            (1805, 641), (1805, 3109), (523, 641), (773, 641), (8252, 2184),
            (11289, 641), (10161, 641), (9213, 1707), (13576, 641),
            (13772, 641), (11934, 641), (12028, 641), (14002, 641),
            (14002, 7603), (12100, 641), (14221, 641), (14221, 3982),
            (12514, 641), (13019, 641), (14490, 3998), (13536, 641),
            (13567, 641), (13454, 641), (13987, 641), (13989, 641),
            (13985, 641), (13990, 641), (13991, 641), (13995, 641),
            (610, 14908), (14561, 641), (13986, 641), (14192, 641),
            (13932, 641), (14557, 641), (13656, 641)
            ]
        
        print("Analisis de prevalencias muy altas =============================")
        for idEdge in self.edge_dict:
            idEntityFrom, idEntityTo, idEdgeType, edgeName, _, force = \
                self.edge_dict[idEdge]
            if (idEdgeType==PREVALENCE_DISEASE or idEdgeType==PREVALENCE_GROUP) and \
                force>0.1:
                if (idEntityFrom, idEntityTo) not in whiteList:
                    print("%s (%d) -> %s (%d): Prevalencia: %f"%\
                          (self.entity_dict[idEntityFrom][0], idEntityFrom,
                           self.entity_dict[idEntityTo][0], idEntityTo,
                           force))
                    Ncount+=1
        print("Numero de prevalencias muy altas: %d"%Ncount)
    
    def checkMultipleRelationships(self):
        Ncount=0
        whiteList=[
            (95, # Activity may cause Group
             338) # Activity should be avoided with this Group
            ]
        print("Analisis de multiples relaciones ==========================")
        for idEntity in range(self.graph.getNodeMax()):
            node = self.graph.getNode(idEntity)
            if node is None:
                continue
    
            # For all outgoing edges
            out_dict={}
            out_dict_edgeTypes={}
            for idEntityTo, idEdgeType, idEdge in node.outgoingEdges:
                if not idEntityTo in self.entity_dict:
                    continue
                if idEntityTo not in out_dict:
                    out_dict[idEntityTo]=1
                    out_dict_edgeTypes[idEntityTo]=[idEdgeType]
                else:
                    out_dict[idEntityTo]+=1
                    out_dict_edgeTypes[idEntityTo]+=[idEdgeType]
            
            # Check multiplicity
            for idEntityTo in out_dict:
                if out_dict[idEntityTo]>1:
                    out_dict_edgeTypes[idEntityTo].sort()
                    if not out_dict_edgeTypes[idEntityTo] in whiteList:
                        print("%s (%d) -> %s (%d) Num.Relaciones=%d (%s)"%\
                              (self.entity_dict[idEntity][0], idEntity,
                               self.entity_dict[idEntityTo][0], idEntityTo,
                               out_dict[idEntityTo], 
                               str(out_dict_edgeTypes[idEntityTo])))
                        Ncount+=1
        print("Numero de relaciones multiples=%d"%Ncount)

if __name__=="__main__":                                
    checker = Checker()
    checker.checkRedundancy()
    checker.checkSpecialty()
    checker.checkPrevalence()
    checker.checkDescriptionLevel()
    checker.checkNumberOfEdges()
    checker.checkEdgeMistakes()
    checker.checkNoUsar()
    checker.checkImageData()
    checker.checkHighlightedText()
    checker.checkRelationsToPoblacionGeneral()
    checker.checkHighPrevalences()
    checker.checkMultipleRelationships()
    

