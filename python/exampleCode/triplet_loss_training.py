# -*- coding: utf-8 -*-
"""
Created on Sat May  4 16:01:26 2024

@author: coss

Inspired by https://github.com/13muskanp/Siamese-Network-with-Triplet-Loss/blob/master/Siamese%20Network%20with%20Triplet%20Loss.ipynb

"""

import glob
import numpy as np
import pickle
import os
import tensorflow as tf
import tensorflow.keras as keras
import random

def chooseRandom(N, i):
    while True:
        j = random.randint(0, N-1)
        if j != i:
            break
    return j

def constructEmbeddingNetwork(inputSize=512):
    model = keras.Sequential([
        keras.layers.Dense(inputSize, activation='relu'),
        keras.layers.Dense(inputSize, activation='relu'),
        keras.layers.Dense(inputSize, activation='linear'),
    ])
    return model

def constructSiameseNetwork(inputSize):
    embedding_model = constructEmbeddingNetwork(inputSize)
    inp_anc = keras.layers.Input(shape=(inputSize,))
    inp_pos = keras.layers.Input(shape=(inputSize,))
    inp_neg = keras.layers.Input(shape=(inputSize,))
    
    emb_anc = embedding_model(inp_anc)
    emb_pos = embedding_model(inp_pos)
    emb_neg = embedding_model(inp_neg)
    
    outp = keras.layers.concatenate([emb_anc, emb_pos, emb_neg], axis=1) 
    
    siameseNetwork=keras.models.Model([inp_anc, inp_pos, inp_neg], outp)
    return siameseNetwork, embedding_model

def data_generator(dataI, dataJ, batch_size=32):
    num_samples = dataI.shape[0]
    num_batches = num_samples // batch_size
    
    while True:
        for _ in range(num_batches):
            anchor_batch = dataI[:batch_size]
            positive_batch = dataI[np.random.choice(num_samples, batch_size)]
            negative_batch = dataJ[np.random.choice(len(dataJ), batch_size)]
            
            x_batch = [anchor_batch, positive_batch, negative_batch]
            y_batch = np.zeros((batch_size, 3 * dataI.shape[1]))
            
            yield x_batch, y_batch
   
def triplet_loss(alpha, emb_dim):
    def loss(y_true, y_pred):
        anc, pos, neg = y_pred[:, :emb_dim], \
                        y_pred[:, emb_dim:emb_dim*2], \
                        y_pred[:, 2*emb_dim:]
        dp = tf.reduce_mean(tf.square(anc - pos), axis=1)
        dn = tf.reduce_mean(tf.square(anc - neg), axis=1)
        
        return tf.maximum(dp-dn+alpha, 0.)
    return loss

if __name__=="__main__":
    inputSize = 512
    Nblock = 2500
    Nrounds=5
    contentList = [idURL for idURL in 
              glob.glob(os.path.join('data','recursos','*','content.npy'))]
    
    siameseModel, embedding_model = constructSiameseNetwork(inputSize)
    siameseModel.summary()
    siameseModel.compile(optimizer='adam', 
                             loss=triplet_loss(alpha=0.2, emb_dim=inputSize))
    
    fnEmbedding = 'embedding_model_weights.h5'
    if os.path.exists(fnEmbedding):
        embedding_model.load_weights(fnEmbedding)

    N=len(contentList)    
    b=0
    fnAux = "triplet_loss_inter.pkl"
    if os.path.exists(fnAux):
        with open(fnAux,'rb') as f:
            it0, i0 = pickle.load(f)
    else:
        it0=0
        i0=0
    yloss=[]
    for it in range(it0, Nrounds):
        for i in range(i0, N):
            dataI = np.load(contentList[i])
            j=chooseRandom(N, i)
            dataJ = np.load(contentList[j])

            batch_size=min(32,len(dataI),len(dataJ))
            if batch_size==0:
                continue
            history = siameseModel.fit(
                             data_generator(dataI, dataJ, batch_size), 
                             epochs=1, 
                             steps_per_epoch=dataI.shape[0] // batch_size,
                             verbose=False)
            last_loss = history.history['loss'][-1]
            print("Item %d (%d): loss=%f"%(i,b,last_loss))
            yloss.append(last_loss)
            b+=1
            if b>=Nblock:
                break
        if b>=Nblock:
            break
        else:
            i0=0

    embedding_model.save_weights(fnEmbedding)
    it0=it
    i0=i
    with open(fnAux,'wb') as f:
        pickle.dump([it0, i0], f)
    
    print("Avg loss=%f"%np.mean(yloss))
#    import matplotlib.pyplot as plt
#    plt.plot(yloss)