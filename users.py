from fasthtml.common import *
from dataclasses import dataclass
from hmac import compare_digest

# User-related database setup
def setup_users_db(db):
    users = db.t.users
    if users not in db.t:
        users.create(dict(name=str, pwd=str), pk='name')
    return users.dataclass()

def create_login_redirect():
    return RedirectResponse('/login', status_code=303)

def setup_auth_middleware(login_redirect):
    def before(req, sess):
        auth = req.scope['auth'] = sess.get('auth', None)
        if not auth:
            return login_redirect
        return None

    return Beforeware(before, skip=[
        r'/favicon\.ico',
        r'/static/.*',
        r'.*\.css',
        '/login'
    ])

# Function to initialize all user-related components
def init_user_module(db):
    User = setup_users_db(db)
    middleware = setup_auth_middleware(create_login_redirect())
    return middleware
