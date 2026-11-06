import re
from app.db import get_db
from werkzeug.security import check_password_hash

def token(client,path):
    page=client.get(path)
    match=re.search(rb'name="csrf_token" value="([^"]+)"',page.data)
    assert match,page.data[:200]
    return match.group(1).decode()
def register(client,login='alla_test'):
    return client.post('/register',data={'csrf_token':token(client,'/register'),'login':login,'full_name':'Тестовый Пользователь','password':'Password2026','email':'alla@example.test','phone':'+79991234567'})
def login(client,login='alla_test',password='Password2026'):
    return client.post('/login',data={'csrf_token':token(client,'/login'),'login':login,'password':password})
def test_home(client):assert b'<!doctype html>' in client.get('/').data.lower()
def test_register_and_hash(client,app):
    assert register(client).status_code==302
    with app.app_context():
        u=get_db().execute('SELECT * FROM users WHERE login=?',('alla_test',)).fetchone()
        assert u and u['password_hash']!='Password2026' and check_password_hash(u['password_hash'],'Password2026')
def test_duplicate_login_case_insensitive(client):
    assert register(client).status_code==302
    assert register(client,'ALLA_TEST').status_code==422
def test_short_password_rejected(client):
    response=client.post('/register',data={'csrf_token':token(client,'/register'),'login':'user_abc','full_name':'Тестовый Пользователь','password':'1234567','email':'test@example.test','phone':'+79991234567'})
    assert response.status_code==422
def test_login_wrong_password(client):
    register(client)
    assert login(client,password='wrong').status_code==401
def test_unauthorized_admin(client):
    register(client);login(client)
    assert client.get('/admin/').status_code==403
def test_no_csrf_rejected(client):assert client.post('/register',data={'login':'abc'}).status_code==400
def test_request_and_lifecycle(client,app):
    register(client);login(client)
    with app.app_context():
        event=get_db().execute('SELECT id FROM events WHERE event_date>=date("now") ORDER BY id LIMIT 1').fetchone()
        eid=event['id']
    res=client.post('/requests/new',data={'csrf_token':token(client,'/requests/new'),'event_id':str(eid),'room':'Онлайн','payment':'Бесплатно','seats':'2'})
    assert res.status_code==302
    with app.app_context():
        db=get_db();rid=db.execute('SELECT id FROM requests').fetchone()['id']
        assert db.execute('SELECT status_id FROM requests WHERE id=?',(rid,)).fetchone()[0]==1
    assert client.get(f'/requests/{rid}/review').status_code==403
    with app.app_context():
        db=get_db();db.execute('UPDATE requests SET status_id=3 WHERE id=?',(rid,));db.commit()
    assert client.get(f'/requests/{rid}/review').status_code==200
    resp=client.post(f'/requests/{rid}/review',data={'csrf_token':token(client,f'/requests/{rid}/review'),'rating':'5','body':'Отличная конференция'})
    assert resp.status_code==302
    assert client.get(f'/requests/{rid}/review').status_code==403
def test_no_past_event(client,app):
    register(client);login(client)
    with app.app_context():eid=get_db().execute('SELECT id FROM events WHERE event_date<date("now") LIMIT 1').fetchone()['id']
    res=client.post('/requests/new',data={'csrf_token':token(client,'/requests/new'),'event_id':str(eid),'room':'Онлайн','payment':'Бесплатно','seats':'2'})
    assert res.status_code==422
def test_superscript_digit_never_500(client,app):
    register(client);login(client)
    with app.app_context():eid=get_db().execute('SELECT id FROM events WHERE event_date>=date("now") LIMIT 1').fetchone()['id']
    res=client.post('/requests/new',data={'csrf_token':token(client,'/requests/new'),'event_id':str(eid),'room':'Онлайн','payment':'Бесплатно','seats':'²'})
    assert res.status_code==422
