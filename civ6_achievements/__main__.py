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

    @app.route('/achievements/<steam_id>')
    @cross_origin()
    def user(steam_id):
        api = API_BASE + 'ISteamUserStats/GetPlayerAchievements/v0001'
        user_resp = requests.get(api, params=params() | {'steamid': steam_id})
        data = loads(user_resp.text).get('playerstats').get('achievements')
        data = [entry | SCHEMA_MAP[entry['apiname']] for entry in data]
        return dumps(data)

    return app

def schema_map():
    api = API_BASE + 'ISteamUserStats/GetSchemaForGame/v0002'
    schema_resp = requests.get(api, params=params())
    schema = loads(schema_resp.text).get('game').get('availableGameStats').get('achievements')
    return {entry['name']: omit(entry, 'name') for entry in schema}

def params():
    return {
        'key': STEAM_API_KEY,
        'appid': APP_ID
    }

API_BASE = 'http://api.steampowered.com/'
APP_ID = '289070'
STEAM_API_KEY = getenv('STEAM_API_KEY')
SCHEMA_MAP = schema_map()
