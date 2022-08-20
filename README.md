# CareerCrawler
Scrapes multiple company job boards for new career listings and sends emails when new ones are added, along with list of new job titles available. Software should be run in a shell script with desired arguments as a CRON job.

GitHub link: https://github.com/jguiel/CareerWebScraper
## Code Usage
Code is open-source, Justin Guiel 2021

## Instructions
1. Create a .env file with the following:

    File path to where the script will write and read from a txt file: `CURRENT_JOBS_PATH`
    
    Email creds set up for the script to alert from: `ALERT_BOT_EMAIL`, `ALERT_BOT_PASS`, `ALERT_BOT_DOMAIN`
2. pip install the requirements file
3. Set up a shell script with the args of your choice.
4. Run the .sh as a CRON job 
