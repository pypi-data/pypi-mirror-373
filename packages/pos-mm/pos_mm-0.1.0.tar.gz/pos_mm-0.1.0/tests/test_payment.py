import pytest
from mm_pos.menu import MenuItem
from mm_pos.order import Order
from mm_pos.payment import Payment


def make_order():
    order = Order(table_number=1)
    order.add_item(MenuItem("Burger", 10.00))
    order.add_item(MenuItem("Cola", 2.00))
    return order


def test_cash_payment_with_change():
    order = make_order()
    payment = Payment(order, method="cash", amount_given=20.00)
    assert payment.change_due() == pytest.approx(8.00)
    assert "Change Due: $8.00" in payment.summary()


def test_cash_payment_insufficient_amount():
    order = make_order()
    with pytest.raises(ValueError):
        Payment(order, method="cash", amount_given=5.00)


def test_card_payment_has_no_change():
    order = make_order()
    payment = Payment(order, method="card")
    assert payment.change_due() == 0.0
    assert "Paid Card" in payment.summary()


def test_mobile_payment_summary():
    order = make_order()
    payment = Payment(order, method="mobile")
    assert "Paid Mobile" in payment.summary()
