"""Script entry point."""
from src import Scraper
from config import URLS


Scraper().scrape(URLS)
