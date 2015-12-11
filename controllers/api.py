# -*- coding: utf-8 -*-
import uuid
from sys import stderr
import json, csv
from werkzeug import secure_filename
import os

murl = URL('api', 'load_models', user_signature=True)
turl = URL('api', 'load_transactions', user_signature=True)
mdurl = URL('api', 'load_model', user_signature=True)
tdurl = URL('api', 'load_transaction', args=[],  user_signature=True)
train_url = URL('api', 'train_model', user_signature=True)
eval_url = URL('api', 'eval_model', user_signature=True)
predict_url = URL('api', 'predict_model', user_signature=True)
user_data_url = URL('api', 'get_all_user_data', user_signature=True)
new_url = URL('api', 'add_model', user_signature=True)
edit_url = URL('api', 'edit_model', user_signature=True)

@auth.requires_signature()
def load_models():
    try :
        page = int(request.vars.get('page', 1))
        page_size = int(request.vars.get('page_size', 20))
        pb = int(page-1)*(int(page_size))
        pe = int(page)*(int(page_size))
        trs = db(db.models.creator == auth.user_id).select(orderby=~db.models.created_at, limitby=(pb, pe))
        for t in trs :
            del t['weights']
        return response.json(dict(models=trs))
    except Exception as e :
        stderr.write(str(e))
        return response.json(dict(models={}))

def load_model():
    try :
        iid = int(request.vars.get('id'))
        trs = db(db.models.id == iid).select().first()
        if not auth or not trs or not auth.user_id == trs.creator :
            raise HTTP(404,"Prohibited")
        del trs['weights']
        return response.json(dict(model=trs))
    except Exception as e :
        stderr.write(str(e))
        return response.json(dict(model={}))

@auth.requires_signature()
def add_model():
    try :
        name = request.vars.get('name', '');
        mclass = request.vars.get('mclass', '');
        muuid = request.vars.get('uuid', uuid.uuid4());
        arch = request.vars.get('arch');
        if db((db.models.creator == auth.user_id) & (db.models.name == name)).select().first() :
            raise HTTP(400,"Model name exists already.")

        db['models'].insert(
                    name=name,
                    mclass=mclass,
                    created_at=datetime.datetime.now(),
                    updated_at=datetime.datetime.now(),
                    uuid=muuid,
                    arch=arch,
                    compiled=False,
                    weights=None,
                    status="compiling",
                    creator = auth.user_id)

        model = db(db.models.uuid == muuid).select().first()

        trs = {
                "status": "active",
                "tclass": "create",
                "uuid" : uuid.uuid4(),
                "creator" : auth.user_id,
                "input_payload": json.dumps({
                        "name" : name,
                        "mclass" : mclass,
                        "arch": json.loads(arch)
                }),
                "output_payload": json.dumps({
                        "abstract": "Enqueing New Compilation Request...",
                        "logs": [],
                        "output": []
                }),
                "model_name" : model.name,
                "model_name_short" : model.name_short,
                "model" : model
                }

        db['transactions'].insert(**trs)

        trs = db(db.transactions.uuid == trs['uuid']).select().first()

        print scheduler.queue_task(compile_model,
                                   pvars=dict(mid=model.id, tid=str(trs.id)),
                                   timeout=3600,
                                   retry_failed=5)

        md2 = model
        del md2['weights']
        return response.json(dict(model=md2, transaction=trs))
    except Exception as e :
        stderr.write(str(e))
        return response.json(dict(model={}, transaction={}))


@auth.requires_signature()
def edit_model():
    try:
        name = request.vars.get('name', '');
        mclass = request.vars.get('mclass', '');
        muuid = request.vars.get('uuid', uuid.uuid4());
        arch = request.vars.get('arch');
        model = db(db.models.uuid == muuid).select().first()
        model.update_record(
                    name=name,
                    mclass=mclass,
                    compiled=False,
                    trained=False,
                    uuid=muuid,
                    arch=arch,
                    weights=None,
                    updated= datetime.datetime.now(),
                    status="compiling",
                    creator = auth.user_id)

        trs = {
                "status": "active",
                "tclass": "edit",
                "uuid" : uuid.uuid4(),
                "creator" : auth.user_id,
                "model" : model,
                "input_payload": json.dumps({
                        "name" : name,
                        "mclass" : mclass,
                        "arch": json.loads(arch)
                }),
                "output_payload": json.dumps({
                        "abstract": "Enqueing Recompilation Request...",
                        "logs": [],
                        "output": []
                }),
                "model_name" : model.name,
                "model_name_short" : model.name_short,
                }

        db['transactions'].insert(**trs)

        trs = db(db.transactions.uuid == trs['uuid']).select().first()

        print scheduler.queue_task(compile_model,
                                   pvars=dict(mid=model.id, tid=str(trs.id)),
                                   timeout=3600,
                                   retry_failed=5)

        md2 = model
        del md2['weights']
        return response.json(dict(model=md2, transaction=trs))
    except Exception as e :
        stderr.write(str(e))
        return response.json(dict(model={}, transaction={}))

@auth.requires_signature()
def load_transactions():
    mid = int(request.vars.get('mid', -1))
    page = int(request.vars.get('page', 1))
    page_size = int(request.vars.get('page_size', 1))
    pb = int(page-1)*(int(page_size))
    pe = int(page)*(int(page_size))

    if mid >= 0 :
        trs = db((db.transactions.creator == auth.user_id) & (db.transactions.model == mid)).select(orderby=~db.transactions.created_at, limitby=(pb, pe))
    else :
        trs = db(db.transactions.creator == auth.user_id).select(orderby=~db.transactions.created_at, limitby=(pb, pe))
    return response.json(dict(transactions=trs))

@auth.requires_signature()
def load_transaction():
    tid = int(request.vars.get('tid', -1))
    if not tid :
        raise HTTP(404,"Transaction not found or innaccesable.")
        
    tr = db((db.transactions.creator == auth.user_id) & (db.transactions.id == int(tid))).select().first()
    trn = db((db.transactions.creator == auth.user_id) & (db.transactions.id > int(tid))).select().first()
    trp = db((db.transactions.creator == auth.user_id) & (db.transactions.id < int(tid))).select(orderby=~db.transactions.id).first()
    trn = trn.id if trn else -1
    trp = trp.id if trp else -1

    return response.json(dict(transaction=tr, tnext=trn, tprev=trp))

@auth.requires_signature()
def train_model():
    inp = request.vars.get('input');
    lbs = request.vars.get('labels');
    inpfh = request.vars.get('input_fh');
    lbsfh = request.vars.get('labels_fh');
    inp = json.loads(inp) if inp else {}
    lbs = json.loads(lbs) if lbs else {}
    mid = int(request.vars.get('model_id'));

    nb_epoch = int(request.vars.get('nb_epoch'))
    valid_split = int(request.vars.get('valid_split', 0))/100.0
    batch_size = int(request.vars.get('batch_size'))

    input_data = {} # processed input data
    labels_data = {} # processed labels data

    if inp['upload'] :
        input_data  = add_user_data_helper("inputs", inp['upload_name'], "", inpfh, auth.user_id, inp.get('save', False))
    else :
        iid = inp['select_id']
        input_data  = get_user_data_helper(iid, auth.user_id)    
        
    if lbs['upload'] :
        labels_data = add_user_data_helper("labels", lbs['upload_name'], "", lbsfh, auth.user_id, lbs.get('save', False))
    else :
        iid = lbs['select_id']
        labels_data = get_user_data_helper(iid, auth.user_id)    

    if not input_data  :
        print "Input data couldn't be processed"
        return response.json(dict())
    else:
        print "Input data Processed"

    if not labels_data :
        print "Labels data couldn't be Processed"
        return response.json(dict())
    else:
        print "Labels data Processed"

    # make new transaction for training purposes
    model = db(db.models.id == mid).select().first()

    arch = json.loads(model.arch)
    if arch.get('num_inp') != input_data.get('ccount') :
        print "Error Input : Row count doesn't match column count" + "(%s) vs (%s)"%(str(arch.get('num_inp')), str(input_data.get('ccount')))
        return response.json(dict(error="Column count of input file does not match input count of model." +
                                "(%s) vs (%s)"%(str(arch.get('num_inp')), str(input_data.get('ccount')))))
    if arch.get('num_out') != labels_data.get('ccount') :
        print "Error Labels : Row count doesn't match column count" + "(%s) vs (%s)"%(str(arch.get('num_out')), str(labels_data.get('ccount')))
        return response.json(dict(error="Column count of input file does not match input count of model." +
                                "(%s) vs (%s)"%(str(arch.get('num_inp')), str(input_data.get('ccount')))))

    if labels_data.get('rcount') != input_data.get('rcount') :
        print "Error Labels : Input Row count doesn't match Labels Row count" + "(%s) vs (%s)"%(str(input_data.get('rcount')), str(labels_data.get('rcount')))
        return response.json(dict(error="row count of input file does not match row count of label file."))
    model.update_record(
                trained=False,
                updated= datetime.datetime.now(),
                status="training"
    )

    trs = {
            "status": "active",
            "tclass": "train",
            "uuid" : uuid.uuid4(),
            "creator" : auth.user_id,
            "model" : model,
            "input_payload": json.dumps({
                "input_file" : {
                    "name" : input_data.get('name', ""),
                    "rcount" : input_data.get('rcount', -1),
                    "ccount" : input_data.get('ccount', -1),
                    "saved" : bool(input_data.get('id', None)),
                    "id" : input_data.get('id', -1),
                    "size_KB" : input_data.get('size_KB', -1)
                },
                "labels_file" : {
                    "name" : labels_data.get('name'),
                    "rcount" : labels_data.get('rcount', -1),
                    "ccount" : labels_data.get('ccount', -1),
                    "saved" : bool(labels_data.get('id', None)),
                    "id" : labels_data.get('id', -1),
                    "size_KB" : labels_data.get('size_KB', -1)
                },
                "nb_epoch": nb_epoch,
                "batch_size": batch_size,
                "valid_split": valid_split,
                "shuffle": "batch"
            }),
            "output_payload": json.dumps({
                    "abstract": "Enqueing Training Request...",
                    "logs": [],
                    "output": []
            }),
            "model_name" : model.name,
            "model_name_short" : model.name_short,
    }

    db['transactions'].insert(**trs)

    trs = db(db.transactions.uuid == trs['uuid']).select().first()

    print scheduler.queue_task(queue_train_model,
                               pvars=dict(mid=model.id, tid=str(trs.id),
                                          infh=input_data.get('payload'),
                                          lbsfh=labels_data.get('payload')),
                                   timeout=7200,
                                   retry_failed=5
                               )

    return response.json(dict(inp=inp))



@auth.requires_signature()
def eval_model():
    inp = request.vars.get('input');
    lbs = request.vars.get('labels');
    inpfh = request.vars.get('input_fh');
    lbsfh = request.vars.get('labels_fh');
    inp = json.loads(inp) if inp else {}
    lbs = json.loads(lbs) if lbs else {}
    mid = int(request.vars.get('model_id'));

    batch_size = int(request.vars.get('batch_size'))

    input_data = {} # processed input data
    labels_data = {} # processed labels data

    if inp['upload'] :
        input_data  = add_user_data_helper("inputs", inp['upload_name'], "", inpfh, auth.user_id, inp.get('save', False))
    else :
        iid = inp['select_id']
        input_data  = get_user_data_helper(iid, auth.user_id)    
        
    if lbs['upload'] :
        labels_data = add_user_data_helper("labels", lbs['upload_name'], "", lbsfh, auth.user_id, lbs.get('save', False))
    else :
        iid = lbs['select_id']
        labels_data = get_user_data_helper(iid, auth.user_id)    

    if not input_data  :
        print "Input data couldn't be processed"
        return response.json(dict())
    else:
        print "Input data Processed"

    if not labels_data :
        print "Labels data couldn't be Processed"
        return response.json(dict())
    else:
        print "Labels data Processed"

    # make new transaction for evaluation purposes
    model = db(db.models.id == mid).select().first()

    arch = json.loads(model.arch)
    if arch.get('num_inp') != input_data.get('ccount') :
        print "Error Input : Row count doesn't match column count" + "(%s) vs (%s)"%(str(arch.get('num_inp')), str(input_data.get('ccount')))
        return response.json(dict(error="Column count of input file does not match input count of model." +
                                "(%s) vs (%s)"%(str(arch.get('num_inp')), str(input_data.get('ccount')))))
    if arch.get('num_out') != labels_data.get('ccount') :
        print "Error Labels : Row count doesn't match column count" + "(%s) vs (%s)"%(str(arch.get('num_out')), str(labels_data.get('ccount')))
        return response.json(dict(error="Column count of input file does not match input count of model." +
                                "(%s) vs (%s)"%(str(arch.get('num_inp')), str(input_data.get('ccount')))))

    if labels_data.get('rcount') != input_data.get('rcount') :
        print "Error Labels : Input Row count doesn't match Labels Row count" + "(%s) vs (%s)"%(str(input_data.get('rcount')), str(labels_data.get('rcount')))
        return response.json(dict(error="row count of input file does not match row count of label file."))

    model.update_record(
                updated= datetime.datetime.now(),
                status="evaluating"
    )

    trs = {
            "status": "active",
            "tclass": "evaluate",
            "uuid" : uuid.uuid4(),
            "creator" : auth.user_id,
            "model" : model,
            "input_payload": json.dumps({
                "input_file" : {
                    "name" : input_data.get('name', ""),
                    "rcount" : input_data.get('rcount', -1),
                    "ccount" : input_data.get('ccount', -1),
                    "saved" : bool(input_data.get('id', None)),
                    "id" : input_data.get('id', -1),
                    "size_KB" : input_data.get('size_KB', -1)
                },
                "labels_file" : {
                    "name" : labels_data.get('name'),
                    "rcount" : labels_data.get('rcount', -1),
                    "ccount" : labels_data.get('ccount', -1),
                    "saved" : bool(labels_data.get('id', None)),
                    "id" : labels_data.get('id', -1),
                    "size_KB" : labels_data.get('size_KB', -1)
                },
                "batch_size": batch_size
            }),
            "output_payload": json.dumps({
                    "abstract": "Enqueing Evaluation Request...",
                    "logs": [],
                    "output": []
            }),
            "model_name" : model.name,
            "model_name_short" : model.name_short,
    }

    db['transactions'].insert(**trs)

    trs = db(db.transactions.uuid == trs['uuid']).select().first()

    print scheduler.queue_task(queue_eval_model,
                               pvars=dict(mid=model.id, tid=str(trs.id),
                                          infh=input_data.get('payload'),
                                          lbsfh=labels_data.get('payload')),
                                   timeout=7200,
                                   retry_failed=5
                               )

    return response.json(dict(inp=inp))


@auth.requires_signature()
def predict_model():
    inp = request.vars.get('input');
    inpfh = request.vars.get('input_fh');
    inp = json.loads(inp) if inp else {}
    mid = int(request.vars.get('model_id'));

    batch_size = int(request.vars.get('batch_size'))

    input_data = {} # processed input data

    if inp['upload'] :
        input_data  = add_user_data_helper("inputs", inp['upload_name'], "", inpfh, auth.user_id, inp.get('save', False))
    else :
        iid = inp['select_id']
        input_data  = get_user_data_helper(iid, auth.user_id)    
        
    if not input_data  :
        print "Input data couldn't be processed"
        return response.json(dict())
    else:
        print "Input data Processed"


    # make new transaction for prediction purposes
    model = db(db.models.id == mid).select().first()

    arch = json.loads(model.arch)
    if arch.get('num_inp') != input_data.get('ccount') :
        print "Error Input : Row count doesn't match column count" + "(%s) vs (%s)"%(str(arch.get('num_inp')), str(input_data.get('ccount')))
        return response.json(dict(error="Column count of input file does not match input count of model." +
                                "(%s) vs (%s)"%(str(arch.get('num_inp')), str(input_data.get('ccount')))))
    model.update_record(
                updated= datetime.datetime.now(),
                status="predicting"
    )

    trs = {
            "status": "active",
            "tclass": "predict",
            "uuid" : uuid.uuid4(),
            "creator" : auth.user_id,
            "model" : model,
            "input_payload": json.dumps({
                "input_file" : {
                    "name" : input_data.get('name', ""),
                    "rcount" : input_data.get('rcount', -1),
                    "ccount" : input_data.get('ccount', -1),
                    "saved" : bool(input_data.get('id', None)),
                    "id" : input_data.get('id', -1),
                    "size_KB" : input_data.get('size_KB', -1)
                },
                "batch_size": batch_size
            }),
            "output_payload": json.dumps({
                    "abstract": "Enqueing Prediction Request...",
                    "logs": [],
                    "output": []
            }),
            "model_name" : model.name,
            "model_name_short" : model.name_short,
    }

    db['transactions'].insert(**trs)

    trs = db(db.transactions.uuid == trs['uuid']).select().first()

    print scheduler.queue_task(queue_predict_model,
                               pvars=dict(mid=model.id, tid=str(trs.id),
                                          infh=input_data.get('payload')),
                                   timeout=7200,
                                   retry_failed=5
                               )

    return response.json(dict(inp=inp))

@auth.requires_signature()
def get_user_data() :
    iid = int(request.args.get(0))
    user_data = user_data_helper(iid, auth.user_id)
    return response.json(user_data)

@auth.requires_signature()
def get_all_user_data() :
    dclass = request.vars.get('dclass', None)
    user_data = []
    if dclass :
        user_data = db((db.user_uploads.downer == auth.user_id) & (db.user_uploads.dclass == dclass)).select(orderby=~db.user_uploads.created_at)
    else :
        user_data = db(db.user_uploads.downer == auth.user_id).select(orderby=~db.user_uploads.created_at)
    return response.json({"user_data": [{
                    "id": ud.id, "dclass" : ud.dclass, "name" : ud.name, "description" : ud.description, 
                    "size_KB" : ud.size_KB, "rcount": ud.rcount, "ccount" : ud.ccount, "created_at" : ud.created_at} 
                    for ud in user_data]})

@auth.requires_signature()
def add_user_data() :
    pass

def get_user_data_helper(iid, user_id) :
    print "data_helper, id = " + str(iid)
    user_data = db((db.user_uploads.downer == user_id) & (db.user_uploads.id == iid)).select().first()
    return user_data

def add_user_data_helper(dclass, name, desc, payload, creator, save=False) :
    if dclass not in ['inputs', 'labels'] :
        print "Invalid File Class, must be inputs or labels"
        return False
    name = secure_filename(name)
    ext = os.path.splitext(name)[1]
    if ext != ".csv" :
        return False
    data = payload.file.read()
    payload.file.seek(0, os.SEEK_END)
    file_length_bytes = payload.file.tell()
    size_KB= file_length_bytes/1000.0
    created_at = datetime.datetime.now()
    try :
        payload.file.seek(0)
        dialect = csv.Sniffer().sniff(payload.file.read(1024))
        payload.file.seek(0)
        reader = csv.reader(payload.file, dialect)
        rcount = 0
        ccount = 0
        for line in reader :
            ccount = len([x for x in line])-1 #-1 for row counter
            rcount += 1
        if db(db.user_uploads.name == name).select().first() :
            saved = False
            print "This file already exists for this account"
        if save :
            new_id = db['user_uploads'].insert(
                    dclass=dclass,
                    name=name,
                    description=desc,
                    payload=data,
                    extension=ext,
                    created_at=created_at,
                    size_KB=size_KB,
                    rcount=rcount, ccount=ccount,
                    downer=creator
            )
            return db(db.user_uploads.id == new_id).select().first()
        else :
            return dict(
                    dclass=dclass,
                    name=name,
                    description=desc,
                    payload=data,
                    extension=ext,
                    created_at=created_at,
                    size_KB=size_KB,
                    rcount=rcount, ccount=ccount,
                    downer=creator
            )
    except Exception as e :
        stderr.write(str(e))
        return False
