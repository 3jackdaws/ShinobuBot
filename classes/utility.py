import json

class ConfigManager:
    def __init__(self, config_file, base={}):
        self.config_file = config_file
        try:
            self.config = json.load(open(config_file, "r+"))
        except:
            self.config = base
            self.save()


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
    def __init__(self, parent, key, value=[]):
        self.key = key
        self.value = value

        self.parent = parent

    def __getitem__(self, item):
        return CMValue(parent=self, key=item,value=self.value[item])

    def __setitem__(self, key, value):
        self.value[key] = value
        self.save()

    def __contains__(self, item):
        if item in self.value:
            return True
        return False

    def __iter__(self):
        return self.value.__iter__()


    def save(self):
        self.parent[self.key] = self.value

    def append(self, item):
        if isinstance(self.value, list):
            self.value.append(item)
        elif len(self.value) == 0:
            self.value = []
            self.value.append(item)
        else:
            raise TypeError(self.key + " is a dictionary and cannot be appened to")
        self.save()






