"""Main"""
from json import loads, dumps
from os import getenv

from flask import Flask
from flask_cors import cross_origin
from funcy import omit
import requests


def create_app():
    """Create app"""
    app = Flask(__name__)

    @app.route('/achievements', strict_slashes=False)
    @app.route('/achievements/<int:steam_id>')
    @cross_origin()
    def achievements(steam_id=None):
        player_data = {}
        if(is_valid_user(steam_id)):
            api = API_BASE + 'ISteamUserStats/GetPlayerAchievements/v0001'
            user_resp = requests.get(api, params=params(APP_ID) | {'steamid': steam_id})
            player_data = create_map('apiname', loads(user_resp.text).get('playerstats').get('achievements'))
        return dumps([{'apiname': k} | v | STATS_MAP[k] | player_data.get(k, {}) for k, v in SCHEMA_MAP.items()])

    return app

def schema_map(app_id):
    api = API_BASE + 'ISteamUserStats/GetSchemaForGame/v0002'
    schema_resp = requests.get(api, params=params(app_id))
    schema = loads(schema_resp.text).get('game').get('availableGameStats').get('achievements')
    return create_map('name', schema)

def stats_map(app_id):
    api = API_BASE + "ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002"
    stats_resp = requests.get(api, params={'gameid': app_id})
    stats = loads(stats_resp.text).get('achievementpercentages').get('achievements')
    return create_map('name', stats)

def params(app_id):
    return {
        'key': STEAM_API_KEY,
        'appid': app_id
    }

def is_valid_user(user):
    return user != None

def create_map(index, list):
    return {entry[index]: omit(entry, index) for entry in list}

API_BASE = 'http://api.steampowered.com/'
APP_ID = '289070'
STEAM_API_KEY = getenv('STEAM_API_KEY')
SCHEMA_MAP = schema_map(APP_ID)
STATS_MAP = stats_map(APP_ID)
