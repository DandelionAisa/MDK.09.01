from flask import Blueprint,request,render_template,redirect,url_for,flash,abort
from .db import get_db
from .security import admin_required,require_csrf
admin=Blueprint('admin',__name__,url_prefix='/admin')
@admin.get('/')
@admin_required
def index():
    db=get_db();status=request.args.get('status','');event=request.args.get('event','');name=request.args.get('name','')
    sql="""SELECT requests.*,users.full_name,events.title,statuses.name as status FROM requests JOIN users ON users.id=requests.user_id JOIN events ON events.id=requests.event_id JOIN statuses ON statuses.id=requests.status_id WHERE 1=1""";params=[]
    if status in ('1','2','3'):sql+=' AND requests.status_id=?';params.append(int(status))
    if event.isascii() and event.isdecimal():sql+=' AND requests.event_id=?';params.append(int(event))
    if name:sql+=' AND users.full_name LIKE ?';params.append('%'+name[:60]+'%')
    sql+=' ORDER BY requests.id DESC'
    items=db.execute(sql,params).fetchall();events=db.execute('SELECT id,title FROM events ORDER BY event_date').fetchall()
    return render_template('admin.html',items=items,events=events,selected_status=status,selected_event=event,selected_name=name)
@admin.post('/requests/<int:rid>/advance')
@admin_required
def advance(rid):
    require_csrf();db=get_db();r=db.execute('SELECT status_id FROM requests WHERE id=?',(rid,)).fetchone()
    if not r:abort(404)
    if r['status_id']>=3:abort(403)
    db.execute('UPDATE requests SET status_id=status_id+1 WHERE id=?',(rid,));db.commit();flash('Статус обновлён','success');return redirect(url_for('admin.index'))
@admin.post('/requests/<int:rid>/delete')
@admin_required
def delete(rid):
    require_csrf();db=get_db();db.execute('DELETE FROM reviews WHERE request_id=?',(rid,));db.execute('DELETE FROM requests WHERE id=?',(rid,));db.commit();flash('Заявка удалена','success');return redirect(url_for('admin.index'))
