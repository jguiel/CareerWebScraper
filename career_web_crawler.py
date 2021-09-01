#! python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 17:12:17 2021
@author: Justin Guiel
"""


#%%

# Import web request module, HTML parsing module, and smtplib module to send email alert
import requests
from bs4 import BeautifulSoup
import smtplib

#Email recipient addresses for job alert
#Input any address that would like to receive updates on listings
toAddress = ['email@domain.com', 'email2@domain2.com']


#%%

# Insert specific URL for job board of interest here
career_listings_url = 'https://domain.com/careers'

#User-Agent info, fill in with own information
#Can be acquired from whatsmyuseragent.org
headers = {'User-Agent': 'PASTE USER AGENT HERE'}

# Requests HTML and creates soup object for clarity of code
page = requests.get(career_listings_url, headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')


#%%

#Read through parsed HTML to find ID for job listings and input below
all_results = soup.find(id='careers-list')

#Read through parsed HTML to find class name for job title
job_elements = all_results.find_all('td', class_='listing-title')
    
#Finds all job titles and iterates through them, adding to a job list
jobs = all_results.find_all('a', target='_blank')
job_list = [job.text for job in jobs]
    
    
#%%

# FIRST RUN ONLY
# COMMENT OUT AFTER INITIAL RUN
# Creates a current_jobs.txt with job list based on what is currently available on career board
# Will be used as comparison for changes in postings during subsequent runs

# with open('../CareerWebScraperGH/current_jobs.txt', 'w') as current_jobs:
#     [current_jobs.write(job + '\n') for job in job_list]
#     current_jobs.close()


#%%

# Creates list of jobs from previous time code was run
with open('../CareerWebScraperGH/current_jobs.txt', 'r') as prev_jobs:
    previous_job_list = [job.strip('\n') for job in prev_jobs.readlines()]
    prev_jobs.close()

# Detects job change according to current listings vs previous listings
job_change = previous_job_list != job_list


#%%

# Removes any job listings that have been filled or taken down from job board
with open('../CareerWebScraperGH/current_jobs.txt', 'r+') as update_jobs:
    # Saves previous list of jobs
    oldjobs = update_jobs.readlines()
    # Clears and inputs updated list, removing any listings that have been filled
    update_jobs.truncate(0)
    update_jobs.seek(0)
    [update_jobs.write(job) for job in oldjobs if job.strip('\n') in job_list]
    update_jobs.close()


#%%

# Determines new job listings, and appends them to .txt file for next code cycle
# New listings are added so they are not recognized next time code is run
new_jobs_added_list = [job for job in job_list if job not in previous_job_list]
new_jobs_added = '\n'.join(new_jobs_added_list)
with open('../CareerWebScraperGH/current_jobs.txt', 'a') as current_jobs:
    current_jobs.write(new_jobs_added)
    current_jobs.close()


#%%

# Drafts email with subject line and body of choice
# Includes list of new job openings posted
email_body = 'Subject: A job listing has been added\n\nJobs added: \n%s' % (new_jobs_added)
# Fixes bug with non-ascii characters
email_body = email_body.encode('ascii', 'replace')

# Input the email domain, address, and password which will send alert
alert_email_address = 'email address'
alert_email_pass = 'email password'
email_domain = 'smtp.DOMAIN.COM'

# Sends email if there has been a change in jobs
if job_change == True:
    conn = smtplib.SMTP(email_domain, 587) 
    conn.ehlo()
    conn.starttls()
    conn.login(alert_email_address, alert_email_pass) 
    conn.sendmail(alert_email_address, toAddress, email_body)
    conn.quit()


#%%

# OPTIONAL
# Sends email if no change was found in job postings
else:
    conn = smtplib.SMTP(email_domain, 587)
    conn.ehlo()
    conn.starttls()
    conn.login(alert_email_address, alert_email_pass) 
    conn.sendmail(alert_email_address, toAddress, 'Subject: No jobs have been added')
    conn.quit()