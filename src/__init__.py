from datetime import datetime
from json import dump
from os import getcwd
from os.path import join, isdir
from typing import List
from w3lib.html import get_base_url
import extruct
import requests


class Scraper(object):
    def scrape(self, urls: List[str]):
        """Parse structured data from a list of pages."""

        movie = {}

        for url in urls:
            print(Metadata(url).get_json_dl())
            print()

        # save_movie(movie)
        # return movie

    def save_movie(movie):
        with open(
            self.create_file_name(movie),
            "w",
            encoding="utf8",
        ) as file:
            dump(movie, file, ensure_ascii=False, indent=4, sort_keys=True)

    def create_file_name(self, movie):
        return join(
            getcwd(),
            "data",
            movie["name"],
            + datetime.today().strftime("%Y-%m-%d-%H_%M_%S") + ".json",
        )


class Metadata(object):
    def __init__(self, url):
        self.url = url

    def get_json_dl(self):
        """Fetch JSON-LD structured data."""

        json_dl = self.fetch_json_dl()

        if self.is_filled_list(json_dl):
            json_dl = json_dl[0]

        return json_dl

    def is_filled_list(self, json_dl):
        return bool(json_dl) and isinstance(json_dl, list)

    def fetch_json_dl(self):
        return extruct.extract(
            self.get_html(),
            base_url=get_base_url(self.url),
            syntaxes=["json-ld"],
            uniform=True,
        )["json-ld"]

    def get_html(self):
        """Get raw HTML from a URL."""
        return requests.get(self.url).content
