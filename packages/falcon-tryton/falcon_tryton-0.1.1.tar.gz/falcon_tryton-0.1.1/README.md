Falcon-Tryton
============

Adds Tryton support to Falcon application.


```
#! -*- coding: utf8 -*-

from functools import wraps
from falcon_tryton import Tryton
import falcon
import os

CONTEXT = None
CONFIG = {}
CONFIG['TRYTON_DATABASE'] = os.environ.get('DB_NAME', 'mydb') 
CONFIG['TRYTON_USER'] = 0

app = falcon.App()

tryton = Tryton(app, CONFIG)

User = tryton.pool.get('res.user')
        
# @tryton.default_context
# def default_context():
#     global CONTEXT
#     if not CONTEXT:
#         CONTEXT = User.get_preferences(context_only=True)
#     return CONTEXT    

class ApiUser:
    def __init__(self, tryton = None):
        self.tryton = tryton
        
    @tryton.transaction()
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        users = User.browse([1])       
        resp.media = {'name':users[0].name}

apiuser = ApiUser(tryton)

app.add_route("/user", apiuser)



# wsgi gunicorn o uwsgi:

""" example file wsgi_falcon.py:

            from app_falcon import app
"""
# important: no use app.run()

```
There are three configuration options available:

* `TRYTON_DATABASE`: the Tryton's database to connect.
* `TRYTON_USER`: the Tryton user id to use, by default `0` (aka `root`).


