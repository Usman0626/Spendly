from werkzeug.security import generate_password_hash


def _create_user(isolated_db, name="Rahul Sharma", email="rahul.sharma@example.com", password="password123"):
    conn = isolated_db.get_db()
    conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, generate_password_hash(password)),
    )
    conn.commit()
    user_id = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()["id"]
    conn.close()
    return user_id


def test_get_login_still_renders_form(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b'name="email"' in response.data


def test_post_login_valid_credentials_sets_session_and_redirects(client, isolated_db):
    user_id = _create_user(isolated_db, name="Rahul Sharma", email="rahul.sharma@example.com", password="password123")

    response = client.post(
        "/login",
        data={"email": "rahul.sharma@example.com", "password": "password123"},
    )

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with client.session_transaction() as sess:
        assert sess["user_id"] == user_id
        assert sess["user_name"] == "Rahul Sharma"


def test_post_login_shows_welcome_flash_message(client, isolated_db):
    _create_user(isolated_db, name="Sneha Nair", email="sneha.nair@example.com", password="password123")

    response = client.post(
        "/login",
        data={"email": "sneha.nair@example.com", "password": "password123"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome back, Sneha Nair." in response.data


def test_post_login_wrong_password_shows_error(client, isolated_db):
    _create_user(isolated_db, name="Priya Iyer", email="priya.iyer@example.com", password="password123")

    response = client.post(
        "/login",
        data={"email": "priya.iyer@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 200
    assert b"auth-error" in response.data

    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_post_login_unknown_email_shows_error(client, isolated_db):
    response = client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    assert b"Invalid email or password." in response.data


def test_post_login_wrong_password_and_unknown_email_show_same_message(client, isolated_db):
    _create_user(isolated_db, name="Amit Gupta", email="amit.gupta@example.com", password="password123")

    wrong_password_response = client.post(
        "/login",
        data={"email": "amit.gupta@example.com", "password": "wrongpassword"},
    )
    unknown_email_response = client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "password123"},
    )

    assert b"Invalid email or password." in wrong_password_response.data
    assert b"Invalid email or password." in unknown_email_response.data


def test_post_login_email_repopulated_on_failure(client, isolated_db):
    _create_user(isolated_db, name="Neha Rao", email="neha.rao@example.com", password="password123")

    response = client.post(
        "/login",
        data={"email": "neha.rao@example.com", "password": "wrongpassword"},
    )

    assert response.status_code == 200
    assert b'value="neha.rao@example.com"' in response.data


def test_post_login_password_never_repopulated(client, isolated_db):
    _create_user(isolated_db, name="Kavya Menon", email="kavya.menon@example.com", password="password123")

    response = client.post(
        "/login",
        data={"email": "kavya.menon@example.com", "password": "distinctivewrongpass999"},
    )

    assert response.status_code == 200
    assert b"distinctivewrongpass999" not in response.data


def test_logout_clears_session_and_redirects(client, isolated_db):
    user_id = _create_user(isolated_db, name="Vikram Singh", email="vikram.singh@example.com", password="password123")

    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = "Vikram Singh"

    response = client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with client.session_transaction() as sess:
        assert "user_id" not in sess
        assert "user_name" not in sess


def test_logout_when_not_logged_in_is_harmless(client):
    response = client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_navbar_shows_user_name_when_logged_in(client, isolated_db):
    user_id = _create_user(isolated_db, name="Foo Bar", email="foo.bar@example.com", password="password123")

    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["user_name"] = "Foo Bar"

    response = client.get("/")

    assert response.status_code == 200
    assert b"Foo Bar" in response.data
    assert b"Logout" in response.data
    assert b"Sign in" not in response.data


def test_navbar_shows_sign_in_when_logged_out(client):
    response = client.get("/")

    assert response.status_code == 200
    assert b"Sign in" in response.data
    assert b"Get started" in response.data
    assert b"Logout" not in response.data
