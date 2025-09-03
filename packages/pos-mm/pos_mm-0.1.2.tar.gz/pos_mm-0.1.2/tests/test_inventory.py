import pytest
from mm_pos.db import (
    init_db,
    MenuItemDB,
    MenuItemInventoryDB,
    OrderDB,
    OrderItemDB,
)
from mm_pos.inventory import InventoryManager


def test_inventory_deduction(tmp_path):
    db_path = tmp_path / "inv_test.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()
    inv = InventoryManager(session)

    patties = inv.add_stock("Burger Patty", 10)

    burger = MenuItemDB(name="Burger", price=9.99)
    session.add(burger)
    session.commit()

    link = MenuItemInventoryDB(
        menu_item_id=burger.id, inventory_id=patties.id, amount_used=1
    )
    session.add(link)
    session.commit()

    order = OrderDB(table_number=1)
    session.add(order)
    session.commit()

    oi = OrderItemDB(order_id=order.id, menu_item_id=burger.id, qty=2)
    session.add(oi)
    session.commit()

    inv.deduct_for_order(order.items)

    assert inv.get_stock("Burger Patty") == 8


def test_insufficient_stock_raises(tmp_path):
    db_path = tmp_path / "inv_fail.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()
    inv = InventoryManager(session)

    patties = inv.add_stock("Burger Patty", 1)

    burger = MenuItemDB(name="Burger", price=9.99)
    session.add(burger)
    session.commit()

    link = MenuItemInventoryDB(
        menu_item_id=burger.id, inventory_id=patties.id, amount_used=2
    )
    session.add(link)
    session.commit()

    order = OrderDB(table_number=1)
    session.add(order)
    session.commit()

    oi = OrderItemDB(order_id=order.id, menu_item_id=burger.id, qty=1)
    session.add(oi)
    session.commit()

    with pytest.raises(ValueError):
        inv.deduct_for_order(order.items)


def test_insufficient_stock_no_error_if_enforce_false(tmp_path):
    db_path = tmp_path / "inv_flexible.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()
    inv = InventoryManager(session)

    patties = inv.add_stock("Burger Patty", 1)

    burger = MenuItemDB(name="Burger", price=9.99)
    session.add(burger)
    session.commit()

    link = MenuItemInventoryDB(
        menu_item_id=burger.id, inventory_id=patties.id, amount_used=2
    )
    session.add(link)
    session.commit()

    order = OrderDB(table_number=1)
    session.add(order)
    session.commit()

    oi = OrderItemDB(order_id=order.id, menu_item_id=burger.id, qty=1)
    session.add(oi)
    session.commit()

    # With enforce=False, should NOT raise
    inv.deduct_for_order(order.items, enforce=False)

    # Stock should now be negative
    assert inv.get_stock("Burger Patty") == -1


def test_global_enforce_true_raises(tmp_path):
    db_path = tmp_path / "inv_enforce.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()
    inv = InventoryManager(session, enforce=True)  # strict mode

    patties = inv.add_stock("Burger Patty", 1)

    burger = MenuItemDB(name="Burger", price=9.99)
    session.add(burger)
    session.commit()

    link = MenuItemInventoryDB(
        menu_item_id=burger.id, inventory_id=patties.id, amount_used=2
    )
    session.add(link)
    session.commit()

    order = OrderDB(table_number=1)
    session.add(order)
    session.commit()

    oi = OrderItemDB(order_id=order.id, menu_item_id=burger.id, qty=1)
    session.add(oi)
    session.commit()

    with pytest.raises(ValueError):
        inv.deduct_for_order(order.items)


def test_global_enforce_false_allows_negative_stock(tmp_path):
    db_path = tmp_path / "inv_flex.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()
    inv = InventoryManager(session, enforce=False)  # flexible mode

    patties = inv.add_stock("Burger Patty", 1)

    burger = MenuItemDB(name="Burger", price=9.99)
    session.add(burger)
    session.commit()

    link = MenuItemInventoryDB(
        menu_item_id=burger.id, inventory_id=patties.id, amount_used=2
    )
    session.add(link)
    session.commit()

    order = OrderDB(table_number=1)
    session.add(order)
    session.commit()

    oi = OrderItemDB(order_id=order.id, menu_item_id=burger.id, qty=1)
    session.add(oi)
    session.commit()

    # No error in flexible mode
    inv.deduct_for_order(order.items)
    assert inv.get_stock("Burger Patty") == -1
