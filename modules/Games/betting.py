from Shinobu.utility import ConfigManager

class Bet:
    def __init__(self, game, bet, user):
        self.game = game
        self.bet = bet
        self.user = user
        self._has_begun = False
        self._start_bet()

    def conclude_bet(self, won, odds):
        if won:
            win_amt = self.calculate_win_amount(self.bet, odds) + self.bet
            self.add_balance(win_amt)
            return win_amt
        else:
            return self.bet

    def _start_bet(self):
        global user_records
        self._has_begun = True
        if not self.user_exists():
            config["accounts"].append(create_user(self.user.id))
        if not get_user_balance(self.user.id)[0] > self.bet:
            raise Exception("User does not have enough balance for that bet")
        else:
            self.add_balance(-self.bet)


    def user_exists(self):
        for record in config["accounts"]:
            if record['id'] == self.user.id:
                return True
        return False



    def add_balance(self, balance_amnt):
        for record in config["accounts"]:
            if record['id'] == self.user.id:
                record['balance'] += balance_amnt

    def calculate_win_amount(self, bet, odds):
        return odds * bet



config = ConfigManager("resources/accounts.json")
config.assure("accounts", [])
config.assure("store_items", [])



def create_user(user_id):
    record = {
        "mention": "<@{}>".format(user_id),
        "id": user_id,
        "balance": 10,
        "holds": 0
    }
    return record

def credit_user(user, amnt):
    for record in config["accounts"]:
        if record['id'] == user.id:
            record['balance'] += amnt
            config.save()

bet_example = {
    "game":["flip", "roll"],
    "amount":100
}

game_return_example = {
    "game":["flip","roll","etc"],
    "odds":0.5,
    "win":True
}



def get_user_balance(user_id):
    global user_records
    for record in config["accounts"]:
        if record['id'] == user_id:
            return record['balance'], False
    config["accounts"].append(create_user(user_id))
    return 10, True

def get_all_accounts():
    return config['accounts']



