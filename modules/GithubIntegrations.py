from classes.Shinobu import Shinobu, StopPropagationException
import discord
import re
from urllib.request import urlopen, Request
import json
import time

def form_request(url):
    r = Request(url)
    r.add_header("Authorization", "token {}".format(config["token"]))
    return r

def get_json_at(url):
    site = urlopen(form_request(url))
    return json.loads(site.read().decode("utf-8"))

def repo_is_valid(reponame):
    baseurl = "https://api.github.com/repos/"
    try:
        urlopen(form_request(baseurl + reponame))
        return True
    except:
        return False

def gen_pie_chart(data):
    fig = {
        'data': [{'labels': ['Residential', 'Non-Residential', 'Utility'],
                  'values': [19, 26, 55],
                  'type': 'pie'}],
        'layout': {'title': 'Forcasted 2014 U.S. PV Installations by Market Segment'}
    }
    plot.iplot(fig)

def get_contributions(reponame, duration):
    baseurl = "https://api.github.com/repos/"
    statsurl = "/stats/contributors"
    stats = {"contributors": [],
             "commits": 0,
             "changes": 0,
             "days":duration}
    fullurl = baseurl + reponame + statsurl
    week_ago = int(time.time()) - (duration * 60 * 60 * 24)
    print(week_ago)
    contributions = get_json_at(fullurl)
    for user in contributions:
        username = user['author']['login']
        user_stats = {
            "login":username,
            "additions":0,
            "deletions":0,
            "commits":0
        }
        for week in user['weeks']:
            if week['w'] > week_ago:
                user_stats['additions'] += week['a']
                user_stats['deletions'] += week['d']
                stats['changes'] += week['a'] + week['d']
                user_stats['commits'] += week['c']
                stats["commits"] += week['c']
        stats['contributors'].append(user_stats)
    return stats

def sort_by_contributions(user):
    print("user:", user)
    return user['additions'] + user['deletions']

def format_stats(stats):
    first = "In the last {} days, there were __{}__ commits and __{}__ total changes\n".format(stats['days'],stats["commits"], stats["changes"])
    per_user = "**{}** pushed __{}__ additions and __{}__ deletions. [{}%]\n"
    user_list = []
    for user in sorted(stats['contributors'], key=sort_by_contributions, reverse=True):
        first+= per_user.format(user['login'], user["additions"], user["deletions"], round(100*(user['additions'] + user['deletions'])/stats['changes']))
    return first

def register_commands(ShinobuCommand):
    @ShinobuCommand("Registers a repo with this module", ['all'])
    async def register_repository(message: discord.Message, arguments: str):
        repo_name = arguments
        if repo_name not in config['managed_repos']:
            if repo_is_valid(repo_name):
                config["managed_repos"][repo_name] = {"owner":message.author.id}
                shinobu.config[__name__] = config
                shinobu.write_config()
                await shinobu.send_message(message.channel, "Successfully registered {0}".format(repo_name))
            else:
                await shinobu.send_message(message.channel, "That repo was not valid")
        else:
            await shinobu.send_message(message.channel, "Repository with name {0} has already been registered by <@{1}>".format(repo_name, config["managed_repos"][repo_name]["owner"]))

    @ShinobuCommand("Gets stats for the provided repo\n.stats repo_name num_days", ['all'])
    async def stats(message: discord.Message, arguments: str):
        att_repo = arguments.rsplit()[0]
        try:
            duration = int(arguments.rsplit()[1])
        except:
            duration = 7
        if len(att_repo) > 1:
            for repo in config['managed_repos']:
                if re.search(att_repo, repo.lower()) is not None:
                    await shinobu.send_typing(message.channel)
                    stats = get_contributions(repo, duration)
                    await shinobu.send_message(message.channel, format_stats(stats))
                    return
        await shinobu.send_message(message.channel, "Unknown repo: {}".format(att_repo))

    @ShinobuCommand("Removes a repository from this modules", ['all'])
    async def remove_repository(message: discord.Message, arguments: str):
        global config
        att_repo = arguments
        for repo in config['managed_repos']:
            if re.search(att_repo, repo.lower()) is not None:
                if config['managed_repos'][repo]["owner"] == message.author.id:
                    await shinobu.send_message(message.channel, "Do you mean {}".format(repo))
                    answer = await shinobu.wait_for_message(channel=message.channel, author=message.author, timeout=10)
                    if answer is not None and "no" not in answer.content:
                        await shinobu.send_message(message.channel, "{0} has been removed from list.".format(repo))
                        del config["managed_repos"][repo]
                        shinobu.config[__name__] = config
                        shinobu.write_config()
                        return
                    else:
                        await shinobu.send_message(message.channel, "Ok :^)")

async def accept_message(message:discord.Message):
    pass

def accept_shinobu_instance(instance):
    global shinobu, config
    shinobu = instance
    try:
        config = shinobu.config[__name__]
    except:
        shinobu.config[__name__] = {"managed_repos":{}}
        shinobu.write_config()


version = "1.0.0"
shinobu = None # type: Shinobu
config = {}

