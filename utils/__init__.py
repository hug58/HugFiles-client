import json

with open('config.json') as f:
    data = json.load(f)

URL_BASE = data['url']