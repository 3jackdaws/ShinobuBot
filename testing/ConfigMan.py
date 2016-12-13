from Shinobu.utility import ConfigManager

config = ConfigManager("../resources/test.json")


config.assure("test", [])


config["test"].append("1")





