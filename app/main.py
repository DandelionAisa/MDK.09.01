from flask import Blueprint,render_template,request,g,redirect,url_for,flash,abort
from datetime import date
from .db import get_db
from .security import login_required,require_csrf
from .validators import ROOMS,PAYMENTS,ascii_int
main=Blueprint('main',__name__)
@main.get('/')
def index():
    events=get_db().execute('SELECT * FROM events ORDER BY event_date').fetchall()
    return render_template('index.html',events=events,today=date.today().isoformat())
@main.get('/events/<int:event_id>')
def event_detail(event_id):
    event=get_db().execute('SELECT * FROM events WHERE id=?',(event_id,)).fetchone()
    if not event:abort(404)
    reviews=get_db().execute('SELECT reviews.*,users.full_name FROM reviews JOIN requests ON reviews.request_id=requests.id JOIN users ON users.id=requests.user_id WHERE requests.event_id=? ORDER BY reviews.id DESC',(event_id,)).fetchall()
    return render_template('event.html',event=event,reviews=reviews,today=date.today().isoformat())
@main.route('/requests/new',methods=['GET','POST'])
@login_required
def new_request():
    if g.user['role']!='participant':abort(403)
    db=get_db();events=db.execute('SELECT * FROM events WHERE event_date>=? ORDER BY event_date',(date.today().isoformat(),)).fetchall();error=None
    if request.method=='POST':
        require_csrf();event_id=ascii_int(request.form.get('event_id',''),1,1000000);seats=ascii_int(request.form.get('seats',''),1,50)
        event=db.execute('SELECT * FROM events WHERE id=? AND event_date>=?',(event_id,date.today().isoformat())).fetchone() if event_id else None
        room=request.form.get('room','');payment=request.form.get('payment','')
        if not event or not seats or room not in ROOMS or payment not in PAYMENTS:error='Проверьте мероприятие, помещение, оплату и число мест (1–50).'
        else:
            db.execute('INSERT INTO requests(user_id,event_id,room,payment,seats) VALUES (?,?,?,?,?)',(g.user['id'],event_id,room,payment,seats));db.commit();flash('Заявка создана','success');return redirect(url_for('main.requests_list'))
    return render_template('new_request.html',events=events,rooms=ROOMS,payments=PAYMENTS,error=error),422 if error else 200
@main.get('/requests')
@login_required
def requests_list():
    items=get_db().execute("""SELECT requests.*,events.title,events.event_date,statuses.name as status,
    (SELECT id FROM reviews WHERE reviews.request_id=requests.id) as review_id
    FROM requests JOIN events ON requests.event_id=events.id JOIN statuses ON requests.status_id=statuses.id
    WHERE requests.user_id=? ORDER BY requests.id DESC""",(g.user['id'],)).fetchall()
    return render_template('requests.html',items=items)
@main.route('/requests/<int:rid>/edit',methods=['GET','POST'])
@login_required
def edit_request(rid):
    db=get_db();r=db.execute('SELECT * FROM requests WHERE id=? AND user_id=?',(rid,g.user['id'])).fetchone()
    if not r:abort(404)
    if r['status_id']!=1:abort(403)
    error=None
    if request.method=='POST':
        require_csrf();room=request.form.get('room','');payment=request.form.get('payment','');seats=ascii_int(request.form.get('seats',''),1,50)
        if room not in ROOMS or payment not in PAYMENTS or not seats:error='Некорректные данные заявки'
        else:
            db.execute('UPDATE requests SET room=?,payment=?,seats=? WHERE id=?',(room,payment,seats,rid));db.commit();flash('Заявка изменена','success');return redirect(url_for('main.requests_list'))
    return render_template('edit_request.html',item=r,rooms=ROOMS,payments=PAYMENTS,error=error),422 if error else 200
@main.post('/requests/<int:rid>/cancel')
@login_required
def cancel_request(rid):
    require_csrf();db=get_db();r=db.execute('SELECT * FROM requests WHERE id=? AND user_id=?',(rid,g.user['id'])).fetchone()
    if not r:abort(404)
    if r['status_id']!=1:abort(403)
    db.execute('DELETE FROM requests WHERE id=?',(rid,));db.commit();flash('Заявка отменена','success');return redirect(url_for('main.requests_list'))
@main.route('/requests/<int:rid>/review',methods=['GET','POST'])
@login_required
def review(rid):
    db=get_db();r=db.execute('SELECT * FROM requests WHERE id=? AND user_id=?',(rid,g.user['id'])).fetchone()
    if not r:abort(404)
    if r['status_id']!=3:abort(403,'Отзыв только после завершения заявки')
    if db.execute('SELECT 1 FROM reviews WHERE request_id=?',(rid,)).fetchone():abort(403,'Отзыв уже отправлен')
    error=None
    if request.method=='POST':
        require_csrf();rating=ascii_int(request.form.get('rating',''),1,5);body=request.form.get('body','').strip()
        if not rating or len(body)<5 or len(body)>1000:error='Введите оценку от 1 до 5 и текст от 5 до 1000 символов'
        else:
            db.execute('INSERT INTO reviews(request_id,body,rating) VALUES (?,?,?)',(rid,body,rating));db.commit();flash('Отзыв опубликован','success');return redirect(url_for('main.requests_list'))
    return render_template('review.html',rid=rid,error=error),422 if error else 200
