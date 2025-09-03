# mm_pos/payment.py

from mm_pos.order import Order


class Payment:
    def __init__(self, order: Order, method: str, amount_given: float = None):
        self.order = order
        self.method = method.lower()
        self.amount_given = amount_given

        if self.method == "cash" and (
            amount_given is None or amount_given < order.total()
        ):
            raise ValueError("Insufficient cash provided for this order.")

    def change_due(self) -> float:
        if self.method != "cash":
            return 0.0
        return round(self.amount_given - self.order.total(), 2)

    def summary(self) -> str:
        if self.method == "cash":
            return f"Paid {self.method.title()} - Change Due: ${self.change_due():.2f}"
        return f"Paid {self.method.title()}"
