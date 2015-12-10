import datetime
import uuid

"""
This table defines all of the models that can be created by users.
Each model represents one neural network customized and owned by a given
user on tinyML. The user is free to customize the architecture of the model
such as the number of input and output nodes, hidden layerts, activation functions, etc.
The models can then be trained with data supplied by the user, and for each training session
a transaction is generated that identifies that training session uniquely.

valid @mclass values :  Deep nnet
valid @status values :idle, compiling, training, predicting, broken
"""
db.define_table('models',
        Field('name', 'string'), # @TODO set default to be user_id+model_id or something
        Field('name_short', compute=lambda x : x['name'][:12]), 
        Field('mclass', 'string'),
        Field('uuid', 'string', default=str(uuid.uuid4())),
        Field('creator', db.auth_user, default=auth.user_id),
        Field('created_at', 'datetime', default=datetime.datetime.now()),
        Field('updated_at', 'datetime', default=datetime.datetime.now()),
        Field('status', 'string'), # @TODO - define statuses (training, active, busy, new)
        Field('arch_json', 'blob'), # raw model architecture in full json rep
	Field('compiled', 'boolean', default=False),
	Field('trained', 'boolean', default=False),
        Field('weights', 'blob'), # hd5 file describing the weight for the current model
        Field('arch', 'blob')) # json describing layers in short-syntax, convenient for UI stuff

"""
The transactions table defines a list of all transactions that occur in the tinyML system,
where a transaction is defined as a single unit of interaction with any given model. This means
that requests to create, edit, train, or use models for prediction will cause a transaction to
be generated that tracks the status and meta-data associated with that transaction.

valid @tclass values : created/edit/train/predict
valid @status values : active/success/failed
"""

get_abstract = lambda x: json.loads(x['output_payload'])['abstract']
db.define_table('transactions',
        Field('tclass', 'string'),
        Field('uuid', 'string', default=str(uuid.uuid4())),
        Field('model', 'reference models'),
        Field('model_name', 'string'),
        Field('model_name_short', 'string'),
        Field('creator', db.auth_user, default=auth.user_id),
        Field('created_at', 'datetime', default=datetime.datetime.now()),
        Field('finished_at', 'datetime'),
        Field('input_payload', 'blob'), # json struct containing fields for training/prediction parameters
        Field('output_payload', 'blob'), # json struct containing output info like results, logs, epochs, weights, etc.
        Field('status', 'string'),
        Field('tresult', compute=get_abstract), # the output of the transaction, contains training/prediction results # for those types of requests. 
        Field('tresult_short', compute=lambda x : x['tresult'][:100]))
                                 

"""
This table defines all labeled training/ unlabeled usage data that a user wants to store on our servers
and have associated with their account. This 

valid @dclass : training_input, training_labels, training_input_labels, predict_input

note that training_input_labels requires that the first n columns be the input values, and the last m be the labels,
where n is the number of inputs for the model and m the number of outputs
"""
db.define_table('user_uploads', 
        Field('dclass', 'string'), # class such as training data, unlabeled data, etc.
        Field('name', 'string'),
        Field('description', 'text', default=""),
        Field('payload', 'blob'),
        Field('extension', 'string'), # either .csv or .txt
        Field('created_at', 'datetime'),
        Field('size_KB', 'float'),
        Field('rcount', 'integer'),
        Field('ccount', 'integer'),
        Field('downer', db.auth_user, default=auth.user_id))
