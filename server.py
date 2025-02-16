#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request, redirect
import json
app = Flask(__name__)
app.debug = True

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }

class World:
    def __init__(self):
        self.clear()
        
    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data
        self.notify_all(entity,data)

    def clear(self):
        self.space = dict()
        self.listeners = dict()

    def get(self, entity):
        return self.space.get(entity,dict())
    
    def world(self):
        return self.space

    def post_world(self, c_world):

        self.space = c_world

    # notify all of listerners that data has been manipulated    
    def notify_all(self,entity,data):
        for listener in self.listeners:
            # only contain the data that has been manipulated
           self.listeners[listener][entity] = data

    def add_listener(self,listener_name):
        self.listeners[listener_name] = dict()

    def get_listener(self, listener_name):
        return self.listeners[listener_name]

    def clear_listener(self, listener_name):
        self.listeners[listener_name] = dict()

    def listener_exist_flag(self, listener_name):
        if listener_name not in self.listeners:
            return False
        return True
            



# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}' 

myWorld = World()         

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data.decode("utf8") != u''):
        return json.loads(request.data.decode("utf8"))
    else:
        return json.loads(request.form.keys()[0])

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''

    #returns the message we want to display in the user’s browser.
    return redirect("/static/index.html", code=302)

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface, add entity'''
    v = flask_post_json()
    myWorld.set( entity, v )
    e = myWorld.get(entity)    
    # flask has a security restriction in jsonify
    return json.dumps(e) # flask.jsonify( e )


@app.route("/world", methods=['GET'])    
def world():
    '''you should probably return the world here'''
    return json.dumps( myWorld.world() ) 


@app.route("/world/<c_world>", methods=['POST'])    
def post_world(c_world):
    '''you should probably return the world here'''
    myWorld.post_world(c_world)

    return json.dumps( myWorld.world() ) 


@app.route("/listener/<listener_id>", methods=['POST','PUT'])
def add_listener(listener_id):
    myWorld.add_listener( listener_id )

    # give enitre world when we register, to follow other listerners' step
    return flask.jsonify( myWorld.world() ) 

@app.route("/listener/<listener_id>", methods=['GET'])    
def get_listener(listener_id):

    if myWorld.listener_exist_flag(listener_id):
        v = myWorld.get_listener(listener_id)
        myWorld.clear_listener(listener_id)
    else:
        myWorld.add_listener(listener_id)
        v = dict()
        v["clear"] = "True"

    return flask.jsonify( v )


@app.route("/entity/<entity>", methods=['GET'])    
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    e = myWorld.get(entity)    
    # flask has a security restriction in jsonify
    return json.dumps( e ) # flask.jsonify( e )

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    myWorld.clear()
    return json.dumps(myWorld.world())

if __name__ == "__main__":
    app.run()
