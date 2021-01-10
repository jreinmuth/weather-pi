#!/usr/bin/python
import flask

import os, sys, sqlite3
from flask import request,jsonify

# Initialize variables and constants
DEBUG = False
PATH_TO_DB = "/var/db/weather.db"

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d 

app = flask.Flask(__name__)
app.config["DEBUG"] = True

@app.route('/weather', methods =['GET'])
def weather():
    connection = sqlite3.connect(PATH_TO_DB)
    cursor = connection.cursor()
    sql = """SELECT * FROM WEATHER ORDER BY recorded_datetime DESC LIMIT 1;"""
    cursor.execute(sql)
    result = cursor.fetchone()
    if DEBUG:
         print(result)
    connection.close()
    return jsonify(dict_factory(cursor,result))

app.run(host='0.0.0.0')