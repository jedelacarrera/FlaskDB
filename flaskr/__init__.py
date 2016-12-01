#!/usr/bin/python3
# -*- coding: latin-1 -*-
import os
import sys
import psycopg2
import json
from bson import json_util
from pymongo import MongoClient
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


def create_app():
    app = Flask(__name__)
    return app

app = create_app()

# REPLACE WITH YOUR DATABASE NAME
MONGODATABASE = "myDatabase"
MONGOSERVER = "localhost"
MONGOPORT = 27017
client = MongoClient(MONGOSERVER, MONGOPORT)
mongodb = client[MONGODATABASE]

# Uncomment for postgres connection
# REPLACE WITH YOUR DATABASE NAME, USER AND PASS

"""
POSTGRESDATABASE = "myDatabase"
POSTGRESUSER = "user"
POSTGRESPASS = "password"
postgresdb = psycopg2.connect(
    database=POSTGRESDATABASE,
    user=POSTGRESUSER,
    password=POSTGRESPASS)
"""

QUERIES_FILENAME = '/var/www/flaskr/queries'

# Path para local
# QUERIES_FILENAME = 'queries'


@app.route("/")
def home():
    try:
        with open(QUERIES_FILENAME, 'r', encoding='utf-8') as queries_file:
            json_file = json.load(queries_file)
            pairs = [(x["name"],
                      x["database"],
                      x["description"],
                      x["query"],
                      x["params"]) for x in json_file]
            return render_template('file.html', results=pairs)
    except(FileNotFoundError):
        with open('queries', 'r', encoding='utf-8') as queries_file:
            json_file = json.load(queries_file)
            pairs = [(x["name"],
                      x["database"],
                      x["description"],
                      x["query"],
                      x["params"]) for x in json_file]
            return render_template('file.html', results=pairs)


@app.route("/mongo")
def mongo():
    try:
        lista = request.args.get("query").split('-')
        query = lista[0]
        if len(lista) > 1:
            args = lista[1:]
            while query.find('param') != -1:
                pos = query.find('param')
                num = query[pos + 5]
                query = query.replace('param'+num, args[int(num) - 1])
        if 'messages.find({$and: [{$or: [{"sender":' in query:
            string = query[query.find]
            results = mongodb.messages.find({'$and': [{'$or': [{"sender": 3}, {"sender": 33}]}, {'$or': [{"receptant": 3}, {"receptant": 33}]}]}, {"_id": 0, "date": 1, "sender": 1, "message":1, "receptant": 1})
        results = eval('mongodb.'+query)
        results = json_util.dumps(results, sort_keys=True, indent=4)
        if "find" in query:
            return render_template('mongo.html', results=results)
        else:
            return "ok"
    except:
        return render_template('mongo.html', results={'query': query, 'problema': 'falta la base de datos de mongo'})


@app.route("/postgres")
def postgres():
    try:
        query = request.args.get("query")
        cursor = postgresdb.cursor()
        cursor.execute(query)
        results = [[a for a in result] for result in cursor]
        print(results)
        return render_template('postgres.html', results=results)
    except:return render_template('postgres.html', results=[['status', 'Error'],['Ricci hola', ' wayo hola'], ['query', query]])



@app.route("/example")
def example():
    return render_template('example.html')

@app.route("/map")
def map():
    return render_template('leaflet.html')


if __name__ == "__main__":
    app.run()
