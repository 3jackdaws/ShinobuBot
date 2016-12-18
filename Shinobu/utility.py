import json
import os
import re

class ConfigManager:
    def __init__(self, config_file, base={}):
        self.config_file = config_file
        path_base = os.path.dirname(config_file)
        if not os.path.exists(path_base):
            print("Making {}",format(path_base))
            os.makedirs(path_base)
        try:
            self.config = json.load(open(config_file, "r+"))
        except:
            self.config = base
            self.save()

    def __len__(self):
        return self.config.__len__()

    def __setitem__(self, key, value):
        self.config[key] = value
        self.save()

    def __getitem__(self, item):
        return CMValue(self, item, self.config[item])

    def save(self):
        c_file = open(self.config_file, "w+")
        json.dump(self.config, c_file, indent=2)

    def assure(self, key, if_not_exists_value):
        if key not in self.config:
            self.config[key] = if_not_exists_value
            self.save()


class CMValue:
    def __init__(self, parent, key, value={}):
        self.key = key
        self.value = value

        self.parent = parent

    def __getitem__(self, item):
        return CMValue(parent=self, key=item,value=self.value[item])

    def __getattr__(self, item):
        attr = self.value.__getattribute__(item)
        def wrapper(*args):
            attr(*args)
            self.save()
        return wrapper

    def __int__(self):
        return int(self.value)

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __gt__(self, other):
        return self.value > other

    def __lt__(self, other):
        return self.value < other


    def __setitem__(self, key, value):
        self.value[key] = value
        self.save()

    def __eq__(self, other):
        return self.value == other

    def __contains__(self, item):
        if item in self.value:
            return True
        return False

    def __str__(self):
        return str(self.value)

    def __iter__(self):
        return self.value.__iter__()


    def __len__(self):
        return self.value.__len__()

    def __isub__(self, other):
        self.value -= other
        self.save()

    def __iadd__(self, other):
        self.value += other
        self.save()

    def save(self):
        self.parent[self.key] = self.value


class FuzzyMatch:
    def __init__(self, iterable):
        self.collection = iterable

    def find(self, query_string):
        results = []
        for item in self.collection:
            idx = item.find(query_string)
            if idx >= 0:
                results.append((idx, item))
        final = []
        for item in sorted(results):
            final.append(item[1])
        return final












