# -*- coding: utf-8 -*-
import uuid
from sys import stderr
import task_lib, json, csv
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


def deletedb():
    redirect(URL('default', 'deletedb'))

def populate():
    redirect(URL('default', 'populate'))

def index():
    if not auth.user_id :
        redirect(URL('default', 'index'))
    return dict(logged_in=("true" if auth.user_id != None else "false"),
                user_id=auth.user_id if auth.user_id else -1,
                models=[], transactions=[],
                user_data_url=user_data_url,
                murl=murl, turl=turl)
def model():
    try :
        if not auth.user_id :
            redirect(URL('default', 'index'))
        iid = int(request.args(0))
        model = db(db.models.id == iid).select().first()
        return dict(logged_in=("true" if auth.user_id != None else "false"),
                        user_id=auth.user_id if auth.user_id else -1, model_id=iid,
                        train_url=train_url, eval_url=eval_url, predict_url=predict_url,
                        user_data_url=user_data_url,
                        turl=turl, mdurl=mdurl, model=model, transactions=[])
    except :
        redirect(URL('dashboard', 'index'))

def models():
    try:
        if not auth.user_id :
            redirect(URL('default', 'index'))
        return dict(logged_in=("true" if auth.user_id != None else "false"),
                    user_id=auth.user_id if auth.user_id else -1,
                    murl=murl, models=[], transactions=[])
    except :
        redirect(URL('dashboard', 'index'))

def create():
    try:
        if not auth.user_id :
            redirect(URL('default', 'index'))
        return dict(logged_in=("true" if auth.user_id != None else "false"),
                    user_id=auth.user_id if auth.user_id else -1,
                    mdurl=mdurl, murl=murl, new_url=new_url,
                    tdurl=tdurl,  edit_url=edit_url, model={}, transactions=[])
    except :
        redirect(URL('dashboard', 'index'))

def activity():
    try:
        if not auth.user_id :
            redirect(URL('default', 'index'))
        return dict(logged_in=("true" if auth.user_id != None else "false"),
                    user_id=auth.user_id if auth.user_id else -1,
                    turl=turl, mdurl=mdurl, murl=murl, tdurl=tdurl)
    except :
        redirect(URL('dashboard', 'index'))


def mdlrequest():
    try:
        if not auth.user_id :
            redirect(URL('default', 'index'))
        iid = int(request.vars.get('tid'))
        return dict(logged_in=("true" if auth.user_id != None else "false"),
                    user_id=auth.user_id if auth.user_id else -1,
                    trans_id=iid, turl=turl, mdurl=mdurl, murl=murl, tdurl=tdurl)
    except :
        redirect(URL('dashboard', 'index'))



def do_logout() :
    redirect(URL('default', 'user', args=['logout']))

def do_login() :
    redirect(URL('default', 'user', args=['login']))

def do_register() :
    redirect(URL('default', 'user', args=['register']))
