#!/usr/bin/env python
from keras.models import Sequential, Graph
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
import numpy as np
import theano, sys

NUM_TRAIN = 100000
NUM_TEST = 10000
INDIM = 3
EPOCHS=20

mn = 0.1
mx= 0.00001

def myrand(a, b) :
    return (b)*(np.random.random_sample()-0.5)+a

def get_data(count, ws, xno, bounds=100, rweight=0.0) :
    xt = np.random.rand(count, len(ws))
    xt = np.multiply(bounds, xt)
    yt = np.random.rand(count, 1)
    ws = np.array(ws, dtype=np.float)
    xno = np.array([float(xno) + rweight*myrand(-mn, mn) for x in xt], dtype=np.float)
    yt = np.dot(xt, ws)
    yt = np.add(yt, xno)

    return (xt, yt)



if __name__ == '__main__' :
    if len(sys.argv) > 1 :
       EPOCHS = int(sys.argv[1])
       XNO = float(sys.argv[2])
       WS = [float(x) for x in sys.argv[3:]]
       mx = max([abs(x) for x in (WS+[XNO])])
       mn = min([abs(x) for x in (WS+[XNO])])
       mn = min(1, mn)
       WS = [float(x)/mx for x in WS]
       XNO = float(XNO)/mx
       INDIM = len(WS)
    else :
        INDIM = 3
        WS = [2.0, 1.0, 0.5]
        XNO = 2.2

    X_test, y_test = get_data(10000, WS, XNO, 10000, rweight=0.0)
    X_train, y_train = get_data(100000, WS, XNO, 10000, rweight=0.3)
    # graph model with one input and two outputs
    graph = Graph()
    graph.add_input(name='input', input_shape=(INDIM,))
    graph.add_node(Dense(1, init='lecun_uniform'), name='dense1', input='input')
    graph.add_output(name='output1', input='dense1')

    graph.compile('rmsprop', {'output1':'mse'})
    history = graph.fit({'input':X_train, 'output1':y_train}, nb_epoch=EPOCHS, shuffle="dense", validation_split=0.1)

    predict_data  = X_test#np.random.rand(100*100, 2)
    predictions = graph.predict({"input" : predict_data})

    avgerr = 0.0
    for x in range(len(predict_data)) :
        err = abs((predictions['output1'][x]-y_test[x])/y_test[x])
        avgerr += err
        if x % 50 == 0 :
            print "%s --> %s | error(%s)" % (str(predict_data[x]), str(predictions['output1'][x]), str(err))

    avgerr = avgerr / float(len(predict_data))

    nodes = graph.nodes

    node = nodes['dense1'].get_weights()
    foundws = np.append(node[0],node[1]).tolist()

    rwts = ["{0:.2f}".format(x*mx) for x in WS+[XNO]]
    fwts = ["{0:.2f}".format(x*mx) for x in foundws]
    print "real/found weights :"
    for x in range(len(rwts)) :
      print "%s | %s " % (rwts[x].ljust(10), fwts[x].ljust(10))
    print "average error : %s" % str(avgerr)
