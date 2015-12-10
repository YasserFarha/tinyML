#!/usr/bin/env python
import keras
from keras.models import Sequential, Graph
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
import numpy as np
import theano, sys

import pandas as pd

def fn(xt) :
  return np.sin(xt) #+ 2*np.cos(np.multiply(2.1, xt)) - 1.4*np.cos(3.4*np.sin(np.multiply(xt, xt)))

xt = np.random.rand(10000, 1)
xt = np.multiply(xt, 10)
yt = fn(xt)

class LossHistory(keras.callbacks.Callback):
    global dbt 
    def on_train_begin(self, logs={}):
        self.losses = []

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))


dx = pd.read_csv("/home/jhallard/linux/tinyML/testXX.csv")
dy = pd.read_csv("/home/jhallard/linux/tinyML/testYY.csv")
xt = dx.values.copy()
xt = xt[:, -1:]
print str(xt)

yt = dy.values.copy()
yt = yt[:, -1:]
print str(yt)


losscb = LossHistory()

model = Sequential()
model.add(Dense(output_dim=18, input_dim=1))
model.add(Activation('relu'))
model.add(Dense(output_dim=64, init='uniform'))
# model.add(Dropout(0.1))
model.add(Activation('relu'))
# model.add(Dropout(0.1))
model.add(Dense(1, init='uniform'))
model.compile(loss='mse', optimizer='rmsprop')

print model.to_json()

model.fit(xt, yt, nb_epoch=460, batch_size=360, validation_split=0.2, callbacks=[losscb])

print str([str(x) for x in losscb.losses])

# for x in [(xt[p], yt[p]) for p in range(len(xt))] :
    # print str(x[0]) + " --> " + str(model.predict(np.array([x[0]]))) + " --> " + str(x[1])

