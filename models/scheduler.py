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


output_payload = {
    "abstract" : "Executing Recompilation Sequence...",
    "logs" : [],
    "output" : []
}
tlogs = []
dbmodel = {}
dbt = {}

# logstr = lambda x: tlogs.append(  str(datetime.datetime.now())+" : " +x) or stderr.write(str(x)+"\n")

def logheader(trs) :
    global output_payload
    global tlogs
    global dbmodel
    global dbt
    lstr = ["Model Compilation Request : %s" % trs.model_name]
    lstr.append("Started at : " +str(datetime.datetime.now())[:-3])
    lstr.append("-"*80)
    tlogs = lstr + tlogs
    stderr.write(str(lstr)+"\n")
    output_payload['logs'] = tlogs
    trs.update_record(
        output_payload = json.dumps(output_payload)
    )
    db.commit()

def logfooter(trs) :
    global output_payload
    global tlogs
    global dbmodel
    global dbt
    lstr = ["-"*80]
    lstr.append("Model Compilation Request : %s" % trs.model_name)
    lstr.append("Finished at : " +str(datetime.datetime.now())[:-3])
    tlogs = tlogs + lstr
    stderr.write(str(lstr)+"\n")
    output_payload['logs'] = tlogs
    trs.update_record(
        output_payload = json.dumps(output_payload)
    )
    db.commit()

def logstr(trs, x) :
    global output_payload
    global tlogs
    global dbmodel
    global dbt
    lstr = str(datetime.datetime.now()).split(" ")[1][:-3]+" : "+str(x)
    stderr.write(str(x)+"\n")
    tlogs.append(lstr)
    output_payload['logs'] = tlogs
    trs.update_record(
        output_payload = json.dumps(output_payload)
    )
    db.commit()


def compile_model(mid, tid) :
    global output_payload
    global tlogs
    global dbmodel
    global dbt
    try :
        dbmodel = db(db.models.id == mid).select().first()
        dbt = db(db.transactions.id == int(tid)).select().first()

        logheader(dbt)
        logstr(dbt, "Attempting Model Compilation, ID (%s)"%str(mid));

        arch = json.loads(dbmodel.arch)
        layers = arch['layer_dicts']

        logstr(dbt,"Creating Sequential Model...");
        mdl = Sequential()
        logstr(dbt, "Sequential Model Created, Adding Layers...");
        
        if not len(layers): return False
        mdl = add_layer(mdl, layers[0], arch, first=True, last=len(layers) == 1)
        logstr(dbt, "First Layer Added")
        for i in range(1, len(layers)-1) :
            logstr(dbt, "Layer %s Added"%str(i+1))
            mdl = add_layer(mdl, layers[i], arch)
        if not len(layers) <= 1:
            mdl = add_layer(mdl, layers[len(layers)-1], arch, first=False, last=True)
            logstr(dbt, "Last Layer Added")

        logstr(dbt, "Compiling Model....")
        mdl.compile(loss=arch['lossfn'], optimizer=arch['optimizer'])
        logstr(dbt, "Model Compiled Successfully.")

        logstr(dbt, "Updating Model and Transaction Records.")
        dbmodel.update_record(
            status = "idle",
            arch_json = mdl.to_json(),
            updated_at = datetime.datetime.now(),
            compiled = True
       ) 
        db.commit()
        logstr(dbt, "Model Saved to DB")

        dbt = db(db.transactions.id == int(tid)).select().first()


        output_payload['abstract'] = "Model Compiled Successfully."
        output_payload['logs'] = tlogs
        output_payload['output'].append("Model (%s) was compiled successfully at (%s)."%(dbmodel.name, str(dbmodel.updated_at)))
        dbt.update_record(
            status = "success",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps(output_payload)
		)

        logfooter(dbt)

        db.commit()
    except Exception as e :
        dbmodel = db(db.models.id == mid).select().first()
        dbt = db(db.transactions.id == int(tid)).select().first()
        logstr(dbt, "Compile Failed : %s" % str(e))
        dbmodel.update_record(
            status = "broken",
            arch_json = "", #mdl.to_json(),
            updated_at = datetime.datetime.now(),
            compiled = False, 
            trained = False
       ) 
        db.commit()
        logstr(dbt, "Exception while Compiling Model (%s)" % str(dbmodel.name))

        logstr(dbt, "Error noted and Transaction marked as failed");

        logstr(dbt, "Transaction Failure Saved in DB");
        logfooter(dbt)
        dbt.update_record(
            status = "failed",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps({
					"abstract": "Error While Compiling. (%s)" % (str(e)),
                    "logs": tlogs,
                    "output": ["Error was experienced while compiling model (%s)."%(dbmodel.name), "Full error output:  (%s)."%(str(e))]
            })
		)
        db.commit()



def add_layer(mdl, ld, arch, first=False, last=False) :
    global output_payload
    global tlogs
    global dbmodel
    global dbt
    num_inp = arch['num_inp']
    num_out = arch['num_out']
    if ld['type'] == 'dense' :
        if first : mdl.add(Dense(ld['nodes'], input_dim=num_inp, init=ld['init']))
        if last : mdl.add(Dense(output_dim=num_out,init=ld['init']))
        else :  mdl.add(Dense(ld['nodes'], init=ld['init']))
            

    try :
        if ld['type'] == 'convolutional' :
            logstr(dbt, "Adding convolutional layer")
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


    

