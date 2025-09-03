from mm_pos.menu import Menu, MenuItem


def test_add_item_to_menu():
    menu = Menu()
    burger = MenuItem("Burger", 8.99, "Food")
    menu.add_item(burger)
    assert burger in menu.items


def test_list_items_returns_all():
    menu = Menu()
    menu.add_item(MenuItem("Cola", 1.99, "Drink"))
    menu.add_item(MenuItem("Fries", 3.49, "Food"))
    items = menu.list_items()
    assert len(items) == 2
    assert all(isinstance(item, MenuItem) for item in items)


def test_menu_item_repr():
    item = MenuItem("Burger", 8.99, "Food")
    assert "Burger ($8.99)" in repr(item)
