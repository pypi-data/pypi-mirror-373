# mm_pos/menu.py


class MenuItem:
    def __init__(self, name: str, price: float, category: str = "General"):
        self.name = name
        self.price = price
        self.category = category

    def __repr__(self):
        return f"{self.name} (${self.price:.2f})"


class Menu:
    def __init__(self):
        self.items = []

    def add_item(self, item: MenuItem):
        self.items.append(item)

    def list_items(self):
        return self.items
