import datetime
import uuid

db.define_table('models',
        Field('name', 'string'), # @TODO set default to be user_id+model_id or something
        Field('uid', 'string', default=str(uuid.uuid4())),
        Field('owner', db.auth_user, default=auth.user_id),
        Field('created_at', 'datetime', default=datetime.datetime.now()),
        Field('updated_at', 'datetime', default=datetime.datetime.now()),
        Field('status', 'integer'), # @TODO - define statuses (training, active, busy, new)
        Field('ninputs', 'integer')) # number of input fields

