import json
import random
import urllib.request
HOST = 'localhost'
PORT = 8069
DB = 'odoo'
USER = 'karla.vanessa@outlook.es'
PASS = 'admin'
ROOT = 'http://%s:%d/xmlrpc/' % (HOST,PORT)

def json_rpc(url, method, params):
    data = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": random.randint(0, 1000000000),
    }
    req = urllib.request.Request(url=url, data=json.dumps(data).encode("utf-8"), headers={
        "Content-Type":"application/json",
    })
    reply = json.load(urllib.request.urlopen(req)) 
    if reply.get("error"):
        raise Exception(reply["error"])
    return reply["result"]

def call(url, service, method, *args):
    return json_rpc(url, "call", {"service": service, "method": method, "args": args})

# log in the given database
url = "http://%s:%s/jsonrpc" % (HOST, PORT)
uid = call(url, "common", "login", DB, USER, PASS)
print(uid)


# create a new note
args = {
    'name' : 'Web Service2',
    'course_id' : 8,
}
note_id = call(url, "object", "execute", DB, uid, PASS, 'openacademy.session', 'create', args)
