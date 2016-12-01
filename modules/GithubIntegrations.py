from classes.Shinobu import Shinobu, StopPropagationException
import discord
import re
from urllib.request import urlopen, Request
import json
import datetime

def form_request(url):
    r = Request(url)
    r.add_header("Authorization", "token {}".format(config["token"]))
    return r

def repo_is_valid(reponame):
    baseurl = "https://api.github.com/repos/"
    try:
        urlopen(form_request(baseurl + reponame))
        return True
    except:
        return False

def get_commits(url):
    url = url + "/commits?since={}"
    since = datetime.datetime.now()
    since = since - datetime.timedelta(7)
    since = since.isoformat()
    full = url.format(since)
    print(full)
    site = urlopen(form_request(full))
    commits = json.loads(site.read().decode("utf-8"))
    return commits

def get_commit_json(commit):
    url = commit['url']
    site = urlopen(form_request(url))
    return json.loads(site.read().decode("utf-8"))

def compute_stats(reponame):
    baseurl = "https://api.github.com/repos/"
    stats = {"contributions":{},
             "commits":0,
             "changes":0}
    for commit in get_commits(baseurl + reponame):
        stats["commits"] += 1
        cjson = get_commit_json(commit)
        user = cjson["author"]["login"]
        additions = cjson["stats"]["additions"]
        deletions = cjson["stats"]["deletions"]
        if user not in stats["contributions"]:
            stats["contributions"][user] = {"additions":0,"deletions":0}
        stats["contributions"][user]["additions"] += additions
        stats["contributions"][user]['deletions'] += deletions
        stats["changes"] += (additions + deletions)
    return stats

def format_stats(stats):
    first = "In the past week, there were {0} commits and {1} total changes\n".format(stats["commits"], stats["changes"])
    per_user = "**{}** pushed {} additions and {} deletions.\n"
    for user in stats['contributions']:
        first+= per_user.format(user, stats['contributions'][user]["additions"], stats['contributions'][user]["deletions"])
    return first

def register_commands(ShinobuCommand):
    @ShinobuCommand("Registers a repo with this module")
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

    @ShinobuCommand("Gets weekly stats for the provided repo")
    async def stats(message: discord.Message, arguments: str):
        att_repo = arguments
        if len(att_repo) > 1:
            for repo in config['managed_repos']:
                if re.search(att_repo, repo.lower()) is not None:
                    await shinobu.send_typing(message.channel)
                    stats = compute_stats(repo)
                    await shinobu.send_message(message.channel, format_stats(stats))
                    return
        await shinobu.send_message(message.channel, "Unknown repo: {}".format(att_repo))

    @ShinobuCommand("Removes a repository from this modules")
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

