from mm_pos.menu import MenuItem
from mm_pos.order import Order
from mm_pos.receipt import Receipt
from mm_pos.payment import Payment


def test_receipt_contains_items_and_total():
    order = Order(table_number=3)
    burger = MenuItem("Burger", 8.99, "Food")
    cola = MenuItem("Cola", 1.99, "Drink")

    order.add_item(burger, qty=2)
    order.add_item(cola, qty=1)

    receipt = Receipt(order).generate()

    # Check important details are in the receipt
    assert "Table: 3" in receipt
    assert "2x Burger - $17.98" in receipt
    assert "1x Cola - $1.99" in receipt
    assert "Total: $19.97" in receipt
    assert "Thank you for dining with us!" in receipt


def test_receipt_includes_payment_info():
    order = Order(table_number=2)
    burger = MenuItem("Burger", 10.00)
    order.add_item(burger, qty=1)

    payment = Payment(order, method="cash", amount_given=20.00)
    receipt = Receipt(order, payment=payment).generate()

    assert "Total: $10.00" in receipt
    assert "Paid Cash - Change Due: $10.00" in receipt
