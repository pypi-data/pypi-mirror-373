from datetime import date
from mm_pos.db import init_db, MenuItemDB, OrderDB, OrderItemDB, PaymentDB
from mm_pos.reports import Reports


def test_reports_generate_basic_stats(tmp_path):
    db_path = tmp_path / "reports_test.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()

    # Add menu items
    burger = MenuItemDB(name="Burger", price=10.0)
    cola = MenuItemDB(name="Cola", price=2.0)
    session.add_all([burger, cola])
    session.commit()

    # Create order with 2 burgers + 1 cola
    order1 = OrderDB(table_number=1)
    session.add(order1)
    session.commit()

    session.add(OrderItemDB(order_id=order1.id, menu_item_id=burger.id, qty=2))
    session.add(OrderItemDB(order_id=order1.id, menu_item_id=cola.id, qty=1))
    session.commit()

    # Add payment
    payment = PaymentDB(order_id=order1.id, method="cash", amount_given=25.0)
    session.add(payment)
    session.commit()

    reports = Reports(session)

    # Daily sales should equal 2*10 + 1*2 = 22
    assert reports.daily_sales_total(date.today()) == 22.0

    # Top selling item should be Burger (2 qty)
    top_items = reports.top_selling_items(limit=1)
    assert top_items[0][0] == "Burger"
    assert top_items[0][1] == 2

    # Payment breakdown should show 1 cash payment
    breakdown = reports.payment_breakdown(date.today())
    assert breakdown.get("cash") == 1


def test_reports_csv_exports(tmp_path):
    db_path = tmp_path / "reports_csv.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()

    # Setup menu and order
    burger = MenuItemDB(name="Burger", price=10.0)
    session.add(burger)
    session.commit()

    order = OrderDB(table_number=1)
    session.add(order)
    session.commit()

    session.add(OrderItemDB(order_id=order.id, menu_item_id=burger.id, qty=3))
    session.commit()

    session.add(PaymentDB(order_id=order.id, method="card"))
    session.commit()

    reports = Reports(session)

    # Export top items
    items_csv = tmp_path / "top_items.csv"
    reports.export_top_items_csv(str(items_csv))
    assert items_csv.exists()

    with open(items_csv) as f:
        content = f.read()
        assert "Burger" in content
        assert "3" in content

    # Export payment breakdown
    payments_csv = tmp_path / "payments.csv"
    reports.export_payment_breakdown_csv(str(payments_csv), date.today())
    assert payments_csv.exists()

    with open(payments_csv) as f:
        content = f.read()
        assert "card" in content
        assert "1" in content
