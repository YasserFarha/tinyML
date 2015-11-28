#!/usr/bin/env python
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
import numpy as np

model = Sequential()
# Dense(64) is a fully-connected layer with 64 hidden units.
# in the first layer, you must specify the expected input data shape:
# here, 20-dimensional vectors.
model.add(Dense(64, input_dim=20, init='uniform'))
model.add(Activation('tanh'))
model.add(Dropout(0.5))
model.add(Dense(64, init='uniform'))
model.add(Activation('tanh'))
model.add(Dropout(0.5))
model.add(Dense(2, init='uniform'))
model.add(Activation('softmax'))

sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='mean_squared_error', optimizer=sgd)

ws = np.random.rand(20, 2)
print "weights : " + str(ws)

xt = np.random.rand(10000, 20)
yt = np.dot(xt, ws)

print yt

X_train = xt
y_train = yt
X_test  = np.random.rand(10000, 20)
y_test  = np.dot(X_test, ws)

model.fit(X_train, y_train, nb_epoch=20, batch_size=16)
score = model.evaluate(X_test, y_test, batch_size=16, show_accuracy=True)

print score

predictions = model.predict(X_test)

print predictions

for x in range(len(predictions)) :
    print str(predictions[x]) + ", "+  str(y_test[x])
