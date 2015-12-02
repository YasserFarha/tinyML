# -*- coding: utf-8 -*-
import uuid


def deletedb():
    redirect(URL('default', 'deletedb'))

def populate():
    redirect(URL('default', 'populate'))

def index():
	if not auth.user_id :
		redirect(URL('default', 'index'))
	murl = URL('default', 'load_models', user_signature=True)
	turl = URL('default', 'load_transactions', user_signature=True)
	return dict(logged_in=("true" if auth.user_id != None else "false"),
                user_id=auth.user_id if auth.user_id else -1,
				models=[], transactions=[],
				murl=murl, turl=turl)

def model():
	if not auth.user_id :
		redirect(URL('default', 'index'))
	iid = int(request.args(0))
	model = db(db.models.id == iid).select().first()
	return dict(logged_in=("true" if auth.user_id != None else "false"),
                user_id=auth.user_id if auth.user_id else -1,
				model=model, transactions=[])
def models():
	if not auth.user_id :
		redirect(URL('default', 'index'))
	murl = URL('default', 'load_models', user_signature=True)
	turl = URL('default', 'load_transactions', user_signature=True)
	return dict(logged_in=("true" if auth.user_id != None else "false"),
                user_id=auth.user_id if auth.user_id else -1,
                murl=murl, models=[], transactions=[])

def create():
	if not auth.user_id :
		redirect(URL('default', 'index'))
	murl = URL('default', 'load_models', user_signature=True)
	new_url = URL('dashboard', 'add_model', user_signature=True)
	edit_url = URL('dashboard', 'edit_model', user_signature=True)
	return dict(logged_in=("true" if auth.user_id != None else "false"),
                    user_id=auth.user_id if auth.user_id else -1,
                    murl=murl, new_url=new_url, edit_url=edit_url, model={}, transactions=[])

@auth.requires_signature()
def load_models():
    page = int(request.vars.get('page', 1))
    page_size = int(request.vars.get('page_size', 20))
    pb = int(page-1)*(int(page_size))
    pe = int(page)*(int(page_size))
    trs = db(db.models.creator == auth.user_id).select(orderby=~db.models.created_at, limitby=(pb, pe))
    return response.json(dict(models=trs))

@auth.requires_signature()
def load_model():
    iid = int(request.args(0))
    trs = db(db.models.id == iid).select().first()
    return response.json(dict(models=trs))

@auth.requires_signature()
def add_model():
    name = request.vars.get('name', '');
    mclass = request.vars.get('mclass', '');
    muuid = request.vars.get('uuid', uuid.uuid4());
    arch = request.vars.get('arch');
    db['models'].insert(
                name=name,
                mclass=mclass,
                uuid=muuid,
                arch=arch,
                status="idle",
                creator = auth.user_id)
    return response.json(dict(model=db(db.models.uuid == muuid).select().first()))


@auth.requires_signature()
def edit_model():
    name = request.vars.get('name', '');
    mclass = request.vars.get('mclass', '');
    muuid = request.vars.get('uuid', uuid.uuid4());
    arch = request.vars.get('arch');
    model = db(db.models.uuid == muuid).select().first()
    model.update_record(
                name=name,
                mclass=mclass,
                uuid=muuid,
                arch=arch,
                status="idle",
                creator = auth.user_id)
    return response.json(dict(model=model))

@auth.requires_signature()
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

