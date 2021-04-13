from datetime import datetime
from pprint import pprint
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

        pprint(
            reduce(self.merge, [Metadata(url).get_json_dl() for url in urls])
        )

    # def are_values_overwritable(self, destination, key, value):
    #     return destination.setdefault(key, value) == value

    def merge(self, source, destination):
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
            return self.merge(source, destination)

        elif self.are_both_lists(source, destination):
            for element in destination:
                self.append_to_list(source, element)
            return source

        elif self.is_one_a_list(source, destination):
            return self.append_to_list(
                *self.identify_list_and_value(source, destination)
            )

        elif source != destination:
            return [source, destination]

        else:  # source == destination
            return source

    def append_to_list(self, list_of_elements, single_element):

        if single_element in list_of_elements:
            pass
        elif isinstance(single_element, dict):
            self.append_dict_to_list(list_of_elements, single_element)
        else:
            list_of_elements.append(single_element)

        return list_of_elements

    def append_dict_to_list(self, list_of_elements, single_element):
        try:
            same_dict = next(
                dictionary
                for dictionary in list_of_elements
                if self.are_names_equal(element, single_element)
            )

            same_element.update(single_element)

        except StopIteration:
            list_of_elements.append(single_element)

        finally:
            return list_of_elements

    def are_names_equal(element, another_element):
        return (
            "name" in element.keys()
            and "name" in another_element.keys()
            and element["name"] == another_element["name"]
        )

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

    def save_movie(self, movie):
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
        return requests.get(
            self.url,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Max-Age": "3600",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            },
        ).content
