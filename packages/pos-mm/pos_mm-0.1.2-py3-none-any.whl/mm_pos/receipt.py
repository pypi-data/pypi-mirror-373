# mm_pos/receipt.py

from datetime import datetime
from mm_pos.order import Order
from mm_pos.payment import Payment


class Receipt:
    def __init__(self, order: Order, payment: Payment = None):
        self.order = order
        self.payment = payment
        self.timestamp = datetime.now()

    def generate(self) -> str:
        header = ["MM-POS Receipt", "-" * 20]

        if self.order.table_number:
            header.append(f"Table: {self.order.table_number}")
        elif self.order.takeout:
            header.append("Takeout Order")

        header.append(f"Date: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # Items
        body = [
            f"{qty}x {item.name} - ${item.price * qty:.2f}"
            for item, qty in self.order.items
        ]

        # Footer
        footer = [
            "-" * 20,
            f"Total: ${self.order.total():.2f}",
            "Thank you for dining with us!",
        ]

        # Add payment info if available
        if self.payment:
            footer.append(self.payment.summary())

        return "\n".join(header + body + footer)
