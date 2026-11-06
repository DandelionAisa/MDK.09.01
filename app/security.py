from functools import wraps
from flask import session,g,redirect,url_for,abort,request
import secrets,hmac

def csrf_token():
    if '_csrf' not in session:session['_csrf']=secrets.token_urlsafe(32)
    return session['_csrf']
def require_csrf():
    expected=session.get('_csrf','');received=request.form.get('csrf_token','')
    if not expected or not received or not hmac.compare_digest(expected,received):abort(400,'Неверный токен формы')
def login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if g.user is None:return redirect(url_for('auth.login'))
        return func(*args,**kwargs)
    return wrapper
def admin_required(func):
    @wraps(func)
    @login_required
    def wrapper(*args,**kwargs):
        if g.user['role']!='admin':abort(403,'Доступ только для администратора')
        return func(*args,**kwargs)
    return wrapper
