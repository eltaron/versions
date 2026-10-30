import pytest
from app import create_app, db
from app.models.user import User
from app.models.system import System
from app.models.version import Version
from app.models.version_change import VersionChange


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def admin_user(app):
    with app.app_context():
        user = User(username='testadmin', email='admin@test.com', full_name='Test Admin', role='admin')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def regular_user(app):
    with app.app_context():
        user = User(username='testuser', email='user@test.com', full_name='Test User', role='user')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_system(app):
    with app.app_context():
        system = System(
            name='Test System', code='TST-SYS', system_type='Web Application',
            description='A test system', owner='Test Owner', department='IT',
            technology='Python', platform='Linux', status='Active'
        )
        db.session.add(system)
        db.session.commit()
        return system.id


def login(client, email='admin@test.com', password='testpass'):
    return client.post('/login', data={'email': email, 'password': password},
                       follow_redirects=True)


def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert 'نظام إدارة الإصدارات'.encode('utf-8') in response.data


def test_login_success(client, admin_user):
    response = login(client)
    assert response.status_code == 200
    assert 'لوحة التحكم'.encode('utf-8') in response.data


def test_login_failure(client, admin_user):
    response = client.post('/login', data={'email': 'admin@test.com', 'password': 'wrong'},
                           follow_redirects=True)
    assert 'البريد الإلكتروني أو كلمة المرور غير صحيحة'.encode('utf-8') in response.data


def test_logout(client, admin_user):
    login(client)
    response = client.get('/logout', follow_redirects=True)
    assert 'تم تسجيل الخروج'.encode('utf-8') in response.data


def test_unauthenticated_redirect(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_dashboard(client, admin_user):
    login(client)
    response = client.get('/')
    assert response.status_code == 200
    assert 'لوحة التحكم'.encode('utf-8') in response.data


def test_system_creation(client, admin_user):
    login(client)
    response = client.post('/systems/create', data={
        'name': 'New System',
        'code': 'NEW-SYS',
        'system_type': 'API / Service',
        'description': 'A new test API',
        'owner': 'Test Owner',
        'department': 'Engineering',
        'technology': 'Python, Flask',
        'platform': 'Linux',
        'status': 'Active',
    }, follow_redirects=True)
    assert response.status_code == 200
    with client.application.app_context():
        assert System.query.filter_by(code='NEW-SYS').first() is not None


def test_system_duplicate_code(client, admin_user, sample_system):
    login(client)
    response = client.post('/systems/create', data={
        'name': 'Duplicate System',
        'code': 'TST-SYS',
        'system_type': 'Web Application',
        'status': 'Active',
    }, follow_redirects=True)
    assert 'يوجد نظام بالفعل' in response.data.decode('utf-8')


def test_system_edit(client, admin_user, sample_system):
    login(client)
    response = client.post(f'/systems/{sample_system}/edit', data={
        'name': 'Updated System',
        'code': 'TST-SYS',
        'system_type': 'Web Application',
        'description': 'Updated description',
        'status': 'Active',
    }, follow_redirects=True)
    assert response.status_code == 200
    with client.application.app_context():
        system = System.query.get(sample_system)
        assert system.name == 'Updated System'


def test_system_details(client, admin_user, sample_system):
    login(client)
    response = client.get(f'/systems/{sample_system}')
    assert response.status_code == 200
    assert b'Test System' in response.data


def test_version_creation(client, admin_user, sample_system):
    login(client)
    response = client.post('/versions/create', data={
        'system_id': sample_system,
        'version_number': '1.0.0',
        'version_type': 'Major',
        'status': 'Draft',
        'description': 'First version',
        'release_date': '2026-08-15',
    }, follow_redirects=True)
    assert response.status_code == 200
    with client.application.app_context():
        v = Version.query.filter_by(system_id=sample_system, version_number='1.0.0').first()
        assert v is not None
        assert v.status == 'Draft'


def test_duplicate_version_prevention(client, admin_user, sample_system):
    login(client)
    client.post('/versions/create', data={
        'system_id': sample_system,
        'version_number': '1.0.0',
        'version_type': 'Major',
        'status': 'Draft',
    }, follow_redirects=True)

    response = client.post('/versions/create', data={
        'system_id': sample_system,
        'version_number': '1.0.0',
        'version_type': 'Major',
        'status': 'Draft',
    }, follow_redirects=True)
    assert 'موجود بالفعل' in response.data.decode('utf-8')


def test_version_release(client, admin_user, sample_system):
    login(client)
    client.post('/versions/create', data={
        'system_id': sample_system,
        'version_number': '1.0.0',
        'version_type': 'Major',
        'status': 'Draft',
        'description': 'First version',
    }, follow_redirects=True)

    with client.application.app_context():
        v = Version.query.filter_by(system_id=sample_system, version_number='1.0.0').first()
        version_id = v.id

    response = client.post(f'/versions/{version_id}/release', follow_redirects=True)
    assert response.status_code == 200

    with client.application.app_context():
        v = Version.query.get(version_id)
        assert v.status == 'Released'


def test_current_version_logic(client, admin_user, sample_system):
    login(client)

    client.post('/versions/create', data={
        'system_id': sample_system,
        'version_number': '1.0.0',
        'version_type': 'Major',
        'status': 'Released',
        'release_date': '2026-01-01',
    }, follow_redirects=True)

    client.post('/versions/create', data={
        'system_id': sample_system,
        'version_number': '2.0.0',
        'version_type': 'Major',
        'status': 'Released',
        'release_date': '2026-08-01',
    }, follow_redirects=True)

    with client.application.app_context():
        system = System.query.get(sample_system)
        current = system.current_version
        assert current is not None
        assert current.version_number == '2.0.0'

        versions = Version.query.filter_by(system_id=sample_system, status='Released').all()
        assert len(versions) == 2


def test_version_comparison(client, admin_user, sample_system):
    login(client)

    client.post('/versions/create', data={
        'system_id': sample_system,
        'version_number': '1.0.0',
        'version_type': 'Major',
        'status': 'Released',
        'description': 'Initial version',
    }, follow_redirects=True)

    client.post('/versions/create', data={
        'system_id': sample_system,
        'version_number': '2.0.0',
        'version_type': 'Major',
        'status': 'Released',
        'description': 'Major update',
    }, follow_redirects=True)

    with client.application.app_context():
        v1 = Version.query.filter_by(system_id=sample_system, version_number='1.0.0').first()
        v2 = Version.query.filter_by(system_id=sample_system, version_number='2.0.0').first()

        db.session.add(VersionChange(version_id=v1.id, change_type='New Feature', title='Feature A', description='Feature A desc'))
        db.session.add(VersionChange(version_id=v2.id, change_type='New Feature', title='Feature B', description='Feature B desc'))
        db.session.commit()

        v1_id = v1.id
        v2_id = v2.id

    response = client.post('/versions/compare', data={
        'system_id': sample_system,
        'version_a_id': v1_id,
        'version_b_id': v2_id,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'مقارنة الإصدارات'.encode('utf-8') in response.data


def test_system_archive(client, admin_user, sample_system):
    login(client)
    response = client.post(f'/systems/{sample_system}/archive', follow_redirects=True)
    assert response.status_code == 200

    with client.application.app_context():
        system = System.query.get(sample_system)
        assert system.status == 'Archived'


def test_system_search(client, admin_user, sample_system):
    login(client)
    response = client.get('/systems/?search=Test')
    assert response.status_code == 200
    assert b'Test System' in response.data


def test_system_filter(client, admin_user, sample_system):
    login(client)
    response = client.get('/systems/?type=Web+Application')
    assert response.status_code == 200


def test_reports_current_versions(client, admin_user, sample_system):
    login(client)
    response = client.get('/reports/current-versions')
    assert response.status_code == 200


def test_reports_version_history(client, admin_user, sample_system):
    login(client)
    response = client.post('/reports/version-history', data={
        'system_id': sample_system,
    })
    assert response.status_code == 200


def test_audit_log(client, admin_user):
    login(client)
    response = client.get('/audit/')
    assert response.status_code == 200


def test_users_page(client, admin_user):
    login(client)
    response = client.get('/users/')
    assert response.status_code == 200


def test_regular_user_cannot_manage_users(client, regular_user):
    login(client, 'user@test.com', 'testpass')
    response = client.get('/users/')
    assert response.status_code == 302


def test_regular_user_cannot_see_audit(client, regular_user):
    login(client, 'user@test.com', 'testpass')
    response = client.get('/audit/')
    assert response.status_code == 302


def test_version_with_changes(client, admin_user, sample_system):
    login(client)
    response = client.post('/versions/create', data={
        'system_id': sample_system,
        'version_number': '1.0.0',
        'version_type': 'Major',
        'status': 'Draft',
        'description': 'Version with changes',
        'change_type[]': ['New Feature', 'Bug Fix'],
        'change_title[]': ['Search Feature', 'Login Fix'],
        'change_description[]': ['Added search', 'Fixed login bug'],
    }, follow_redirects=True)
    assert response.status_code == 200

    with client.application.app_context():
        v = Version.query.filter_by(system_id=sample_system, version_number='1.0.0').first()
        changes = VersionChange.query.filter_by(version_id=v.id).all()
        assert len(changes) == 2


def test_version_archive(client, admin_user, sample_system):
    login(client)

    client.post('/versions/create', data={
        'system_id': sample_system,
        'version_number': '1.0.0',
        'version_type': 'Major',
        'status': 'Released',
        'release_date': '2026-01-01',
    }, follow_redirects=True)

    with client.application.app_context():
        v = Version.query.filter_by(system_id=sample_system, version_number='1.0.0').first()
        version_id = v.id

    client.post('/versions/create', data={
        'system_id': sample_system,
        'version_number': '2.0.0',
        'version_type': 'Major',
        'status': 'Released',
        'release_date': '2026-08-01',
    }, follow_redirects=True)

    response = client.post(f'/versions/{version_id}/archive', follow_redirects=True)
    assert response.status_code == 200

    with client.application.app_context():
        v = Version.query.get(version_id)
        assert v.status == 'Archived'
