import scrapy
import csv
from scrapy.crawler import CrawlerProcess
from urllib.parse import urlparse, urljoin
import argparse
import logging

class GovScraper(scrapy.Spider):
    name = 'gov_scraper'

    custom_settings = {
        'DEPTH_LIMIT': 3,
        'CLOSESPIDER_PAGECOUNT': 100,
        'DOWNLOAD_DELAY': 1,
        'LOG_LEVEL': 'DEBUG',
    }

    def __init__(self, start_url=None, *args, **kwargs):
        super(GovScraper, self).__init__(*args, **kwargs)
        if start_url:
            self.start_urls = [start_url]
            self.allowed_domains = [urlparse(start_url).netloc]
        else:
            raise ValueError("Please provide a start URL")

        self.visited_urls = set()
        self.errors = []

    def parse(self, response):
        self.log(f"Scraping: {response.url}")
        self.visited_urls.add(response.url)

        try:
            # Follow pagination or other links
            next_pages = response.css('a::attr(href)').getall()
            for next_page in next_pages:
                next_page = urljoin(response.url, next_page)
                if urlparse(next_page).netloc == self.allowed_domains[0]:
                    normalized_next_page = self.normalize_url(next_page)
                    if normalized_next_page not in self.visited_urls:
                        self.visited_urls.add(normalized_next_page)
                        self.log(f"Following link: {next_page}")
                        yield response.follow(next_page, self.parse)
        except Exception as e:
            self.log(f"Error occurred: {e}")
            self.errors.append({'URL': response.url, 'Error': str(e)})

    def normalize_url(self, url):
        parsed_url = urlparse(url)
        return parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

    def closed(self, reason):
        self.log(f"Spider closed: {reason}")

        # Collect and write stats to a new CSV file
        stats = self.crawler.stats.get_stats()
        with open('stats_output.csv', 'w', newline='', encoding='utf-8') as stats_file:
            stats_writer = csv.writer(stats_file)
            stats_writer.writerow(['Stat', 'Value'])
            for stat, value in stats.items():
                stats_writer.writerow([stat, value])
        self.log(f"Stats written to stats_output.csv")

        # Write errors to a separate CSV file
        if self.errors:
            with open('error_log.csv', 'w', newline='', encoding='utf-8') as error_file:
                error_writer = csv.DictWriter(error_file, fieldnames=['URL', 'Error'])
                error_writer.writeheader()
                for error in self.errors:
                    error_writer.writerow(error)
            self.log(f"Errors written to error_log.csv")

def main():
    parser = argparse.ArgumentParser(description="Choose to scrape a government site.")
    parser.add_argument('choice', choices=['gov'], help="Choose 'gov' to scrape a government site.")
    parser.add_argument('--start_url', type=str, help='The starting URL to scrape (required if choice is "gov")')

    args = parser.parse_args()

    if args.choice == 'gov':
        if not args.start_url:
            print("Please provide a start URL for scraping a government site.")
            return
        process = CrawlerProcess()
        process.crawl(GovScraper, start_url=args.start_url)
        process.start()

if __name__ == "__main__":
    main()
