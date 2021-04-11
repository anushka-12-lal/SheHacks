# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 13:49:27 2021

@author: diksha
"""
from flask import Flask,render_template,request,redirect,url_for,session,make_response
from flask_mysqldb import MySQL
import os
import io
from io import StringIO
from os.path import join, dirname, realpath
import pandas as pd
import matplotlib.pyplot as plt
import MySQLdb.cursors
import re
from io import BytesIO
import json
import numpy as np
from transformers import AutoModelWithLMHead, AutoTokenizer


app=Flask(__name__)
app.secret_key='key1'

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='1234'
app.config['MYSQL_DB']='db1'

mysql=MySQL(app)
UPLOAD_FOLDER=r'.\static'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
df2 = pd.DataFrame()

def summarizer(text):
    model = AutoModelWithLMHead.from_pretrained("t5-small", return_dict=True)
    tokenizer = AutoTokenizer.from_pretrained("t5-small")
    
    bodyc=text
    
    inputs = tokenizer.encode("summarize: " + bodyc, return_tensors="pt", max_length=512)
    outputs = model.generate(inputs, max_length=200, min_length=10, length_penalty=2.0, num_beams=4, early_stopping=True)
    print(tokenizer.decode(outputs[0]))
    return tokenizer.decode(outputs[0])
    

@app.route('/')
def landing():
    return(render_template('index.html')) 

@app.route('/day')
def day():
    return render_template('How-was-Your-Day.html')

@app.route('/week')
def week():
    return render_template('Weekly-Mood.html')

@app.route('/relax')
def relax():
    return render_template('RELAX.html')
@app.route('/four')
def four():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM summarytext WHERE date=% s',('4apr', ))
    account=cursor.fetchone() 
    log=account['stext']
    sentiment=sentimentanalyzer(log)# sentiment analyzer function for sentiment analysis
    return render_template('April-4.html',summary=log)

@app.route('/five')
def five():
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM summarytext WHERE date=% s',('5apr', ))
    account=cursor.fetchone() 
    log=account['stext']
    sentiment=sentimentanalyzer(log)# sentiment analyzer function for sentiment analysis
    return render_template('April-5.html')    
    
@app.route('/uploader',methods=['GET','POST'])
def upload():
    if request.method=='POST':
        text=request.form['message']
        date=request.form['date']
        stext=summarizer(text)
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT into summarytext VALUES(NULL,% s,% s)',(stext,date, ))
        mysql.connection.commit()
        cursor.close()
    return stext
    
@app.route('/summary',methods=['GET','POST'])
def summary():
    msg=''
    if request.method=='POST' and 'text' in request.form and 'date' in request.form:
        text=request.form['text']
        date=request.form['date']
        stext=summarizer(text)
        cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        #cursor.execute('SELECT * FROM summarytext WHERE username=% s AND password=% s',(username,password, ))
        #summarytext=cursor.fetchone() 
        if summarytext:
            cursor.execute('INSERT into summarytext VALUES(NULL,% s,% s)',(stext,date, ))
            mysql.connection.commit()
            cursor.close()
            msg='You have successfully registered'
        else:
            msg='Error!'
    return render_template('page.html',msg=msg)