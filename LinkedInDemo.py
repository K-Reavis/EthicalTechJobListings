import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime 

def add_terms_linkedin(df, terms):
    for term in terms:
        url =("https://www.linkedin.com/jobs/search?keywords=" + term.replace(" ", "%20") + 
              "&location=United%20States&trk=public_jobs_jobs-search-bar_search-submit&redirect=false&position=1&pageNum=0&f_TP=1")
        myRequest = requests.get(url)
        soup = str(BeautifulSoup(myRequest.text, "html.parser"))

        title_match = r'<span class="screen-reader-text">([^<]+)'
        titles = [x.replace("amp;", "") for x in re.findall(title_match, soup)]

        company_match = r'alt="([^"]+)'
        companies = [x.replace("amp;", "") for x in re.findall(company_match, soup)][:-1]

        url_match = r'href="https://www.linkedin.com/jobs/view([^"]+)' 
        urls = ["https://www.linkedin.com/jobs/view" + x for x in re.findall(url_match, soup)]

        location_match = r'<span class="job-result-card__location">([^<]+)'
        locations = re.findall(location_match, soup)

        seniorities = []
        types = []
        industries = []

        for url in urls:
            urlRequest = requests.get(url)
            soup = str(BeautifulSoup(urlRequest.text, "html.parser"))

            subhead = '<h3 class="job-criteria__subheader">'
            criteria = '</h3><span class="job-criteria__text job-criteria__text--criteria">([^<]+)'

            seniority_match = subhead + 'Seniority level'+ criteria
            seniorities.append(re.findall(seniority_match, soup)[0])

            type_match = subhead + 'Employment type' + criteria
            types.append(re.findall(type_match, soup)[0])

            industry_match = subhead + 'Industries' + criteria
            industries.append(re.findall(industry_match, soup)[0].replace("amp;", ""))

        new_df = pd.DataFrame()

        new_df['Platform'] = ["LinkedIn"] * len(companies)
        new_df['Search_Term'] = [term] * len(companies)
        new_df['Title'] = titles
        new_df['Company'] = companies
        new_df['Location'] = locations
        new_df['URL'] = urls
        new_df['Seniority'] = seniorities
        new_df['Type'] = types
        new_df['Industry'] = industries
        new_df['Date_Queried'] = [datetime.now().date()] * len(companies)

        df = df.append(new_df).drop_duplicates().reset_index(drop=True)
        
    return df