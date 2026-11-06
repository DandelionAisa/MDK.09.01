import pytest
from app import create_app
@pytest.fixture
def app(tmp_path):
    from app.auth import ATTEMPTS
    ATTEMPTS.clear()
    application=create_app({'TESTING':True,'DATABASE':str(tmp_path/'test.sqlite3'),'SECRET_KEY':'test-secret'})
    yield application
@pytest.fixture
def client(app):return app.test_client()
