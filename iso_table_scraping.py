from datapackage import Package
import pandas as pd

##Download ISO country code used to map ISO webpage for each country e.g. IN for https://www.iso.org/obp/ui/#iso:code:3166:IN
package = Package('https://datahub.io/core/country-list/datapackage.json')

# print list of all resources:
print(package.resource_names)

# print processed tabular data (if exists any)
for resource in package.resources:
    if resource.descriptor['datahub']['type'] == 'derived/csv':
        data = resource.read()
        print(data)

#convert to dataframe, select useful column, change country code to uppercase
country_code2 = pd.DataFrame(data)
country_code2.columns = ['ISO_COUNTRY_NM', 'ISO_COUNTRY_2_CD']
country_code2['ISO_COUNTRY_NM'] = country_code2['ISO_COUNTRY_NM'].apply(lambda x: x.upper())

#import packages for web scraping 
from IPython.core.interactiveshell import InteractiveShell
InteractiveShell.ast_node_interactivity = "all"
import requests
from requests import get
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
import lxml.html as lh
from selenium import webdriver
import time
from selenium.webdriver.chrome.options import Options

#Retry the request 3 times if any exception occurs
@retry(Exception, tries=4)

#get subdivision table 
def getsubdivisions():
   
    subdivisions_list = [] #variable to hold all countries data
    
    #get urls
    country_urls = ["https://www.iso.org/obp/ui/#iso:code:3166:"+item for item in iso_country_2_cd]

    for country_url in country_urls:
            
        page = requests.get(country_url).text
        soup = BeautifulSoup(page, 'lxml')
        
        #installed Selenium WebDriver for Chrome browser, we pass the driver path and initiator the WebDriver
        _path = 'C:/Users/irwang/AppData/Local/Packages/Microsoft.MicrosoftEdge_8wekyb3d8bbwe/TempState/Downloads/chromedriver_win32/chromedriver'
        #Using the ChromeOptions class for setting ChromeDriver-specific capabilities
        chrome_options = webdriver.ChromeOptions()
        #Prevent notification bar
        chrome_options.add_argument("--disable-infobars")
        #initial the WebDriver
        driver = webdriver.Chrome(executable_path = _path, chrome_options=chrome_options)

        driver.get(country_url)
        
        #Wait for 2 seconds
        time.sleep(2) 
        
        #use driver as the object of page source 
        soup = BeautifulSoup(driver.page_source)

        #find table in the source code
        try:
            table = soup.find('table', {'class':'tablesorter'})

            subdivisions = pd.read_html(str(table))[0]

            subdivisions_list.append(subdivisions)    

        except:
            print('No Table for This Country!')
            
            continue

    return pd.concat(subdivisions_list, axis=0)


if __name__ == "__main__":
    
    subdivisions_list = getsubdivisions()
    
    print(subdivisions_list)
                           

#convert into dataframe
subdivisions_allcountry = pd.DataFrame(subdivisions_list)
subdivisions_allcountry.head()
#read into csv
subdivisions_allcountry.to_csv('subdivisions_allcountry.csv')
