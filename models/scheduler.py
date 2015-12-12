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
import theano, sys, json, datetime, uuid, os
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
    try :
        f = StringIO(str(fh))
        df = pd.read_csv(f)
        X = df.values.copy()
        if train:
            # np.random.shuffle(X)  # https://youtu.be/uyUXoap67N8
            stderr.write(str(X))
            return X[:, 1:]
        else:
            stderr.write(str(X))
            return X[:, 1:]
    except Exception as e :
        logstr(dbt, str(e))
        return []

def logheader(trs, instr) :
    global output_payload
    global tlogs
    global dbmodel
    global dbt
    lstr = [instr + " : %s" % trs.model_name]
    lstr.append("Started at : " +str(datetime.datetime.now())[:-3])
    lstr.append("-"*80)
    tlogs = lstr + tlogs
    stderr.write(str(lstr)+"\n")
    output_payload['logs'] = tlogs
    trs.update_record(
        output_payload = json.dumps(output_payload)
    )
    db.commit()

def logfooter(trs, instr) :
    global output_payload
    global tlogs
    global dbmodel
    global dbt
    lstr = ["-"*80]
    lstr.append(instr + " : %s" % trs.model_name)
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

def load_weights(dbmodel, dbt, model) :
    if not dbmodel.weights :
        return model
    stderr.write("Loading Weights")
    wtsfn = dbmodel.name+str(dbt.id)+".h5"
    with open(wtsfn, 'w') as wfh :
        wfh.write(dbmodel.weights)

    model.load_weights(wtsfn)
    os.remove(wtsfn)
    return model

def save_weights(dbmodel, dbt, model) :
    stderr.write("Saving Weights")
    wtsfn = dbmodel.name+str(dbt.id)+".h5"
    model.save_weights(wtsfn, overwrite=True)
    wtstxt = None
    with open(wtsfn, 'r') as wfh :
        wtstxt = wfh.read()

    os.remove(wtsfn)
    dbmodel.update_record(
            weights = wtstxt
    )
    db.commit()
    return dbmodel


class LossHistory(keras.callbacks.Callback):
    global dbt

    def on_epoch_begin(self, epoch, log={}):
        self.losses = []

    def on_epoch_end(self, epoch, logs={}):
        totall = 0
        totala = 0
        stderr.write(str(logs))
        for x in self.losses :
            # stderr.write(str(x))
            totall += x.get('loss')
            totala += x.get('accuracy')
        totall = float(totall)/len(self.losses)
        totala = float(totala)/len(self.losses)
        self.epochs.append({"avg_loss" : round(totall, 5), "avg_acc" : round(totala, 5),
                            "val_loss" : round(logs['val_loss'], 5), "val_acc" : round(logs['val_acc'], 5)})

    def on_train_begin(self, logs={}):
        self.epochs = []
        self.losses = []

    def on_batch_end(self, batch, logs={}):
        # stderr.write(str(logs))
        self.losses.append({"loss" : logs.get('loss'), "accuracy" : logs.get('acc')})


def queue_train_model(mid, tid, infh, lbsfh) :
    global output_payload
    global tlogs
    global dbmodel
    global dbt
    output_payload['abstract'] = "Executing Training Sequence..."
    try :
        dbmodel = db(db.models.id == mid).select().first()
        dbt = db(db.transactions.id == int(tid)).select().first()

        logheader(dbt, "Model Training Request")
        logstr(dbt, "Attempting Model Training, ID (%s)"%str(mid));

        ipl = json.loads(dbt['input_payload'])
        nb_epoch = ipl.get('nb_epoch')
        batch_size = ipl.get('batch_size')
        valid_split = ipl.get('valid_split')
        shuffle = ipl.get('shuffle')


        model = model_from_json(dbmodel.arch_json)
        model = load_weights(dbmodel, dbt, model)


        logstr(dbt, "Model Loaded Successfully");
        stderr.write(model.to_json())

        X = load_data(infh, train=True)
        labels = load_data(lbsfh, train=True)

        losscb = LossHistory()

        stderr.write("Starting Model Fit.\n")
        model.fit(X, labels,
                  nb_epoch=int(nb_epoch), 
                  batch_size=int(batch_size),
                  validation_split=float(valid_split),
                  shuffle="batch",
                  show_accuracy=True,
                  verbose=0,
                  callbacks=[losscb])
        stderr.write("Finished Model Fit.\n")
        # TODO add weight to model if weights are saved

        stderr.write(str([str(x) for x in losscb.epochs]))

        save_weights(dbmodel, dbt, model)

        dbmodel.update_record(
            status = "idle",
            updated_at = datetime.datetime.now(),
            trained = True
       ) 

        logstr(dbt, "Transaction Success Saved in DB");
        logstr(dbt, "Training Session Succeeded (%s)" % str(dbmodel.name))
        logfooter(dbt, "Model Training Request Succeeded")
        stderr.write("About to Exit!\n\n")
        dbt.update_record(
            status = "success",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps({
					"abstract": "Training Session Complete",
                    "logs": tlogs,
                    "output": ["model was successfully loaded, trained, and saved for future use."],
                    "epochs" : [x for x in losscb.epochs],
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
        logfooter(dbt, "Model Training Request Failed")
        dbt.update_record(
            status = "failed",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps({
					"abstract": "Error While Training. (%s)" % (str(e)),
                    "logs": tlogs,
                    "output": ["Error was experienced while training model (%s)."%(dbmodel.name), "Full error output:  (%s)."%(str(e))],
                    "epochs" : [],
                    "loss_history" : []
            })
		)
        db.commit()
        

def queue_eval_model(mid, tid, infh, lbsfh) :
    global output_payload
    global tlogs
    global dbmodel
    global dbt
    output_payload['abstract'] = "Executing Evaluation Sequence..."
    try :
        dbmodel = db(db.models.id == mid).select().first()
        dbt = db(db.transactions.id == int(tid)).select().first()

        logheader(dbt, "Model Evaluation Request")
        logstr(dbt, "Attempting Model Evaluation, ID (%s)"%str(mid));

        ipl = json.loads(dbt['input_payload'])
        batch_size = ipl.get('batch_size')


        model = model_from_json(dbmodel.arch_json)
        model = load_weights(dbmodel, dbt, model)

        logstr(dbt, "Model Loaded Successfully");
        stderr.write(model.to_json())

        X = load_data(infh, train=True)
        labels = load_data(lbsfh, train=True)

        stderr.write("Starting Model Fit.\n")
        (loss, acc) = model.evaluate(X, labels,
                                    batch_size=int(batch_size),
                                    show_accuracy=True,
                                    verbose=0)
        stderr.write("Finished Model Fit.\n")
        # TODO add weight to model if weights are saved

        dbmodel.update_record(
            status = "idle",
            updated_at = datetime.datetime.now(),
       ) 

        logstr(dbt, "Transaction Success Saved in DB");
        logstr(dbt, "Evaluation Session Succeeded (%s)" % str(dbmodel.name))
        logfooter(dbt, "Model Evaluation Request Succeeded")
        stderr.write("About to Exit!\n\n")
        dbt.update_record(
            status = "success",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps({
					"abstract": "Evaluation Session Complete",
                    "logs": tlogs,
                    "output": ["model was successfully loaded, evaluated, and saved for future use.",
                              "The total loss over the data was : %s"%str(loss),
                              "The total accuracy over the data was : %s"%str(acc)],
                    "accuracy" : acc,
                    "loss": loss
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
        ) 
        db.commit()
        logstr(dbt, "Exception while Evaluating Model (%s)" % str(dbmodel.name))

        logstr(dbt, "Error noted and Transaction marked as failed");

        logstr(dbt, "Transaction Failure Saved in DB");
        logfooter(dbt, "Model Evaluating Request Failed")
        dbt.update_record(
            status = "success",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps({
					"abstract": "Error During Evaluation.",
                    "logs": tlogs,
                    "output": ["Error was experienced while evaluating model (%s)."%(dbmodel.name), "Full error output:  (%s)."%(str(e))],
                    "accuracy" : acc,
                    "loss": loss
            })
		)
        db.commit()



def queue_predict_model(mid, tid, infh) :
    global output_payload
    global tlogs
    global dbmodel
    global dbt
    output_payload['abstract'] = "Executing Prediction Sequence..."
    try :
        dbmodel = db(db.models.id == mid).select().first()
        dbt = db(db.transactions.id == int(tid)).select().first()

        logheader(dbt, "Model Prediction Request")
        logstr(dbt, "Attempting Model Prediction, ID (%s)"%str(mid));

        ipl = json.loads(dbt['input_payload'])
        batch_size = ipl.get('batch_size')

        model = model_from_json(dbmodel.arch_json)
        model = load_weights(dbmodel, dbt, model)

        logstr(dbt, "Model Loaded Successfully");
        stderr.write(model.to_json())

        X = load_data(infh, train=True)

        stderr.write("Starting Model Predict.\n")
        predictions = model.predict(X, batch_size=int(batch_size), verbose=0)
        stderr.write("Finished Model Predict.\n")

        stderr.write(str(predictions))

        dbmodel.update_record(
            status = "idle",
            updated_at = datetime.datetime.now(),
       ) 

        logstr(dbt, "Transaction Success Saved in DB");
        logstr(dbt, "Prediction Session Succeeded (%s)" % str(dbmodel.name))
        logfooter(dbt, "Model Prediction Request Succeeded")
        stderr.write("About to Exit!\n\n")
        dbt.update_record(
            status = "success",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps({
					"abstract": "Prediction Session Complete",
                    "logs": tlogs,
                    "output": ["model was successfully loaded and used to generate predictions."],
                    "predictions" : predictions.tolist()
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
        ) 
        db.commit()
        logstr(dbt, "Exception while Predicting Model (%s)" % str(dbmodel.name))

        logstr(dbt, "Error noted and Transaction marked as failed");

        logstr(dbt, "Transaction Failure Saved in DB");
        logfooter(dbt, "Model Predicting Request Failed")
        dbt.update_record(
            status = "failed",
            finished_at = datetime.datetime.now(),
            output_payload = json.dumps({
					"abstract": "Error During Prediction.",
                    "logs": tlogs,
                    "output": ["Error was experienced while predicting for model (%s)."%(dbmodel.name), "Full error output:  (%s)."%(str(e))],
                    "predictions" : []
            })
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

        logheader(dbt, "Model Compilation Request")
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

        lossfnstr = arch['lossfn']
        if arch['lossfn'] == 'rmse' :
            lossfnstr = 'root_mean_squared_error'

        mdl.compile(loss=lossfnstr, optimizer=arch['optimizer'])
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

        logfooter(dbt, "Model Compilation Request Succeeded")

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
        logfooter(dbt, "Model Compilation Request Failed")
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
        elif last : mdl.add(Dense(output_dim=num_out,init=ld['init']))
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



