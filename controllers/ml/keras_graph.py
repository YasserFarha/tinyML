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


# graph model with one input and two outputs
graph = Graph()
graph.add_input(name='input', input_shape=(2,))
graph.add_node(Dense(2), name='dense1', input='input')
graph.add_node(Dense(2), name='dense2', input='input')
graph.add_node(Dense(4), name='dense3', inputs=['dense1', 'dense2'])
graph.add_node(Dense(1), name='dense4', input='dense3')
graph.add_output(name='output1', input='dense4')

sgd = SGD(lr=0.1, decay=1e-6, momentum=0.9, nesterov=True)
# graph.compile(loss={'output1' : 'mse'}, optimizer='rmsprop')

graph.compile('rmsprop', {'output1':'mse'})
history = graph.fit({'input':X_train, 'output1':y_train}, nb_epoch=100)

predict_data  = X_test #np.random.rand(100*100, 2)
predictions = graph.predict({"input" : predict_data})

for x in range(len(predict_data)) :
    print "%s --> %s | error(%s)" % (str(predict_data[x]), str(predictions['output1'][x]),
                                    str(abs(predictions['output1'][x]-(2*predict_data[x][0] + 1*predict_data[x][1] + 0.5))))
