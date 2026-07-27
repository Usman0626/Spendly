from werkzeug.security import check_password_hash


def test_get_register_still_renders_form(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert b'name="email"' in response.data


def test_post_register_valid_creates_user_and_redirects(client, isolated_db):
    response = client.post(
        "/register",
        data={
            "name": "Rahul Sharma",
            "email": "rahul.sharma@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

    conn = isolated_db.get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ?", ("rahul.sharma@example.com",)).fetchone()
    conn.close()
    assert user is not None
    assert user["name"] == "Rahul Sharma"


def test_post_register_shows_success_message_on_login_page(client, isolated_db):
    response = client.post(
        "/register",
        data={
            "name": "Sneha Nair",
            "email": "sneha.nair@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Sneha Nair, you are registered." in response.data


def test_post_register_hashes_password(client, isolated_db):
    client.post(
        "/register",
        data={
            "name": "Priya Iyer",
            "email": "priya.iyer@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    conn = isolated_db.get_db()
    user = conn.execute("SELECT password_hash FROM users WHERE email = ?", ("priya.iyer@example.com",)).fetchone()
    conn.close()
    assert user["password_hash"] != "password123"
    assert check_password_hash(user["password_hash"], "password123")


def test_post_register_duplicate_email_shows_error_no_dupe_row(client, isolated_db):
    client.post(
        "/register",
        data={
            "name": "Amit Gupta",
            "email": "amit.gupta@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    response = client.post(
        "/register",
        data={
            "name": "Someone Else",
            "email": "amit.gupta@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    assert response.status_code == 200
    assert b"auth-error" in response.data

    conn = isolated_db.get_db()
    count = conn.execute(
        "SELECT COUNT(*) AS c FROM users WHERE email = ?", ("amit.gupta@example.com",)
    ).fetchone()["c"]
    conn.close()
    assert count == 1


def test_post_register_duplicate_email_is_case_sensitive(client, isolated_db):
    client.post(
        "/register",
        data={
            "name": "Foo Bar",
            "email": "Foo@x.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    response = client.post(
        "/register",
        data={
            "name": "Foo Bar Two",
            "email": "foo@x.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    assert response.status_code == 302

    conn = isolated_db.get_db()
    count = conn.execute(
        "SELECT COUNT(*) AS c FROM users WHERE email IN (?, ?)", ("Foo@x.com", "foo@x.com")
    ).fetchone()["c"]
    conn.close()
    assert count == 2


def test_post_register_short_password_shows_error(client, isolated_db):
    response = client.post(
        "/register",
        data={
            "name": "Neha Rao",
            "email": "neha.rao@example.com",
            "password": "short",
            "confirm_password": "short",
        },
    )

    assert response.status_code == 200
    assert b"auth-error" in response.data

    conn = isolated_db.get_db()
    count = conn.execute(
        "SELECT COUNT(*) AS c FROM users WHERE email = ?", ("neha.rao@example.com",)
    ).fetchone()["c"]
    conn.close()
    assert count == 0


def test_post_register_password_mismatch_shows_error(client, isolated_db):
    response = client.post(
        "/register",
        data={
            "name": "Kavya Menon",
            "email": "kavya.menon@example.com",
            "password": "password123",
            "confirm_password": "password456",
        },
    )

    assert response.status_code == 200
    assert b"Passwords do not match." in response.data

    conn = isolated_db.get_db()
    count = conn.execute(
        "SELECT COUNT(*) AS c FROM users WHERE email = ?", ("kavya.menon@example.com",)
    ).fetchone()["c"]
    conn.close()
    assert count == 0


def test_post_register_empty_name_shows_error(client, isolated_db):
    response = client.post(
        "/register",
        data={
            "name": "",
            "email": "noname@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    assert response.status_code == 200
    assert b"auth-error" in response.data

    conn = isolated_db.get_db()
    count = conn.execute(
        "SELECT COUNT(*) AS c FROM users WHERE email = ?", ("noname@example.com",)
    ).fetchone()["c"]
    conn.close()
    assert count == 0


def test_post_register_malformed_email_shows_error(client, isolated_db):
    response = client.post(
        "/register",
        data={
            "name": "Vikram Singh",
            "email": "notanemail",
            "password": "password123",
            "confirm_password": "password123",
        },
    )

    assert response.status_code == 200
    assert b"auth-error" in response.data

    conn = isolated_db.get_db()
    count = conn.execute(
        "SELECT COUNT(*) AS c FROM users WHERE name = ?", ("Vikram Singh",)
    ).fetchone()["c"]
    conn.close()
    assert count == 0
