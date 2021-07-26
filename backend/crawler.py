from bs4 import BeautifulSoup
import os
import requests
import pandas as pd
from selenium import webdriver
import threading
from csv import writer
import math

movies = pd.read_csv('ml-25m/links.csv')
tmdbId = movies['tmdbId']

notfound = pd.read_csv('update.csv')  #incase code is resumed it will not iterate through those who dont have images
notfoundList = notfound['notfoundids']

i=0
flag = True

def extract(id):
    if os.path.exists(f'movieImages/{id}.jpg'):
        return
    if id in notfoundList.values:
        return
    if math.isnan(id):
        return
    try:
        driver = webdriver.Chrome("C:/Users/ckjag/Downloads/chromedriver.exe")

        driver.get(f'https://www.themoviedb.org/movie/{id}')

        soup = BeautifulSoup(driver.page_source,"html.parser")
        imagetag = soup.findAll("img",{"class":"poster lazyload lazyloaded"})
        link = imagetag[0]["src"]
        
        url = 'https://www.themoviedb.org' + link
        # os.makedirs(f'movieImages', exist_ok=True)
        with open(f'movieImages/{id}.jpg', 'wb') as fh:
            fh.write(requests.get(url).content)
            
    except:
        
        # Open our existing CSV file in append mode
        # Create a file object for this file
        with open('update.csv', 'a', newline='') as f_object:
        
            # Pass this file object to csv.writer()
            # and get a writer object
            writer_object = writer(f_object)
        
            # Pass the list as an argument into
            # the writerow()
            writer_object.writerow([id])
            f_object.close()
    finally:
        driver.quit()


while(flag):
    threads=[]
    for j in range(i,7+i):
        if j<len(tmdbId):
            t = threading.Thread(target=extract,args=(tmdbId[j],))
            t.start()
            threads.append(t)
        else:
            flag = False
            break

    for thread in threads:
        thread.join()
    i=i+7

    
    


    
    





