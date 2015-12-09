#!/usr/bin/env python
from gluon.scheduler import Scheduler
import task_lib, json
scheduler = Scheduler(db)

import numpy as np
import pandas as pd

import keras
from keras.models import Sequential, Graph
from keras.models import model_from_json
from keras.layers.core import Dense, Dropout, Activation, TimeDistributedDense, AutoEncoder
from keras.layers.convolutional import Convolution1D
from keras.optimizers import SGD
import theano, sys, json, datetime, uuid
from sys import stderr, stdout
from cStringIO import StringIO



output_payload = {
    "abstract" : "Executing Recompilation Sequence...",
    "logs" : [],
    "output" : []
}
tlogs = []
dbmodel = {}
dbt = {}

def load_data(fh, train=True):
    f = StringIO(str(fh))
    try :
        df = pd.read_csv(f)
        X = df.values.copy()
        if train:
            np.random.shuffle(X)  # https://youtu.be/uyUXoap67N8
            stderr.write(str(X))
            return X[:, -1:]
        else:
            stderr.write(str(X))
            return X[:, -1:]
    except Exception as e :
        logstr(dbt, str(e))
        return []

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
        output_payload['abstract'] = "Executing Recompilation Sequence..."
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
        return True
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



class LogCallback(keras.callbacks.Callback):
    global dbt
    def on_train_begin(self, logs={}):
        logstr(dbt, "Beginning Training Sequence.")
        stderr.write(str(logs))

    def on_batch_end(self, batch, logs={}):
        logstr(dbt, "Training Batch Completed")
        logstr(dbt, "loss : %s"%str(logs.get('loss')))
        stderr.write(str(logs))
        stderr.write(str(batch))

class LossHistory(keras.callbacks.Callback):
    global dbt
    def on_train_begin(self, logs={}):
        self.losses = []

    def on_batch_end(self, batch, logs={}):
        self.losses.append(logs.get('loss'))


def queue_train_model(mid, tid, infh, lbsfh) :
    global output_payload
    global tlogs
    global dbmodel
    global dbt
    output_payload['abstract'] = "Executing Training Sequence..."
    try :
        dbmodel = db(db.models.id == mid).select().first()
        dbt = db(db.transactions.id == int(tid)).select().first()

        logheader(dbt)
        logstr(dbt, "Attempting Model Training, ID (%s)"%str(mid));

        ipl = json.loads(dbt['input_payload'])
        nb_epoch = ipl.get('nb_epoch')
        batch_size = ipl.get('batch_size')
        valid_split = ipl.get('valid_split')
        shuffle = ipl.get('shuffle')
        
        model = model_from_json(dbmodel.arch_json)

        logstr(dbt, "Model Loaded Successfully");
        stderr.write(model.to_json())

        X = load_data(infh, train=True)
        labels = load_data(lbsfh, train=True)

        stderr.write(str(X))
        stderr.write(str(labels))

        logcb = LogCallback()
        losscb = LossHistory()

        model.fit(X, labels,
                  nb_epoch=int(nb_epoch), 
                  batch_size=int(batch_size),
                   validation_split=float(valid_split),
                   callbacks=[losscb])
        # TODO add weight to model if weights are saved

        dbmodel.update_record(
            status = "idle",
            updated_at = datetime.datetime.now(),
            trained = True
       ) 
        db.commit()
        logstr(dbt, "Training Session Succeeded (%s)" % str(dbmodel.name))


        logstr(dbt, "Transaction Success Saved in DB");
        logfooter(dbt)
        dbt.update_record(
            status = "success",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps({
					"abstract": "Training Session Complete",
                    "logs": tlogs,
                    "output": ["model was successfully loaded, trained, and saved for future use."],
                    "loss_history" : [str(x) for x in losscb.losses]
            })
		)
        db.commit()
        return True

    except Exception as e :
        dbmodel = db(db.models.id == mid).select().first()
        dbt = db(db.transactions.id == int(tid)).select().first()
        logstr(dbt, "Training Failed : %s" % str(e))
        dbmodel.update_record(
            status = "idle",
            updated_at = datetime.datetime.now(),
            trained = False
       ) 
        db.commit()
        logstr(dbt, "Exception while Training Model (%s)" % str(dbmodel.name))

        logstr(dbt, "Error noted and Transaction marked as failed");

        logstr(dbt, "Transaction Failure Saved in DB");
        logfooter(dbt)
        dbt.update_record(
            status = "failed",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps({
					"abstract": "Error While Training. (%s)" % (str(e)),
                    "logs": tlogs,
                    "output": ["Error was experienced while training model (%s)."%(dbmodel.name), "Full error output:  (%s)."%(str(e))]
            })
		)
        db.commit()

