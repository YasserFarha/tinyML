# -*- coding: utf-8 -*-
import uuid, json

### Routes ###
def home() :
    redirect(URL('default', 'index'))

### API Routes ###

@auth.requires_signature()
def load_models():
	page = int(request.vars.get('page', 1))
	page_size = 5
	pb = int(page-1)*(int(page_size))
	pe = int(page)*(int(page_size))
	trs = db(db.models.creator == auth.user_id).select(orderby=~db.models.created_at, limitby=(pb, pe))
	return response.json(dict(models=trs))

def load_transactions():
	page = int(request.vars.get('page', 1))
	page_size = 7
	pb = int(page-1)*(int(page_size))
	pe = int(page)*(int(page_size))
	trs = db(db.transactions.creator == auth.user_id).select(orderby=~db.transactions.created_at, limitby=(pb, pe))
	return response.json(dict(transactions=trs))

def do_logout() :
    redirect(URL('default', 'user', args=['logout']))

def do_login() :
    redirect(URL('default', 'user', args=['login']))

def do_register() :
    redirect(URL('default', 'user', args=['register']))

def index():
    return dict(logged_in=("true" if auth.user_id != None else "false"),
                user_id=auth.user_id if auth.user_id else -1)

def user():
    return dict(form=auth())

@cache.action()
def download():
    return response.download(request, db)



### dbpopulate/delete scripts ###

def deletedb():
	db['models'].truncate()
	db['transactions'].truncate()
	return True

def populate():

        stcts = [ 
            { "layer_dicts" : [
                {   "uuid" : str(uuid.uuid4()),
                    "type" : "dense",
                    "nodes" : 6,
                    "init" : "normal",
                    "activation" : "linear"},
                {   "uuid" : str(uuid.uuid4()),
                    "type" : "dense",
                    "nodes" : 12,
                    "init" : "uniform",
                    "activation" : "tanh"} ],
                "num_inp" : 10,
                "num_out" : 3 },
            { "layer_dicts" : [
                {   "uuid" : str(uuid.uuid4()),
                    "type" : "dense",
                    "nodes" : 6,
                    "init" : "uniform",
                    "activation" : "relu"},
                {   "uuid" : str(uuid.uuid4()),
                    "type" : "convolutional",
                    "nodes" : 6,
                    "init" : "uniform",
                    "activation" : "relu"},
                {   "uuid" : str(uuid.uuid4()),
                    "type" : "dense",
                    "nodes" : 18,
                    "init" : "he_unif",
                    "activation" : "relu"},
                {   "uuid" : str(uuid.uuid4()),
                    "type" : "dense",
                    "nodes" : 10,
                    "init" : "he_unif",
                    "activation" : "linear"} ],
                "num_inp" : 26,
                "num_out" : 12 },
            { "layer_dicts" : [
                {   "uuid" : str(uuid.uuid4()),
                    "type" : "dense",
                    "nodes" : 6,
                    "init" : "uniform",
                    "activation" : "relu"},
                {   "uuid" : str(uuid.uuid4()),
                    "type" : "dense",
                    "nodes" : 18,
                    "init" : "he_unif",
                    "activation" : "relu"},
                {   "uuid" : str(uuid.uuid4()),
                    "type" : "dense",
                    "nodes" : 8,
                    "init" : "uniform",
                    "activation" : "tanh"} ],
                "num_inp" : 4,
                "num_out" : 2 }
            ]

	mdls = [
		  {"name" : "AMD Stock Model",
		   "creator" : auth.user_id,
		   "mclass" : "deep-nnet",
                   "status" : "training",
		   "uuid" : uuid.uuid4(),
                   "arch" : json.dumps(stcts[0])},
		  {"name" : "Housing Price Model",
		   "creator" : auth.user_id,
		   "mclass" : "deep-nnet",
                   "status" : "predicting",
		   "uuid" : uuid.uuid4(),
                   "arch" : json.dumps(stcts[1])},
		  {"name" : "Simple Clustering",
		   "creator" : auth.user_id,
		   "mclass" : "cluster",
                   "status" : "idle",
		   "uuid" : uuid.uuid4(),
                   "arch" : json.dumps(stcts[2])},
		  {"name" : "N-Body Model New",
		   "creator" : auth.user_id,
		   "mclass" : "deep-nnet",
                   "status" : "idle",
		   "uuid" : uuid.uuid4(),
                   "arch" : json.dumps(stcts[0])},
		  {"name" : "Census Data 2012",
		   "creator" : auth.user_id,
		   "mclass" : "deep-nnet",
                   "status" : "training",
		   "uuid" : uuid.uuid4(),
                   "arch" : json.dumps(stcts[2])}
		 ]

	for mdl in mdls :
		db['models'].insert(**mdl)

	db.commit()

	trs = [
			{"status" : "active", "tclass" : "train", "uuid" : uuid.uuid4(),"creator" : auth.user_id,
			 "model" : db(db.models.name == "Simple Clustering").select().first() },
			{"status" : "failed", "tclass" : "train", "uuid" : uuid.uuid4(),"creator" : auth.user_id,
			 "model" : db(db.models.name == "AMD Stock Model").select().first() },
			{"status" : "active", "tclass" : "predict", "uuid" : uuid.uuid4(), "creator" : auth.user_id,
			 "model" : db(db.models.name == "Housing Price Model").select().first() },
			{"status" : "success", "tclass" : "predict", "uuid" : uuid.uuid4(),
			 "model" : db(db.models.name == "N-Body Model New").select().first() },
			{"status" : "failed", "tclass" : "train", "uuid" : uuid.uuid4(),"creator" : auth.user_id,
			 "model" : db(db.models.name == "Census Data 2012").select().first() },
			{"status" : "active", "tclass" : "predict", "uuid" : uuid.uuid4(), "creator" : auth.user_id,
			 "model" : db(db.models.name == "Simple Clustering").select().first() }
		]

	for t in trs :
		db['transactions'].insert(**t)

	print db(db.models).select()
	print db(db.transactions).select()
	return True
