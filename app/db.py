from flask import current_app,g
from pathlib import Path
import sqlite3
from datetime import date,timedelta
from werkzeug.security import generate_password_hash

def get_db():
    if 'db' not in g:
        con=sqlite3.connect(current_app.config['DATABASE']);con.row_factory=sqlite3.Row
        con.execute('PRAGMA foreign_keys=ON');g.db=con
    return g.db

def init_db():
    db=get_db()
    sql=(Path(__file__).parent.parent/'schema.sql').read_text(encoding='utf8')
    db.executescript(sql)
    for i,label in ((1,'новая'),(2,'назначено'),(3,'завершено')):
        db.execute('INSERT OR IGNORE INTO statuses(id,name) VALUES (?,?)',(i,label))
    if not db.execute('SELECT 1 FROM events LIMIT 1').fetchone():
        today=date.today()
        rows=[('Конференция «Цифровая школа»',today+timedelta(days=14),'Москва, ул. Тверская, 12','Технологии образования и цифровые инструменты','Образование'),('Форум «Умный город»',today+timedelta(days=21),'Москва, Экспоцентр','Цифровые сервисы и развитие городов','Технологии'),('Семинар по кибербезопасности',today+timedelta(days=28),'Санкт-Петербург, Невский пр., 18','Безопасность веб-приложений и данных','Безопасность'),('Конференция «Веб-разработка»',today+timedelta(days=35),'Казань, ИТ-парк','Python, Flask и современные веб-интерфейсы','Разработка'),('Конференция «Данные и ИИ»',today-timedelta(days=30),'Москва, Технопарк','Данные, аналитика и машинное обучение','Искусственный интеллект')]
        db.executemany('INSERT INTO events(title,event_date,place,description,category) VALUES (?,?,?,?,?)',[(a,b.isoformat(),c,d,e) for a,b,c,d,e in rows])
    db.commit()

def create_admin(app,login,password):
    if len(password)<8:raise ValueError('Пароль должен быть не короче 8 символов')
    with app.app_context():
        db=get_db()
        if db.execute('SELECT 1 FROM users WHERE login=?',(login,)).fetchone():raise ValueError('Логин занят')
        db.execute('INSERT INTO users(login,full_name,password_hash,email,phone,role) VALUES (?,?,?,?,?,?)',(login,'Администратор',generate_password_hash(password),'admin@example.test','+79990000000','admin'))
        db.commit()
