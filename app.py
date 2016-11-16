#!local/bin/python

"""
@author  :  Rajan Khullar
@created :  09/06/16
@updated :  11/13/16
"""

import decor as dec

from flask import Flask, jsonify, json, request, abort
from flask import render_template
#from flask import Flask, Response, jsonify, json, request, abort, session, render_template, redirect, url_for

from error import apierror
from mail import send_thread_text

from core import core
from person import person
from location import location
from scan import scan
from time import time

BASEURL = 'https://csci870.nydev.me'
BASEAPI = BASEURL + '/api'

app = Flask(__name__)
apierror.apply(app)

# Authorization Methods
pswd = dec.corify(person.pswd)
token = dec.corify(person.token)
admin = dec.corify(person.admin_login)

# User Methods
register = dec.corify(person.register)
verification = dec.corify(person.verification)
verify = dec.corify(person.verify)

# Scan Methods
fetch_locations = dec.corify(location.dump)
persist_scan = dec.corify(scan.persist)

@app.route('/api/echo', methods=['GET', 'POST'])
def api_echo():
    if request.method == 'GET':
        return jsonify({'message': 'ok'})
    if request.method == 'POST':
        #return request.form['data']
        return request.json

@app.route('/api/time', methods=['GET'])
def api_time():
    resp = {'time': int(time())}
    return jsonify(resp)

@app.route('/api/authenticate')
@dec.auth(pswd)
def api_authenticate(userid):
    resp = {'message': 'ok'}
    return jsonify(resp)

@app.route('/api/admin')
@dec.auth(admin)
def api_admin(userid):
    resp = {'message': 'ok'}
    return jsonify(resp)

@app.route('/api/register', methods=['POST'])
@dec.json
def api_register():
    resp = {'message': 'not ok'}
    data = request.json
    t = register(**data)
    if(t):
        e = data['email']
        h = verification(t)
        u = '%s/verify/%s/%s' % (BASEURL, e, h)
        send_thread_text([e], 'nydev verify account', u)
        resp['message'] = 'ok'
    return jsonify(resp)

@app.route('/api/verify/<string:email>/<string:hash>', methods=['GET'])
def api_verify(email, hash):
    t = verify(email, hash)
    resp = {'message': 'ok'} if t else {'message': 'not ok'}
    return jsonify(resp)

@app.route('/verify/<string:email>/<string:hash>', methods=['GET'])
def web_verify(email, hash):
    t = verify(email, hash)
    if t:
        return render_template('verify.html')
    abort(400)

@app.route('/api/locations', methods=['GET'])
@dec.auth(pswd)
def api_locations(userid):
    n = 0
    resp = {'message': 'ok', 'building': [], 'floor': [], 'room':[]}
    for l in fetch_locations():
        resp['building'].append(l.building)
        resp['floor'].append(l.floor)
        resp['room'].append(l.room)
        n += 1
    resp['size'] = n
    return jsonify(resp)

@app.route('/api/scan', methods=['POST'])
@dec.auth(pswd)
@dec.json
def api_scan(userid):
    data = request.json
    data['userID'] = userid
    resp = {'message': 'not ok'}
    t = persist_scan(**data)
    if t:
        resp['message'] = 'ok'
        for k in data:
            resp[k] = data[k]
    return jsonify(resp)


if __name__ == '__main__':
    app.run(debug=True)