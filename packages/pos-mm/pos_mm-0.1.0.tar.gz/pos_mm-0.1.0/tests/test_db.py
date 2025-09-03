from mm_pos.db import init_db, MenuItemDB, OrderDB, OrderItemDB, PaymentDB, UserDB


def test_create_order_with_items_and_payment(tmp_path):
    db_path = tmp_path / "test.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()

    # Add menu item
    pizza = MenuItemDB(name="Pizza", price=12.5, category="Food")
    session.add(pizza)
    session.commit()

    # Create order
    order = OrderDB(table_number=1)
    session.add(order)
    session.commit()

    # Add order item
    session.add(OrderItemDB(order_id=order.id, menu_item_id=pizza.id, qty=2))
    session.commit()

    # Add payment
    payment = PaymentDB(order_id=order.id, method="cash", amount_given=30.00)
    session.add(payment)
    session.commit()

    # Assertions
    saved_order = session.query(OrderDB).first()
    assert saved_order.table_number == 1
    assert saved_order.items[0].qty == 2
    assert saved_order.payments[0].method == "cash"


def test_create_user_and_link_to_order_and_payment(tmp_path):
    db_path = tmp_path / "user_test.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()

    # Create user with secure pin
    alice = UserDB(name="Alice", role="waiter")
    alice.set_pin("1234")  # ✅ hash pin before saving
    session.add(alice)
    session.commit()

    # Assign order to user
    order = OrderDB(table_number=5, user=alice)
    session.add(order)
    session.commit()

    # Assign payment to same user
    payment = PaymentDB(order=order, method="cash", amount_given=50.0, user=alice)
    session.add(payment)
    session.commit()

    # Assertions
    saved_user = session.query(UserDB).first()
    assert saved_user.name == "Alice"
    assert saved_user.orders[0].table_number == 5
    assert saved_user.payments[0].method == "cash"
