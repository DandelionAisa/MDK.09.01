from flask import Flask, g, request, session, render_template
from pathlib import Path
import os, secrets
from .db import init_db, get_db

def create_app(test_config=None):
    app=Flask(__name__,instance_relative_config=True)
    Path(app.instance_path).mkdir(exist_ok=True,parents=True)
    keyfile=Path(app.instance_path)/'secret.key'
    if not keyfile.exists(): keyfile.write_bytes(secrets.token_bytes(32))
    app.config.update(SECRET_KEY=keyfile.read_bytes(),DATABASE=str(Path(app.instance_path)/'portal.sqlite3'),SESSION_COOKIE_HTTPONLY=True,SESSION_COOKIE_SAMESITE='Lax',MAX_CONTENT_LENGTH=32768)
    if test_config: app.config.update(test_config)
    with app.app_context(): init_db()
    from .auth import auth
    from .main import main
    from .admin import admin
    app.register_blueprint(auth);app.register_blueprint(main);app.register_blueprint(admin)
    from .security import csrf_token
    app.jinja_env.globals["csrf_token"]=csrf_token
    @app.before_request
    def load_user():
        g.user=None
        if session.get('user_id'):
            g.user=get_db().execute('SELECT * FROM users WHERE id=?',(session['user_id'],)).fetchone()
    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options']='nosniff'
        response.headers['X-Frame-Options']='DENY'
        response.headers['Referrer-Policy']='same-origin'
        response.headers['Content-Security-Policy']="default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; form-action 'self'; base-uri 'self'"
        if request.endpoint not in ('static',): response.headers['Cache-Control']='no-store'
        return response
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(400)
    def err(e):return render_template('error.html',code=e.code,message=e.description),e.code
    @app.teardown_appcontext
    def close_db(e=None):
        con=g.pop('db',None)
        if con is not None:con.close()
    return app
