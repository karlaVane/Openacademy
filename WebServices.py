import functools
import xmlrpc.client
HOST = 'localhost'
PORT = 8069
DB = 'odoo'
USER = 'karla.vanessa@outlook.es'
PASS = 'admin'
ROOT = 'http://%s:%d/xmlrpc/' % (HOST,PORT)

# 1. Login
#common = xmlrpc.client.ServerProxy('{}common'.format(ROOT))
#id = common.authenticate(DB,USER,PASS,{})
#print(id)

uid = xmlrpc.client.ServerProxy(ROOT + 'common').login(DB,USER,PASS)
print ("Logged in as %s (uid:%d)" % (USER,uid))

call = functools.partial(
    xmlrpc.client.ServerProxy(ROOT + 'object').execute,
    DB, uid, PASS)

print(call)

# 2. Read the sessions
sessions = call('openacademy.session','search_read', [], ['name','seats'])
for session in sessions:
    print ("Session %s -> Seats: %s" % (session['name'], session['seats']))

# 3.create a new session
course_id = call('openacademy.course', 'search', [('name','ilike','Course 1')])[0]
#print(course_id)

session_id = call('openacademy.session', 'create', {
    'name' : 'Web Service',
    'course_id' : course_id,
    'duration':3,
    'seats':2,
})