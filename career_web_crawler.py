"""
Created Aug 25 2021
@author: Justin Guiel
"""

import os
import sys
import time
import requests
import smtplib
import argparse
from bs4 import BeautifulSoup
from dotenv import load_dotenv


load_dotenv()
# Path to .txt file created and read by script. Store path in .env file
CURRENT_JOBS_PATH = os.getenv('CURRENT_JOBS_PATH')
# Email credentials for 
ALERT_BOT_EMAIL = os.getenv('email address')
ALERT_BOT_PASS = os.getenv('email password')
ALERT_BOT_DOMAIN = os.getenv('smtp.DOMAIN.COM')


def initiate_board_state(current_jobs_file: str, job_list: list):
    '''
    Creates a current_jobs.txt with job list based on what is currently available on career board
    Will be used as comparison for changes in postings during subsequent runs
    '''

    print('First time script has checked this job board: initiating job crawler...')
    with open(current_jobs_file, 'w') as current_jobs:
        current_jobs.write('\n'.join(job_list))
    
    # Dramatic effect :)
    time.sleep(3)
    print('See ya soon!')
    sys.exit(0)


def check_job_boards(to_addresses: list, job_board: str, headers: dict, board_attribute: str, listing_attribute: str):
    '''
    Uses one job board URL to send email alert of change to postings
    :param to_addresses: List of emails to be notified of change
    :param job_boards: URL to job board
    :param headers: user-agent for webscraping purposes
    '''

    # Request HTML and create soup object
    page = requests.get(job_board, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find ID for job listings and input below
    all_results = soup.find(id=board_attribute)

    #Read through parsed HTML to find class name for job title
    job_elements = all_results.find_all('td', class_=listing_attribute)
        
    #Finds all job titles and iterates through them, adding to a job list
    jobs = all_results.find_all('a', target='_blank')
    job_list = [job.text for job in jobs]

    # Determines if this is the first run to initiate comparison
    current_jobs_file = os.path.join(CURRENT_JOBS_PATH, job_board+'current_jobs.txt')
    if not os.path.isfile(current_jobs_file):
        initiate_board_state(current_jobs_file,job_list)

    # Creates list of jobs from previous time code was run
    with open(current_jobs_file, 'r+') as prev_jobs:
        previous_job_list = [job.strip('\n') for job in prev_jobs.readlines()]
        job_change = previous_job_list != job_list

        # Removes any job listings that have been filled or taken down from job board
        oldjobs = prev_jobs.readlines()
        prev_jobs.truncate(0)
        prev_jobs.seek(0)
        [prev_jobs.write(job) for job in oldjobs if job.strip('\n') in job_list]

    # Appends new jobs found to .txt for next execution
    new_jobs_added_list = [job for job in job_list if job not in previous_job_list]
    new_jobs_added = '\n'.join(new_jobs_added_list)
    with open(current_jobs_file, 'a') as current_jobs:
        current_jobs.write(new_jobs_added)

    # Sends email with new job listings
    email_body = f'Subject: {len(new_jobs_added)} job listing(s) have been added!\n\nJobs added:\n{new_jobs_added}'
    # Fixes bug with non-ascii characters
    email_body = email_body.encode('ascii', 'replace')

    # Sends email if there has been a change in jobs
    if job_change == True:
        conn = smtplib.SMTP(ALERT_BOT_DOMAIN, 587) 
        conn.ehlo()
        conn.starttls()
        conn.login(ALERT_BOT_EMAIL, ALERT_BOT_PASS) 
        conn.sendmail(ALERT_BOT_EMAIL, to_addresses, email_body)
        conn.quit()

    # # OPTIONAL email if no change was found in job postings
    # else:
    #     conn = smtplib.SMTP(email_domain, 587)
    #     conn.ehlo()
    #     conn.starttls()
    #     conn.login(alert_email_address, alert_email_pass) 
    #     conn.sendmail(alert_email_address, to_addresses, 'Subject: No jobs have been added')
    #     conn.quit()


def main():

    parser = argparse.ArgumentParser(description='Web Scraper to monitor and alert ' \
        'user of changes in a company\'s job postings. Run as CRON for best results.')

    parser.add_argument("-e", "--emails", help='Comma-separated list of emails to notify', required=True)

    parser.add_argument("-u", "--url", help='Comma-separated list of URLs for job boards to monitor', required=True)

    parser.add_argument("-a", "--agent", help='You user-agent. Can be found at whatsmyuseragent.org', required=True)

    parser.add_argument("-b", "--board_id", help='HTML ID of the job board attribute. Find this by inspecting site\'s HTML', required=True)

    parser.add_argument("-j", "--job_id", help='HTML ID a job listing attribute. Find this by inspecting site\'s HTML', required=True)

    args = parser.parse_args()
    to_addresses = args.emails.split(',')
    job_boards = args.url.split(',')
    headers = {'User-Agent': str(args.agent)}
    board_attribute = args.board_id
    listing_attribute = args.job_id

    for board in job_boards:
        check_job_boards(to_addresses, board, headers, board_attribute, listing_attribute)


if __name__ == '__main__':
    main()
