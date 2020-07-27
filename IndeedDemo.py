import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime 

def get_str(tup):
    if tup[0] == '':
        return tup[1]
    return tup[0]

def add_terms_indeed(df, terms):
    for term in terms:
        url = "https://www.indeed.com/jobs?q=" + term.replace(" ", "+") + "&fromage=1"
        #url =("https://www.linkedin.com/jobs/search?keywords=" + term.replace(" ", "%20") + 
        #      "&location=United%20States&trk=public_jobs_jobs-search-bar_search-submit&redirect=false&position=1&pageNum=0&f_TP=1")
        myRequest = requests.get(url)
        soup = str(BeautifulSoup(myRequest.text, "html.parser"))

        title_match = 'rel="noopener nofollow" target="_blank" title="([^"]+)'
        titles = [x.replace("amp;", "") for x in re.findall(title_match, soup)]

        match_1 = r'<span class="company">\n([^<]+)'
        match_2 = r'rel="noopener" target="_blank">\n([^<]+)'

        companies = [get_str(x).replace("amp;", "") for x in re.findall(match_1 + '|' + match_2, soup)]

        #/rc/clk?jk=c519269736acce4f&amp;fccid=de56d7554bea5214&amp;vjs=3
        url_match = r'data-tn-element="jobTitle" href="([^"]+)' 
        urls = ["https://www.indeed.com" + x.replace("amp;", "") for x in re.findall(url_match, soup)]

        location_match = r'data-rc-loc="([^"]+)'
        locations = re.findall(location_match, soup)

        new_df = pd.DataFrame()

        new_df['Platform'] = ["Indeed"] * len(companies)
        new_df['Search_Term'] = [term] * len(companies)
        new_df['Title'] = titles
        new_df['Company'] = companies
        new_df['Location'] = locations
        new_df['URL'] = urls
        new_df['Seniority'] = ["Not Applicable"] * len(companies)
        new_df['Type'] = ["Not Applicable"] * len(companies)
        new_df['Industry'] = ["Not Applicable"] * len(companies)
        new_df['Date_Queried'] = [datetime.now().date()] * len(companies)

        df = df.append(new_df).drop_duplicates().reset_index(drop=True)
        
    return df