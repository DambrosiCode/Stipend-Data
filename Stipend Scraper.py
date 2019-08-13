from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

url="http://www.phdstipends.com/results"

#get table to open
driver=webdriver.Firefox()
driver.get(url)

col=[] #collection of data
page=0 #current page

#this function will parse through the website and collect data on each page
def page_parser():
    #scrape data
    stipend_soup=BeautifulSoup(driver.page_source, 'lxml')
    level1=stipend_soup.find('table',{'id':'mytable'})
    level2=level1.find('tbody')
    global page
    
    #Every time a page is fully scraped, click to the next one
    i = 0
    for stats in level2.findAll('td'):
        col.append(stats.get_text())
        i+=1
        #run for 350 items in table in 128 pages
        if i==350 and page<=128:
            page+=1
            try:
                #click to the 'next page' button and then run the function again
                driver.find_element_by_xpath('//*[@id="mytable_next"]/a').click()
                page_parser()
            except:
                pass
        else:
            pass
    
page_parser()

import pandas as pd
import numpy as np

#Make seven titled columns
stipend_stats=pd.DataFrame(np.reshape(col,(-1,7)))
stipend_stats.columns=["University",
                       "Subject",
                       "Stipend",
                       "LW Ratio",
                       "Academic Year",
                       "Program Year",
                       "Comments"]
                       
#Save as a .csv so I don't have to worry about re-scraping the data later
stipend_stats.to_csv("stipend_stats.txt",sep='\t')
stipend_stats = pd.read_csv('Stipend_Stats.txt', sep='\t')

stipend_stats = stipend_stats.iloc[:,:-1].dropna().reset_index(drop=True)

import re 
  
#remove anything in parenthesis
def Clean_names(name): 
    if re.search(r'\([^)]*\)', str(name)): 
        pos = re.search(r'\([^)]*\)', str(name)).start() 
        return name[:pos] 
  
    else: 
        return name 

stipend_stats['University'] = stipend_stats['University'].apply(Clean_names) 
stipend_stats

#Clean the Stipend column of all special characters
stipend_stats['Stipend'] = stipend_stats['Stipend'].str.replace(',', '')
stipend_stats['Stipend'] = stipend_stats['Stipend'].str.replace('$', '')
stipend_stats['Stipend'] = pd.to_numeric(stipend_stats['Stipend'])

from geopy.geocoders import Nominatim
from tqdm import tqdm
import time

geolocator = Nominatim(user_agent="Stipend")
stipend_stats["Location"]='' #New location column

#get location
def get_locs(i):
    try:
        location = geolocator.geocode(stipend_stats["University"][i], addressdetails=True)
        loc = location.raw
        return(loc['address'])       
    except:
        print("ERROR") #Print ERROR everytime a location can't be found
        return('NA')

    
for i in tqdm(range(len(stipend_stats))):
    stipend_stats["Location"][i] = get_locs(i)
    stipend_stats.to_csv('Stipend.txt', sep='\t')
    time.sleep(.5) #gotta go slow

print(len(stipend_stats)-len(stipend_stats.dropna()))/len(stipend_stats)) #only about 15% was lost

#remove the rows with missing locations
stipend_stats = stipend_stats.dropna().reset_index(drop=True) 

#Save to CSV again
stipend_stats = pd.read_csv('Stipend.txt', sep='\t')

from ast import literal_eval
#when reading from CSV convert string to dictionary
stipend_stats['Location'] = stipend_stats['Location'].apply(lambda x: literal_eval(x))

#Dictionary keys to columns
loc = stipend_stats['Location'].apply(pd.Series)
#Capitalize first letter in column names
loc.columns = map(str.capitalize, loc.columns)

#merge location and stipend_stats dataframes
stipend_loc = pd.concat([loc, stipend_stats], axis = 1)

#remove second University column
stipedn_loc = stipend_loc.iloc[:,~stipend_loc.columns.duplicated()]
#remove Location column
stipend_loc = stipend_loc.drop(['Location', 'Unnamed: 0', 'Unnamed: 0.1'], axis =1 )

#Save to CSV one last time
stipend_loc.to_csv('Stipe And Locations.txt', sep='\t')
