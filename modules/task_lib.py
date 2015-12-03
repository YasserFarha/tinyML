#!/usr/bin/env python

from keras.models import Sequential, Graph
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import SGD
import numpy as np
import theano, sys, json, datetime

def compile_model(mid, tid) :
    with open("/home/jhallard/linux/conf.dat", 'rw+') as fh : 
        fh.write("here stage 1");
    dbmodel = db(db.models.id == mid).select().first()
    arch = json.loads(model.arch)
    layers = arch['layer_dicts']

    with open("/home/jhallard/linux/conf.dat", 'rw+') as fh : 
        fh.write("here stage 2");
    mdl = models.Sequential()
    
    if not len(layers): return False
    mdl = add_layer(mdl, layers[0], first=True, last=len(layers) == 1)
    for i in range(1, len(layers)-1) :
        with open("/home/jhallard/linux/conf.dat", 'rw+') as fh : 
            fh.write("here stage 3");
        mdl = add_layer(mdl, layers[i])
    if not len(layers) <= 1:
        mdl = add_layer(mdl, layers[len(layers)-1], first=False, last=True)

    mdl.compile(loss=mdl.loss, optimizer=mdl.optimizer)
    with open("/home/jhallard/linux/conf.dat", 'rw+') as fh : 
        fh.write("here stage 4");

    mdl.status = idle
    mdl.updated_at = datetime.datetime.now()
    mdl.compiled = True
    db.commit(mdl)

    dbt = db(db.transactions.uuid == tid).select().first()
    dbt.status = "success"
    dbt.finished_at = datetime.datetime.now()

    db.commit(dbt)


def add_layer(mdl, ld, first=False, last=False) :
    if ld['type'] == 'dense' :
        if first : mdl.add(Dense(ld['nodes'], input_dim=ld['num_inp'], init=ld['init']))
        if last : mdl.add(Dense(ld['nodes'], output_dim=ld['output_dim'],init=ld['init']))
        else :  mdl.add(Dense(ld['nodes']), init=ld['init'])
            

    elif ld['type'] == 'convolutional' :
        if first : mdl.add(Convolutional1D(ld['nodes'], filter_length=3, input_dim=ld['num_inp'], init=ld['init']))
        elif last : mdl.add(Convolutional1D(ld['nodes'], filter_length=3, input_dim=ld['num_inp'], init=ld['init']))
        else: mdl.add(Convolutional1D(ld['nodes'], filter_length=3, input_dim=ld['num_inp'], init=ld['init']))

    elif ld['type'] == 'timedistdense' :
        if first : mdl.add(TimeDistributedDense(ld['nodes'], input_dim=ld['num_inp'], init=ld['init']))
        elif last : mdl.add(TimeDistributedDense(ld['num_out'], init=ld['init']))
        else: mdl.add(TimeDistributedDense(ld['nodes'], init=ld['init']))

    elif ld['type'] == 'autoencoder' :
        if first: 
            mdl.add(AutoEncoder(
                          Dense(ld['nodes'], input_dim=ld['num_inp'], init=ld['init']),
                          Dense(ld['nodes'], input_dim=ld['num_inp'], init=ld['init'])))
        elif last: 
            mdl.add(AutoEncoder(
                          Dense(ld['output_dim'], init=ld['init']), 
                          Dense(ld['output_dim'], init=ld['init'])))
        else: 
            mdl.add(AutoEncoder(
                          Dense(ld['nodes'], init=ld['init']), 
                          Dense(ld['nodes'], init=ld['init'])))

    if ld['activation'] and ld['activation'] != 'none' :
        mdl.add(Activation(ld['activation']))

    return mdl


    

