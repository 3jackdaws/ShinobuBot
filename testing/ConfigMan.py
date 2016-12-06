from classes.utility import ConfigManager

config = ConfigManager("../resources/test.json")


config["test"] = None


config["test2"]["test3"] = 8
config["test_array"] = []
config["test_array"].append(5)
config["test_array"].append(6)
config["test_array"].append(7)
config["test_array"].append(8)
config["test_array"].append(5)



