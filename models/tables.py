import datetime
import uuid

"""
This table defines all of the models that can be created by users.
Each model represents one neural network customized and owned by a given
user on tinyML. The user is free to customize the architecture of the model
such as the number of input and output nodes, hidden layerts, activation functions, etc.
The models can then be trained with data supplied by the user, and for each training session
a transaction is generated that identifies that training session uniquely.
"""
db.define_table('models',
        Field('name', 'string'), # @TODO set default to be user_id+model_id or something
        Field('name_short', 'string'), # @TODO set default to be user_id+model_id or something
        Field('mclass', 'string'),
        Field('uuid', 'string', default=str(uuid.uuid4())),
        Field('creator', db.auth_user, default=auth.user_id),
        Field('created_at', 'datetime', default=datetime.datetime.now()),
        Field('updated_at', 'datetime', default=datetime.datetime.now()),
        Field('status', 'string'), # @TODO - define statuses (training, active, busy, new)
        Field('arch_json', 'string'), # raw model architecture in full json rep
	Field('compiled', 'boolean', default=False),
	Field('trained', 'boolean', default=False),
        Field('weights', 'text'), # hd5 file describing the weight for the current model
        Field('arch', 'string')) # json describing layers in short-syntax, convenient for UI stuff


db.define_table('transactions',
        Field('tclass', 'string'),
        Field('uuid', 'string', default=str(uuid.uuid4())),
        Field('model', 'reference models'),
        Field('model_name', 'string'),
        Field('model_name_short', 'string'),
        Field('creator', db.auth_user, default=auth.user_id),
        Field('created_at', 'datetime', default=datetime.datetime.now()),
        Field('finished_at', 'datetime'),
        Field('status', 'string'))
