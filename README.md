# GPCSSI-2024-Tool-Web-Crawler
Web Crawler which can Scrape Government SItes, It tells how many errors are reported in the program and the describes the error

In order to make this tool function 
-First ensure the scrapy module is installed on the system
-After the module is installed, open the file and in the terminal of python type python gov_scraper.py gov --start_url  <site you want to scrape>

Once the scraping is done, 2 CSV files wil be created which are error_log.csv and stats_output.csv

Stats_output.csv will point out which error was found in the site and how many times it was found
error_log.csv will tell what caused the error while scraping the site

