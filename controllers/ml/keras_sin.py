#!/usr/bin/env python
from keras.models import Sequential, Graph
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
import numpy as np
import theano, sys

def fn(xt) :
  return 3*np.sin(xt) # + 2*np.cos(np.multiply(2.1, xt)) - 1.4*np.cos(3.4*np.sin(np.multiply(xt, xt)))

xt = np.random.rand(10000, 1)
xt = np.multiply(xt, 10)
yt = fn(xt)

model = Sequential()
model.add(Dense(18, input_dim=1))
model.add(Activation('tanh'))
model.add(Dense(64, init='uniform'))
model.add(Activation('relu'))
model.add(Dense(1, init='uniform'))
model.compile(loss='mean_squared_error', optimizer='rmsprop')
model.fit(xt, yt, nb_epoch=460, batch_size=36)

for x in [(xt[p], yt[p]) for p in range(len(xt))] :
    print str(x[0]) + " --> " + str(model.predict(np.array([x[0]]))) + " --> " + str(x[1])

