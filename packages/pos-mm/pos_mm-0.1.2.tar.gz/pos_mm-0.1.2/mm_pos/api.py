from fastapi import FastAPI, HTTPException, Depends, status, Form
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC

from mm_pos.db import (
    init_db,
    MenuItemDB,
    OrderDB,
    OrderItemDB,
    PaymentDB,
    UserDB,
)
from mm_pos.reports import Reports
from mm_pos.tables import TableManager

Session = init_db()
session = Session()

app = FastAPI(title="mm-pos API", version="0.1.0")

# ========================
# Authentication utilities
# ========================

SECRET_KEY = "super-secret-key"  # TODO: replace with env var in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a signed JWT token for authentication."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the logged-in user from a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = session.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ========================
# Auth endpoints
# ========================


@app.post("/register/")
def register_user(name: str = Form(...), role: str = Form(...), pin: str = Form(...)):
    """Register a new user (waiter, cashier, admin)."""
    user = UserDB(name=name, role=role)
    user.set_pin(pin)  # hash + store pin
    session.add(user)
    session.commit()
    return {"id": user.id, "name": user.name, "role": user.role}


@app.post("/login/")
def login(name: str = Form(...), pin: str = Form(...)):
    """Login with name + PIN, returns a JWT token."""
    user = session.query(UserDB).filter_by(name=name).first()
    if not user or not user.verify_pin(pin):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


# ========================
# Menu endpoints
# ========================


@app.post("/menu/")
def add_menu_item(
    name: str,
    price: float,
    category: str = "General",
    current_user: UserDB = Depends(get_current_user),
):
    if not current_user.is_admin():
        raise HTTPException(status_code=403, detail="Admins only")
    item = MenuItemDB(name=name, price=price, category=category)
    session.add(item)
    session.commit()
    return {
        "id": item.id,
        "name": item.name,
        "price": item.price,
        "category": item.category,
    }


@app.get("/menu/")
def list_menu_items(current_user: UserDB = Depends(get_current_user)):
    items = session.query(MenuItemDB).all()
    return [
        {"id": i.id, "name": i.name, "price": i.price, "category": i.category}
        for i in items
    ]


# ========================
# Orders endpoints
# ========================


@app.post("/orders/")
def create_order(
    table_number: int = None,
    takeout: bool = False,
    current_user: UserDB = Depends(get_current_user),
):
    if not current_user.can_take_orders():
        raise HTTPException(status_code=403, detail="Not authorized to create orders")
    order = OrderDB(table_number=table_number, takeout=takeout, user_id=current_user.id)
    session.add(order)
    session.commit()
    return {
        "id": order.id,
        "table_number": order.table_number,
        "takeout": order.takeout,
        "user_id": current_user.id,
    }


@app.post("/orders/{order_id}/items/")
def add_item_to_order(
    order_id: int,
    menu_item_id: int,
    qty: int = 1,
    current_user: UserDB = Depends(get_current_user),
):
    if not current_user.can_take_orders():
        raise HTTPException(status_code=403, detail="Not authorized to add items")

    order = session.get(OrderDB, order_id)

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    item = session.get(MenuItemDB, menu_item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")

    oi = OrderItemDB(order_id=order.id, menu_item_id=item.id, qty=qty)
    session.add(oi)
    session.commit()
    return {"order_id": order.id, "item": item.name, "qty": qty}


# ========================
# Payments endpoints
# ========================


@app.post("/payments/")
def add_payment(
    order_id: int,
    method: str,
    amount_given: float = None,
    current_user: UserDB = Depends(get_current_user),
):
    if not current_user.can_process_payments():
        raise HTTPException(
            status_code=403, detail="Not authorized to process payments"
        )

    order = session.get(OrderDB, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payment = PaymentDB(
        order_id=order_id,
        method=method,
        amount_given=amount_given,
        user_id=current_user.id,
    )
    session.add(payment)
    session.commit()
    return {
        "payment_id": payment.id,
        "order_id": order_id,
        "method": method,
        "amount_given": amount_given,
        "user_id": current_user.id,
    }


# ========================
# Reports endpoints
# ========================


@app.get("/reports/daily/")
def daily_sales(current_user: UserDB = Depends(get_current_user)):
    if not current_user.can_view_reports():
        raise HTTPException(status_code=403, detail="Admins only")
    reports = Reports(session)
    return {"total_sales": reports.daily_sales_total()}


@app.get("/reports/top-items/")
def top_items(limit: int = 5, current_user: UserDB = Depends(get_current_user)):
    if not current_user.can_view_reports():
        raise HTTPException(status_code=403, detail="Admins only")
    reports = Reports(session)
    return {"top_items": reports.top_selling_items(limit)}


@app.get("/reports/payments/")
def payment_breakdown(current_user: UserDB = Depends(get_current_user)):
    if not current_user.can_view_reports():
        raise HTTPException(status_code=403, detail="Admins only")
    reports = Reports(session)
    return {"payment_breakdown": reports.payment_breakdown()}


# ========================
# Tables endpoints
# ========================


@app.post("/tables/open/")
def open_table(number: int, current_user: UserDB = Depends(get_current_user)):
    if not current_user.can_take_orders():
        raise HTTPException(status_code=403, detail="Not authorized to open tables")
    manager = TableManager(session)
    t = manager.open_table(number)
    return {"id": t.id, "number": t.number, "status": t.status}


@app.post("/tables/close/")
def close_table(number: int, current_user: UserDB = Depends(get_current_user)):
    if not current_user.can_process_payments():
        raise HTTPException(status_code=403, detail="Not authorized to close tables")
    manager = TableManager(session)
    t = manager.close_table(number)
    return {"id": t.id, "number": t.number, "status": t.status}
