from mm_pos.db import init_db, UserDB, OrderDB, PaymentDB, MenuItemDB, OrderItemDB


def test_user_with_multiple_orders_and_payments(tmp_path):
    db_path = tmp_path / "user_test.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()

    # Create a user (waiter)
    alice = UserDB(name="Alice", role="waiter")
    alice.set_pin("1234")  # ✅ hash the pin before saving
    session.add(alice)
    session.commit()

    # Create menu item
    burger = MenuItemDB(name="Burger", price=10.00, category="Food")
    session.add(burger)
    session.commit()

    # First order by Alice
    order1 = OrderDB(table_number=1, user=alice)
    session.add(order1)
    session.commit()

    session.add(OrderItemDB(order_id=order1.id, menu_item_id=burger.id, qty=2))
    session.commit()

    payment1 = PaymentDB(order=order1, method="cash", amount_given=30.0, user=alice)
    session.add(payment1)
    session.commit()

    # Second order by Alice
    order2 = OrderDB(table_number=2, user=alice)
    session.add(order2)
    session.commit()

    session.add(OrderItemDB(order_id=order2.id, menu_item_id=burger.id, qty=1))
    session.commit()

    payment2 = PaymentDB(order=order2, method="card", user=alice)
    session.add(payment2)
    session.commit()

    # Assertions
    saved_user = session.query(UserDB).first()
    assert saved_user.name == "Alice"
    assert len(saved_user.orders) == 2
    assert len(saved_user.payments) == 2

    # Check roles and linkage
    assert saved_user.orders[0].user == saved_user
    assert saved_user.payments[0].user == saved_user


def test_user_role_permissions(tmp_path):
    db_path = tmp_path / "roles_test.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()

    waiter = UserDB(name="Wally", role="waiter")
    waiter.set_pin("1111")  # ✅ must set pin
    cashier = UserDB(name="Cathy", role="cashier")
    cashier.set_pin("2222")
    admin = UserDB(name="Alice", role="admin")
    admin.set_pin("3333")

    session.add_all([waiter, cashier, admin])
    session.commit()

    # Waiter
    assert waiter.can_take_orders() is True
    assert waiter.can_process_payments() is False
    assert waiter.can_view_reports() is False

    # Cashier
    assert cashier.can_take_orders() is True
    assert cashier.can_process_payments() is True
    assert cashier.can_view_reports() is False

    # Admin
    assert admin.is_admin() is True
    assert admin.can_take_orders() is True
    assert admin.can_process_payments() is True
    assert admin.can_view_reports() is True
