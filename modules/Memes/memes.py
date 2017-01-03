import json
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import time
import datetime
import pytrends.request as trends
from random import randint
import Shinobu.database as db

db = None

def init_db(database):
    db = database

def get_object_at(url):
    return json.loads(urlopen(url).read().decode("utf-8"))

def get_matching_memes(meme, descriptor=None):
    base = "http://rkgk.api.searchify.com/v1/indexes/kym_production/instantlinks?{}&fetch=*"
    obj = get_object_at(base.format(urlencode({"query":meme})))
    return obj["results"]

def print_categories(obj:dict):
    for cat in obj:
        print(cat)

def is_meme(item):
    try:
        res = get_matching_memes(item)
        print(res[0]["category"])
        return res[0]["category"] in ["meme", "subculture", "event"]
    except:
        return False

def get_meme(item):
    res = get_matching_memes(item)
    if len(res) == 0:
        return "No results :("
    elif len(res) == 1:
        return "**{}** - *{}* - *{}*\n{}".format(res[0]['name'], res[0]['year'], res[0]["category"], res[0]["summary"])
    elif len(res) > 1:
        if res[0]["name"].lower() == item.lower():
            return "**{}** - *{}* - *{}*\n{}".format(res[0]['name'], res[0]['year'], res[0]["category"], res[0]["summary"])
        return "__Search returns multiple results:__\n{}".format("\n".join([x["name"] for x in res]))



def write_json(obj, filename):
    file = open(filename, "w+")
    json.dump(obj, file, indent=2)

def get_category(meme:dict):
    return meme["category"]

def get_value(meme_string):
    pass


def get_trend(query:list, numdays="7-d"):
    treq = trends.TrendReq("shinobu@isogen.net", "KKY-aQx-Za9-u4N", custom_useragent="Internet Explorer")
    print(query)
    payload = {'hl': 'en-US',
               "q":",".join(query),
               "geo":"US",
               "date":"today {}".format(numdays)
               }
    return treq.trend(payload, "json")


def hrdate(timestr):
    return datetime.datetime.fromtimestamp(
        int(timestr)
    ).strftime('%Y-%m-%d %H:%M:%S')

def print_table(google_meme_obj):
    colstr = " | ".join(["{0: <20}".format(x["label"]) for x in google_meme_obj["table"]["cols"]])
    print(colstr)
    for row in google_meme_obj["table"]["rows"]:
        rowstr = " | ".join(["{0: <20}".format(x["v"]) for x in row["c"]])
        print(rowstr)

def build_rows(obj):
    rows = obj["table"]["rows"]
    width = len(rows)

def average_rows(obj):
    avg = [{"name":x["label"],
           "avg":0} for x in obj["table"]["cols"]]
    rows = obj["table"]["rows"]
    cols = obj["table"]["cols"]
    num = len(rows)
    for row in rows:
        for i,place in enumerate(row["c"]):
            if i > 0:
                try:
                    avg[i]["avg"] += place['v']
                except:
                    print(place)
    for m in avg:
        m["avg"] /= num
    return avg

def get_popularity_diff(meme1, meme2, days="7-d"):
    obj = get_trend([meme1, meme2, "4chan"], days)
    avg = average_rows(obj)
    return avg[1]["avg"]/avg[2]["avg"] - 1


def get_weighted_trends(*trends, span="7-d"):
    obj = get_trend(["4chan", *trends], "30-d")
    return average_rows(obj)

def calc_volatility(*memes, span="30-d"):
    obj = get_trend(["4chan", *memes], span)
    dev = [{"name": x["label"],
            "last":-1,
            'max-dev':0,
            "avg-dev":0} for x in obj["table"]["cols"]]
    rows = obj["table"]["rows"]
    cols = obj["table"]["cols"]
    num = len(rows)
    for row in rows:
        for i, place in enumerate(row["c"]):
            if i > 0:
                try:
                    val = place['v']
                    deviation = 0
                    if dev[i]["last"] == -1:
                        dev[i]["last"] = val

                    else:
                        deviation = abs(dev[i]["last"] - val)
                        if dev[i]["max-dev"] < deviation:
                            dev[i]["max-dev"] = deviation
                        dev[i]["avg-dev"] += deviation
                        dev[i]["last"] = val
                except:
                    print(place)
    for m in dev:
        m["avg-dev"] /= num
    return {"memes":dev, "periods":num}




