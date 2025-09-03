# mm_pos/order.py

from mm_pos.menu import MenuItem


class Order:
    def __init__(self, table_number: int = None, takeout: bool = False):
        self.items = []
        self.table_number = table_number
        self.takeout = takeout

    def add_item(self, item: MenuItem, qty: int = 1):
        self.items.append((item, qty))

    def total(self):
        return sum(item.price * qty for item, qty in self.items)

    def summary(self):
        lines = [
            f"{qty}x {item.name} - ${item.price * qty:.2f}" for item, qty in self.items
        ]
        lines.append(f"Total: ${self.total():.2f}")
        return "\n".join(lines)
