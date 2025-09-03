import pytest
from mm_pos.menu import MenuItem
from mm_pos.order import Order


def test_add_item_and_total():
    order = Order(table_number=5)
    burger = MenuItem("Burger", 8.99, "Food")
    fries = MenuItem("Fries", 3.49, "Food")

    order.add_item(burger, qty=2)  # 2 burgers
    order.add_item(fries, qty=1)  # 1 fries

    assert order.total() == pytest.approx(8.99 * 2 + 3.49)


def test_order_summary_format():
    order = Order()
    cola = MenuItem("Cola", 1.99, "Drink")
    order.add_item(cola, qty=3)

    summary = order.summary()
    assert "3x Cola - $5.97" in summary
    assert "Total: $5.97" in summary


def test_empty_order_total_is_zero():
    order = Order()
    assert order.total() == 0
    assert "Total: $0.00" in order.summary()
