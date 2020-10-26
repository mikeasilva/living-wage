# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 08:53:47 2016

@author: Michael Silva
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import re

# The year the data represent
data_year = 2020
web_page = requests.get('https://livingwage.mit.edu/')
soup = BeautifulSoup(web_page.content, 'lxml')
state_urls = list()
pages_with_data = list()
valid_page_list = ('/states', '/counties', '/metros')

# Build the list of state links
print('Getting state pages')
for link in soup.findAll('a'):
    if 'locations' in link['href']:
        state_urls.append('https://livingwage.mit.edu'+link['href'])

# Build the list of pages with data
print('Scrapping state pages for links to pages with data')
for state_url in state_urls:
    web_page = requests.get(state_url)
    soup = BeautifulSoup(web_page.content, 'lxml')
    for link in soup.findAll('a'):
        if(link['href'].startswith(valid_page_list)):
            pages_with_data.append('https://livingwage.mit.edu'+link['href'])

# Finally scrape the pages with data
for page_url in pages_with_data:
    print('Scrapping '+page_url)
    web_page = requests.get(page_url)
    soup = BeautifulSoup(web_page.content, 'lxml')
    # Pull the header from the first table
    column_headers = [th.getText() for th in soup.findAll('tr', limit=2)[1].findAll('td')]
    # Pull the data from the first table
    data_rows = soup.findAll('tr')[1:2]
    data = [[td.getText().strip() for td in data_rows[i].findAll('td')] for i in range(len(data_rows))]
    # Build a data frame to hold the data
    temp_df = pd.DataFrame(data, columns=column_headers)
    # Add in the FIPS code
    fips = re.findall('\d+', page_url)
    temp_df['FIPS Code']=fips[0]
    # Add in the location from the header
    location = soup.select('.container h1')[0].text
    location = location.replace('Living Wage Calculation for ','')
    temp_df['Location']=location
    temp_df['year'] = data_year
    temp_df['URL'] = page_url
    # Create or append to the final data frame
    if 'living_wage_df' in locals() or 'living_wage_df' in globals():
        living_wage_df = living_wage_df.append(temp_df)
    else:
        living_wage_df = temp_df

# Save it as an Excel file
print('Writing Data')
writer = pd.ExcelWriter(str(data_year)+' Living Wage.xlsx', engine='xlsxwriter')
living_wage_df.to_excel(writer, str(data_year), index=False)
writer.save()
