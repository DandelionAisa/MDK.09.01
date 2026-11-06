from flask import Blueprint,request,render_template,redirect,url_for,flash,session,g
from werkzeug.security import generate_password_hash,check_password_hash
from .db import get_db
from .validators import registration_errors
from .security import require_csrf
import sqlite3,time

auth=Blueprint('auth',__name__)
ATTEMPTS={}
@auth.route('/register',methods=['GET','POST'])
def register():
    errors={};data={}
    if request.method=='POST':
        require_csrf();data=request.form;errors=registration_errors(data)
        if not errors:
            db=get_db()
            try:
                db.execute('INSERT INTO users(login,full_name,password_hash,email,phone) VALUES (?,?,?,?,?)',(data['login'].strip(),data['full_name'].strip(),generate_password_hash(data['password']),data['email'].strip().lower(),data['phone'].strip()))
                db.commit();flash('Регистрация прошла успешно. Теперь войдите.','success');return redirect(url_for('auth.login'))
            except sqlite3.IntegrityError:errors['login']='Такой логин уже занят'
    return render_template('register.html',errors=errors,data=data),422 if errors else 200
@auth.route('/login',methods=['GET','POST'])
def login():
    error=None
    if request.method=='POST':
        require_csrf();login=request.form.get('login','').strip().lower();password=request.form.get('password','')
        now=time.monotonic();recent=[t for t in ATTEMPTS.get(login,[]) if now-t<600]
        if len(recent)>=5:error='Слишком много попыток входа. Повторите через 10 минут.'
        else:
            user=get_db().execute('SELECT * FROM users WHERE login=?',(login,)).fetchone()
            if user and check_password_hash(user['password_hash'],password):
                ATTEMPTS.pop(login,None);session.clear();session['user_id']=user['id'];return redirect(url_for('admin.index' if user['role']=='admin' else 'main.requests_list'))
            recent.append(now);ATTEMPTS[login]=recent;error='Неверный логин или пароль'
    return render_template('login.html',error=error),401 if error else 200
@auth.post('/logout')
def logout():
    require_csrf();session.clear();return redirect(url_for('main.index'))
