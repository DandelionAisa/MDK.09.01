import re
LOGIN=re.compile(r'[A-Za-z0-9_]{3,20}\Z')
EMAIL=re.compile(r'[^\s@]+@[^\s@]+\.[A-Za-zА-Яа-я]{2,}\Z')
PHONE=re.compile(r'\+?7[0-9()\s-]{10,17}\Z')
ROOMS=('Большой зал','Малый зал','Онлайн')
PAYMENTS=('Карта','Перевод по счёту','Бесплатно')
def registration_errors(data):
    err={}
    login=data.get('login','').strip();name=data.get('full_name','').strip();pw=data.get('password','');mail=data.get('email','').strip();phone=data.get('phone','').strip()
    if not LOGIN.fullmatch(login):err['login']='Логин: 3–20 латинских букв, цифр или _'
    if len(name)<3 or len(name)>100:err['full_name']='ФИО: от 3 до 100 символов'
    if not 8<=len(pw)<=128:err['password']='Пароль: от 8 до 128 символов'
    if not EMAIL.fullmatch(mail):err['email']='Введите корректную почту'
    if not PHONE.fullmatch(phone) or len(re.sub(r'\D','',phone))!=11:err['phone']='Введите телефон в формате +7 999 123-45-67'
    return err
def ascii_int(value,low,high):
    if not re.fullmatch(r'[0-9]+',str(value)):return None
    number=int(value)
    return number if low<=number<=high else None
