#!/usr/bin/env python
from gluon.scheduler import Scheduler
import task_lib, json
scheduler = Scheduler(db)

from keras.models import Sequential, Graph
from keras.layers.core import Dense, Dropout, Activation, TimeDistributedDense, AutoEncoder
from keras.layers.convolutional import Convolution1D
from keras.optimizers import SGD
import numpy as np
import theano, sys, json, datetime
from sys import stderr

def compile_model(mid, tid) :
    try :
        stderr.write("here stage 1");
        dbmodel = db(db.models.id == mid).select().first()
        arch = json.loads(dbmodel.arch)
        layers = arch['layer_dicts']

        stderr.write( "here stage 2")
        mdl = Sequential()
        stderr.write( "here stage 3")
        
        if not len(layers): return False
        mdl = add_layer(mdl, layers[0], arch, first=True, last=len(layers) == 1)
        for i in range(1, len(layers)-1) :
            stderr.write("here stage 4")
            mdl = add_layer(mdl, layers[i], arch)
        if not len(layers) <= 1:
            mdl = add_layer(mdl, layers[len(layers)-1], arch, first=False, last=True)

        mdl.compile(loss=arch['lossfn'], optimizer=arch['optimizer'])
        stderr.write("here stage 5")

        dbmodel.update_record(
            status = "idle",
            arch_json = mdl.to_json(),
            updated_at = datetime.datetime.now(),
            compiled = True
       ) 
        db.commit()
        stderr.write("here stage 5")

        dbt = db(db.transactions.id == int(tid)).select().first()
        dbt.update_record(status = "success",
            finished_at = datetime.datetime.now())

        stderr.write(str(dbmodel))
        stderr.write(str(dbt))

        db.commit()
    except Exception as e :
        stderr.write("Compile Failed : " + str(e))
        dbmodel.update_record(
            status = "broken",
            arch_json = mdl.to_json(),
            updated_at = datetime.datetime.now(),
            compiled = False 
       ) 
        db.commit()
        stderr.write("here stage 5")

        dbt = db(db.transactions.id == int(tid)).select().first()
        dbt.update_record(status = "failed",
            finished_at = datetime.datetime.now())
        db.commit()



def add_layer(mdl, ld, arch, first=False, last=False) :
    num_inp = arch['num_inp']
    num_out = arch['num_out']
    if ld['type'] == 'dense' :
        if first : mdl.add(Dense(ld['nodes'], input_dim=num_inp, init=ld['init']))
        if last : mdl.add(Dense(output_dim=num_out,init=ld['init']))
        else :  mdl.add(Dense(ld['nodes'], init=ld['init']))
            

    try :
        if ld['type'] == 'convolutional' :
            stderr.write("Adding convolutional layer")
            if first : mdl.add(Convolution1D(ld['nodes'], filter_length=3, input_dim=num_inp, init=ld['init']))
            elif last : mdl.add(Convolution1D(num_out, filter_length=3, init=ld['init']))
            else: mdl.add(Convolution1D(ld['nodes'], filter_length=3, input_dim=ld['num_inp'], init=ld['init']))
    except Exception as e :
        stderr.write(str(e))

    try :
        if ld['type'] == 'timedistdense' :
            if first : mdl.add(TimeDistributedDense(ld['nodes'], input_dim=num_inp, init=ld['init']))
            elif last : mdl.add(TimeDistributedDense(num_out, init=ld['init']))
            else: mdl.add(TimeDistributedDense(ld['nodes'], init=ld['init']))
    except Exception as e :
        stderr.write(str(e))

    if ld['type'] == 'autoencoder' :
        if first: 
            mdl.add(AutoEncoder(
                          Dense(ld['nodes'], input_dim=num_inp, init=ld['init']),
                          Dense(ld['nodes'], input_dim=num_inp, init=ld['init'])))
        elif last: 
            mdl.add(AutoEncoder(
                          Dense(num_out, init=ld['init']), 
                          Dense(num_out, init=ld['init'])))
        else: 
            mdl.add(AutoEncoder(
                          Dense(ld['nodes'], init=ld['init']), 
                          Dense(ld['nodes'], init=ld['init'])))

    if ld['activation'] and ld['activation'] != 'none' :
        mdl.add(Activation(ld['activation']))

    return mdl


    

