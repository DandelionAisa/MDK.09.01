import sys
from app import create_app
app = create_app()
if __name__ == '__main__':
    if len(sys.argv)>1 and sys.argv[1]=='create-admin':
        if len(sys.argv)!=4:
            raise SystemExit('Использование: python run.py create-admin ЛОГИН ПАРОЛЬ')
        from app.db import create_admin
        create_admin(app,sys.argv[2],sys.argv[3]);print('Администратор создан')
    else:
        app.run(host='127.0.0.1',port=5000,debug=False)
