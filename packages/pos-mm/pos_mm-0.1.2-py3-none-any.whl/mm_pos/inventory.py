from sqlalchemy.orm import Session
from mm_pos.db import InventoryDB


class InventoryManager:
    def __init__(self, session: Session, enforce: bool = True):
        """
        :param session: SQLAlchemy session
        :param enforce: whether to enforce strict stock checks (default=True)
        """
        self.session = session
        self.enforce = enforce

    def add_stock(self, name: str, qty: float):
        """Add or update stock quantity for an ingredient."""
        item = self.session.query(InventoryDB).filter_by(name=name).first()
        if not item:
            item = InventoryDB(name=name, quantity=qty)
            self.session.add(item)
        else:
            item.quantity += qty
        self.session.commit()
        return item

    def get_stock(self, name: str) -> float:
        """Return current stock quantity for an ingredient."""
        item = self.session.query(InventoryDB).filter_by(name=name).first()
        return item.quantity if item else 0.0

    def deduct_for_order(self, order_items, enforce: bool = None):
        """
        Deduct inventory for a list of OrderItemDB objects.
        Uses global enforcement unless override provided.
        """
        # Decide enforcement mode
        if enforce is None:
            enforce = self.enforce

        # First pass: check stock only if links exist
        for oi in order_items:
            if not oi.menu_item.inventory_links:
                continue  # skip items with no inventory tracking

            for link in oi.menu_item.inventory_links:
                required = link.amount_used * oi.qty
                if enforce and link.inventory.quantity < required:
                    raise ValueError(
                        f"Not enough stock for {link.inventory.name}. "
                        f"Required {required}, available {link.inventory.quantity}"
                    )

        # Second pass: deduct
        for oi in order_items:
            if not oi.menu_item.inventory_links:
                continue
            for link in oi.menu_item.inventory_links:
                required = link.amount_used * oi.qty
                link.inventory.quantity -= required
        self.session.commit()

    def low_stock_alerts(self, threshold: float = 5.0):
        """Return a list of items below the given threshold."""
        return [
            (inv.name, inv.quantity)
            for inv in self.session.query(InventoryDB).all()
            if inv.quantity <= threshold
        ]
