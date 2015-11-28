#!/usr/bin/env python
from keras.models import Sequential, Graph
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
import numpy as np
import theano

X_train = np.zeros((100*100, 2), dtype=theano.config.floatX)
y_train=  np.zeros((100*100, 1), dtype=theano.config.floatX)

for t in range(100) :
    for u in range(100) :
        X_train[t*100+u] = [t, u]

for i in range(len(X_train)) :
    y_train[i] =  2*X_train[i][0] + 1*X_train[i][1] + 0.5

print y_train


X_test= np.random.rand(100*100, 2)
for x in range(len(X_test)) :
    X_test[x] = X_test[x]*100
y_test= np.random.rand(100*100, 2)
for i in range(len(X_test)) :
    y_test[i] =  2*X_test[i][0] + 1*X_test[i][1] + 0.5

model = Sequential()
# Dense(64) is a fully-connected layer with 64 hidden units.
# in the first layer, you must specify the expected input data shape:
# here, 20-dimensional vectors.
model.add(Dense(2, input_dim=2, init='uniform'))
model.add(Activation('tanh'))
model.add(Dropout(0.1))
model.add(Dense(64, init='uniform'))
model.add(Activation('tanh'))
model.add(Dropout(0.5))
model.add(Dense(1, init='uniform'))
model.add(Activation('softmax'))

sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='mse', optimizer='rmsprop')

model.fit(X_train, y_train, shuffle="batch", show_accuracy=True)
score, acc = model.evaluate(X_test, y_test, batch_size=16, show_accuracy=True)
print score
print acc

predict_data = np.random.rand(100*100, 2)
predictions = model.predict(predict_data)

for x in range(len(predict_data)) :
    print "%s --> %s" % (str(predict_data[x]), str(predictions[x]))
