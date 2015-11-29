# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
def home() :
    redirect(URL('default', 'boards'))

@auth.requires_signature()
def dashboard():
	return dict(logged_in=("true" if auth.user_id != None else "false"),
                 user_id=auth.user_id if auth.user_id else -1)

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

