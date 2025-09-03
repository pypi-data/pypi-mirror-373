# mm_pos/db.py
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Boolean,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timezone
from passlib.hash import bcrypt

Base = declarative_base()


class MenuItemDB(Base):
    __tablename__ = "menu_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String, default="General")

    inventory_links = relationship(
        "MenuItemInventoryDB", back_populates="menu_item", cascade="all, delete-orphan"
    )


class OrderDB(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_number = Column(Integer, nullable=True)
    takeout = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)
    table = relationship("TableDB", back_populates="orders")

    # FK to user
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("UserDB", back_populates="orders")

    items = relationship(
        "OrderItemDB", back_populates="order", cascade="all, delete-orphan"
    )
    payments = relationship(
        "PaymentDB", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItemDB(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    qty = Column(Integer, nullable=False, default=1)

    order = relationship("OrderDB", back_populates="items")
    menu_item = relationship("MenuItemDB")


class PaymentDB(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    method = Column(String, nullable=False)
    amount_given = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    order = relationship("OrderDB", back_populates="payments")
    user = relationship("UserDB", back_populates="payments")


class TableDB(Base):
    __tablename__ = "tables"
    id = Column(Integer, primary_key=True, autoincrement=True)
    number = Column(Integer, unique=True, nullable=False)
    status = Column(String, default="open")  # open, occupied, closed

    orders = relationship(
        "OrderDB", back_populates="table", cascade="all, delete-orphan"
    )


class InventoryDB(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)  # e.g. "Burger Patty"
    quantity = Column(
        Float, nullable=False, default=0.0
    )  # in units (e.g. pieces, liters)

    # relationship: which menu items depend on this stock
    menu_links = relationship(
        "MenuItemInventoryDB", back_populates="inventory", cascade="all, delete-orphan"
    )


class MenuItemInventoryDB(Base):
    """
    Link table between MenuItem and Inventory.
    Defines how much of each ingredient is used per menu item.
    """

    __tablename__ = "menu_item_inventory"
    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    amount_used = Column(Float, nullable=False)  # how much stock is consumed per item

    menu_item = relationship("MenuItemDB", back_populates="inventory_links")
    inventory = relationship("InventoryDB", back_populates="menu_links")


class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # waiter, cashier, admin
    pin_hash = Column(String, nullable=False)  # store hashed PIN instead of raw

    orders = relationship(
        "OrderDB", back_populates="user", cascade="all, delete-orphan"
    )
    payments = relationship(
        "PaymentDB", back_populates="user", cascade="all, delete-orphan"
    )

    # --- Auth utilities ---
    def set_pin(self, pin: str):
        self.pin_hash = bcrypt.hash(pin)

    def verify_pin(self, pin: str) -> bool:
        return bcrypt.verify(pin, self.pin_hash)

    # --- Role helpers ---
    def is_admin(self):
        return self.role.lower() == "admin"

    def can_take_orders(self):
        return self.role.lower() in ("waiter", "cashier", "admin")

    def can_process_payments(self):
        return self.role.lower() in ("cashier", "admin")

    def can_view_reports(self):
        return self.role.lower() == "admin"


# --- Setup Functions ---
def get_engine(db_url="sqlite:///mmpos.db"):
    return create_engine(db_url, echo=False)


def init_db(engine=None):
    if engine is None:
        engine = get_engine()
    elif isinstance(engine, str):
        engine = get_engine(engine)

    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
