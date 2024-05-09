# -*- coding: utf-8 -*-
"""
Created on Thu May  9 18:56:38 2024

@author: coss
"""

import glob
import numpy as np
import os
import tensorflow.keras as keras

def constructEmbeddingNetwork(inputSize=512):
    model = keras.Sequential([
        keras.layers.Dense(inputSize, activation='relu'),
        keras.layers.Dense(inputSize, activation='relu'),
        keras.layers.Dense(inputSize, activation='linear'),
    ])
    return model

def constructTruncatedNetwork(inputSize):
    embedding_model = constructEmbeddingNetwork(inputSize)
    inp_anc = keras.layers.Input(shape=(inputSize,))
    emb_anc = embedding_model(inp_anc)
    fullNetwork=keras.models.Model(inp_anc, emb_anc)
    embedding_model.load_weights('embedding_model_weights.h5')

    return fullNetwork

if __name__=="__main__":
    inputSize = 512
    embedding_model = constructEmbeddingNetwork(inputSize)

    contentList = [idURL for idURL in 
              glob.glob(os.path.join('data','recursos','*','content.npy'))]
    for fnContent in contentList:
        fnContent2 = fnContent.replace('content.npy','contentEmbedding.npy')
        if not os.path.exists(fnContent2):
            dataI = np.load(fnContent)
            if dataI.shape[0]==0:
                continue
            print(fnContent2)
            np.save(fnContent2, embedding_model(dataI))