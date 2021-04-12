from datetime import datetime
from functools import reduce
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

        print(reduce(merge, [Metadata(url).get_json_dl() for url in urls]))

    def merge(source, destination):
        """
        run me with nosetests --with-doctest file.py

        >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '0' } } }
        >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '4' } } }
        >>> merge(a, b) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '4' } } }
        True
        """
        for key, value in source.items():
            if isinstance(value, dict):
                # get node or create one
                node = destination.setdefault(key, {})
                merge(value, node)

            elif isinstance(value, list):
                pass

            elif are_values_overwritable(destination, key, value):
                destination[key] = value

            else:
                destination[key] = [value, destination[key]]
                pass

        return destination

    def are_values_overwritable(self, destination, key, value):
        return destination.setdefault(key, value) == value

    def merge(source, destination):
        source = self.normalize(source)
        destination = self.normalize(destination)

        for key in source:
            if key in destination:
                destination[key] = self.merge_keys(
                    source[key], destination[key]
                )
            else:
                destination[key] = source[key]
        return destination

    def merge_keys(self, source, destination):

        # there tecnically cant be a dict and something else...?

        if self.are_both_dicts(source, destination):
            return merge(source, destination)

        elif self.are_both_lists(source, destination):
            return list(
                set(source + destination)
            )  # recorrer lista mergeando los diccionarios que tiene adentro

        elif self.is_one_a_list(source, destination):
            return self.append_to_list(
                *self.identify_list_and_value(source, destination)
            )  # TODO

        elif source != destination:
            return [source, destination]

        else:  # source == destination
            return source

    def append_to_list(self, list_of_values, single_value):
        # TODO
        pass

    def identify_list_and_value(self, a_value, another_value):
        if isinstance(a_value, list):
            return a_value, another_value
        return another_value, a_value

    def _are_same_type(self, first_value, second_value, type):
        return isinstance(first_value, type) and isinstance(second_value, type)

    def are_both_dicts(self, first_value, second_value):
        return self._are_same_type(first_value, second_value, dict)

    def are_both_lists(self, first_value, second_value):
        return self._are_same_type(first_value, second_value, list)

    def is_one_a_list(self, first_value, second_value):
        return isinstance(first_value, list) ^ isinstance(second_value, list)

    def normalize(self, dictionary):
        problematic_keys = [("actor", "actors")]

        for standard_key, key in problematic_keys:
            if key in dictionary:
                dictionary[standard_key] = dictionary.pop(key)

        return dictionary

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
            +datetime.today().strftime("%Y-%m-%d-%H_%M_%S") + ".json",
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
