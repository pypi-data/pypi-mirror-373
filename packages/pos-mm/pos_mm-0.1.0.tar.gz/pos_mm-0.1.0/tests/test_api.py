import pytest
from fastapi.testclient import TestClient
from mm_pos.api import app, session
from mm_pos.db import Base, get_engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db(tmp_path):
    """Recreate a fresh DB for every test run."""
    db_path = tmp_path / "test_api.db"
    engine = get_engine(f"sqlite:///{db_path}")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session.bind = engine
    yield


def register_and_login(name: str, role: str, pin: str):
    """Helper: register user + login to get auth token."""
    r = client.post("/register/", data={"name": name, "role": role, "pin": pin})
    assert r.status_code == 200

    r = client.post("/login/", data={"name": name, "pin": pin})
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# --- Auth Tests ---


def test_register_and_login():
    headers = register_and_login("Alice", "admin", "1234")
    assert "Authorization" in headers


# --- Menu Tests ---


def test_menu_requires_admin():
    # Waiter should NOT be able to add menu
    waiter_headers = register_and_login("Wally", "waiter", "1111")
    r = client.post(
        "/menu/", params={"name": "Burger", "price": 9.99}, headers=waiter_headers
    )
    assert r.status_code == 403

    # Admin can add
    admin_headers = register_and_login("Alice", "admin", "1234")
    r = client.post(
        "/menu/", params={"name": "Burger", "price": 9.99}, headers=admin_headers
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Burger"

    # Menu list should include Burger
    r = client.get("/menu/", headers=admin_headers)
    assert any(i["name"] == "Burger" for i in r.json())


# --- Orders Tests ---


def test_create_order_and_add_item():
    admin_headers = register_and_login("Alice", "admin", "1234")
    client.post("/menu/", params={"name": "Cola", "price": 2.5}, headers=admin_headers)

    # Cashier can create order
    cashier_headers = register_and_login("Cathy", "cashier", "2222")
    r = client.post("/orders/", params={"table_number": 5}, headers=cashier_headers)
    assert r.status_code == 200
    order_id = r.json()["id"]

    # Add item to order
    r = client.post(
        f"/orders/{order_id}/items/",
        params={"menu_item_id": 1, "qty": 2},
        headers=cashier_headers,
    )
    assert r.status_code == 200
    assert r.json()["qty"] == 2


# --- Payments Tests ---


def test_payment_requires_cashier_or_admin():
    admin_headers = register_and_login("Alice", "admin", "1234")
    client.post("/menu/", params={"name": "Soup", "price": 5.0}, headers=admin_headers)
    r = client.post("/orders/", params={"table_number": 1}, headers=admin_headers)
    order_id = r.json()["id"]

    waiter_headers = register_and_login("Wally", "waiter", "1111")
    r = client.post(
        "/payments/",
        params={"order_id": order_id, "method": "cash"},
        headers=waiter_headers,
    )
    assert r.status_code == 403  # waiter not allowed

    cashier_headers = register_and_login("Cathy", "cashier", "2222")
    r = client.post(
        "/payments/",
        params={"order_id": order_id, "method": "cash"},
        headers=cashier_headers,
    )
    assert r.status_code == 200


# --- Reports Tests ---


def test_reports_only_admin():
    admin_headers = register_and_login("Alice", "admin", "1234")
    r = client.get("/reports/daily/", headers=admin_headers)
    assert r.status_code == 200

    cashier_headers = register_and_login("Cathy", "cashier", "2222")
    r = client.get("/reports/daily/", headers=cashier_headers)
    assert r.status_code == 403


# --- Tables Tests ---


def test_open_and_close_table():
    admin_headers = register_and_login("Alice", "admin", "1234")

    # Open
    r = client.post("/tables/open/", params={"number": 10}, headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "open"

    # Close
    r = client.post("/tables/close/", params={"number": 10}, headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["status"] == "closed"
