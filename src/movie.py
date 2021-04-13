from src.merger import Merger


class Movie(object):
    def __init__(self, json_dl):
        self.data = json_dl

    def merge(self, another_movie):
        self.normalize()
        another_movie.normalize()

        another_movie.update(self.data)

        return another_movie

    def update(self, another_data):
        merger = Merger(another_data, self.data)
        self.data = merger.merge()

    def normalize(self):
        self.data = self.standarize_keys()
        self.data = self.remove_null_values(self.data)
        return self.data

    def remove_null_values(self, value):
        if isinstance(value, list):
            return [
                self.remove_null_values(val)
                for val in value
                if self.is_valid_value(val)
            ]
        elif isinstance(value, dict):
            return {
                key: self.remove_null_values(val)
                for key, val in value.items()
                if self.is_valid_value(val)
            }
        else:
            return value

    def is_valid_value(self, value):
        return value is not None

    def standarize_keys(self):
        problematic_keys = [("actor", "actors")]

        for standard_key, key in problematic_keys:
            if key in self.data:
                self.data[standard_key] = self.data.pop(key)

        return self.data

    def remove_data(self, keys_to_remove):
        for key in keys_to_remove:
            if key in self.data.keys():
                del self.data[key]

        return self
