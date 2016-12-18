def blacklist(*channels):
    def set_item(function):
        function.Blacklist = channels
        return function
    return set_item


def whitelist(*channels):
    def set_item(function):
        function.Whitelist = channels
        return function
    return set_item


def permissions(*roles):
    def set_item(function):
        function.Permissions = roles
        return function
    return set_item

def description(desc):
    def set_item(function):
        function.Description = desc
        return function
    return set_item


def usage(*exp):
    def set_item(function):
        function.Usage = exp
        return function
    return set_item
