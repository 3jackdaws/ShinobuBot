import json

class ConfigManager:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = {}
        try:
            self.config = json.load(open(config_file, "r+"))
        except:
            self.config = {}
            self.save()

    def __setitem__(self, key, value):
        self.config[key] = value
        self.save()

    def __getitem__(self, item):
        return self.config[item]

    def key(self, name, value=None):
        if value is None:
            return self.config[name]
        else:
            self.config[name] = value
            self.save()

    def save(self):
        c_file = open(self.config_file, "w+")
        json.dump(self.config, c_file, indent=2)

    def assure(self, key, if_not_exists_value):
        if key not in self.config:
            self.config[key] = if_not_exists_value
            self.save()
