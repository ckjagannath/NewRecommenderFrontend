from flask import Flask,request
from flask_cors import CORS
import re
import pandas as pd
from pandas import DataFrame as df
import json
import numpy as np
from runtime_topmov import build_chart
from runtime_100k import make_recommendation_newuser

app = Flask(__name__)
cors = CORS(app)

#loading saved movies_info
movies_info = pd.read_csv('movies_info.csv')
movieNames = movies_info['title']
"""
    taking the title column and preparing a new dataframe of lower case titles from it
    without changing the index, Line: 39 & 40
"""
movieNamesInLowerCase = list(map(lambda y:y.lower(),movieNames))  
df2 = df(movieNamesInLowerCase, columns=['lowercasetitles'])

@app.route('/api/search', methods=['POST'])
def searchString():
    data = json.loads(request.data.decode('utf-8'))
    searchstring = data['searchstring']
    if len(searchstring) == 0:              # if search is empty return []
        return json.dumps([])
    x = re.compile(searchstring.lower())    #converting searchstring to regex object
       
    matched = list(filter(x.search,movieNamesInLowerCase))    #matched movienames from searchstring
    """
        filter returns an iterator of the 'true' based values from re.search() 
        and applying list() to it actauuly gives the matched values
    """
    # print(matched)
    
    matched = list(map(lambda z: df2[df2['lowercasetitles'] == z].index.tolist(), matched)) # getting indexes of matched titles
    matched = list(map(lambda z: (movieNames[z[0]], movies_info['tmdbId'][z[0]]), matched)) #using indexes retrieving the actual titles from movieNames frame so originally present case is maintained
    
    return json.dumps(matched[0:5]) # returning first five matches if present

@app.route('/api/genre', methods=['POST'])
def getChartbyGenre():
    data = json.loads(request.data.decode('utf-8'))
    genre = data["genre"]
    chart_df = build_chart(genre).head(15)
    ids = list(chart_df['tmdbId'].values)
    print("in genre", type(ids))
    return json.dumps(ids)

@app.route('/api/recommend', methods=['POST'])
def Recommended():
    data = json.loads(request.data.decode('utf-8'))
    tmdbid = float(data['value'])
    idx = movies_info[movies_info['tmdbId'] == tmdbid]['movieId'].values[0]
    recChart = make_recommendation_newuser(idx).dropna(subset=['tmdbId'])
    recChart = list(recChart['tmdbId'].values)
    print("in rec", type(recChart))
    return json.dumps(recChart)