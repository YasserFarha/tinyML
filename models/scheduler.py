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
from sys import stderr, stdout

tlogs = []
logstr = lambda x: tlogs.append(x) or stderr.write(str(x)) or stderr.write("\n");


def compile_model(mid, tid) :
    try :
        logstr("Attempting Model Compilation, ID (%s)"%str(mid));
        dbmodel = db(db.models.id == mid).select().first()
        arch = json.loads(dbmodel.arch)
        layers = arch['layer_dicts']

        logstr("Creating Sequential Model...");
        mdl = Sequential()
        logstr("Sequential Model Created, Adding Layers...");
        
        if not len(layers): return False
        mdl = add_layer(mdl, layers[0], arch, first=True, last=len(layers) == 1)
        logstr("First Layer Added")
        for i in range(1, len(layers)-1) :
            logstr("Layer %s Added"%str(i+1))
            mdl = add_layer(mdl, layers[i], arch)
        if not len(layers) <= 1:
            mdl = add_layer(mdl, layers[len(layers)-1], arch, first=False, last=True)

        logstr("Compiling Model....")
        mdl.compile(loss=arch['lossfn'], optimizer=arch['optimizer'])
        logstr("Model Compiled Successfully.")

        logstr("Updating Model and Transaction Records.")
        dbmodel.update_record(
            status = "idle",
            arch_json = mdl.to_json(),
            updated_at = datetime.datetime.now(),
            compiled = True
       ) 
        db.commit()
        logstr("Model Saved to DB")

        dbt = db(db.transactions.id == int(tid)).select().first()
        dbt.update_record(
            status = "success",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps({
                    "abstract": "Model Compiled Successfully.",  
                    "logs": tlogs,
                    "output": "Model (%s) was compiled successfully at (%s)."%(dbmodel.name, str(dbmodel.updated_at))
            })
		)

        logstr("Transaction Saved to DB")

        db.commit()
    except Exception as e :
        logstr("Compile Failed : %s" % str(e))
        dbmodel = db(db.models.id == mid).select().first()
        dbmodel.update_record(
            status = "broken",
            arch_json = "", #mdl.to_json(),
            updated_at = datetime.datetime.now(),
            compiled = False, 
            trained = False
       ) 
        db.commit()
        logstr("Exception while Compiling Model (%s)" % str(dbmodel.name))

        dbt = db(db.transactions.id == int(tid)).select().first()
        dbt.update_record(
            status = "failed",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps({
					"abstract": "Error While Compiling. (%s)" % (str(e)),
                    "abstract": "Model Compiled Successfully.",  
                    "logs": tlogs,
                    "output": "Error was experienced while compiling model (%s). Full error output:  (%s)."%(dbmodel.name, str(e))
            })
		)
        db.commit()
        logstr("Error noted and Transaction marked as failed");



def add_layer(mdl, ld, arch, first=False, last=False) :
    num_inp = arch['num_inp']
    num_out = arch['num_out']
    if ld['type'] == 'dense' :
        if first : mdl.add(Dense(ld['nodes'], input_dim=num_inp, init=ld['init']))
        if last : mdl.add(Dense(output_dim=num_out,init=ld['init']))
        else :  mdl.add(Dense(ld['nodes'], init=ld['init']))
            

    try :
        if ld['type'] == 'convolutional' :
            logstr("Adding convolutional layer")
            if first : mdl.add(Convolution1D(ld['nodes'], filter_length=3, input_dim=num_inp, init=ld['init']))
            elif last : mdl.add(Convolution1D(num_out, filter_length=3, init=ld['init']))
            else: mdl.add(Convolution1D(ld['nodes'], filter_length=3, input_dim=ld['num_inp'], init=ld['init']))
    except Exception as e :
        logstr(str(e))

    try :
        if ld['type'] == 'timedistdense' :
            if first : mdl.add(TimeDistributedDense(ld['nodes'], input_dim=num_inp, init=ld['init']))
            elif last : mdl.add(TimeDistributedDense(num_out, init=ld['init']))
            else: mdl.add(TimeDistributedDense(ld['nodes'], init=ld['init']))
    except Exception as e :
        logstr(str(e))

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


    

