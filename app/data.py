import json
users = None
with open('db.json', 'r') as js_f:
    users = json.load(js_f)
