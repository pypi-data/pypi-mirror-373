# mm_pos/reports.py

import csv
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from mm_pos.db import OrderDB, OrderItemDB, MenuItemDB, PaymentDB


class Reports:
    def __init__(self, session: Session):
        self.session = session

    def daily_sales_total(self, day: date = None) -> float:
        """Return total sales for a given day (default: today)."""
        if day is None:
            day = date.today()

        total = (
            self.session.query(func.sum(MenuItemDB.price * OrderItemDB.qty))
            .join(OrderItemDB, MenuItemDB.id == OrderItemDB.menu_item_id)
            .join(OrderDB, OrderItemDB.order_id == OrderDB.id)
            .filter(func.date(OrderDB.timestamp) == day)
            .scalar()
        )
        return round(total or 0.0, 2)

    def top_selling_items(self, limit: int = 5):
        """Return top N selling items (name, quantity)."""
        results = (
            self.session.query(
                MenuItemDB.name, func.sum(OrderItemDB.qty).label("total_qty")
            )
            .join(OrderItemDB, MenuItemDB.id == OrderItemDB.menu_item_id)
            .group_by(MenuItemDB.name)
            .order_by(func.sum(OrderItemDB.qty).desc())
            .limit(limit)
            .all()
        )
        return [(row[0], row[1]) for row in results]

    def payment_breakdown(self, day: date = None):
        """Return total collected per payment method (cash, card, etc.) for a given day."""
        if day is None:
            day = date.today()

        results = (
            self.session.query(
                PaymentDB.method, func.count(PaymentDB.id).label("count")
            )
            .filter(func.date(PaymentDB.timestamp) == day)
            .group_by(PaymentDB.method)
            .all()
        )
        return {row[0]: row[1] for row in results}

    # --- CSV Export Utilities ---
    def export_top_items_csv(self, filepath: str, limit: int = 5):
        """Export top-selling items to a CSV file."""
        items = self.top_selling_items(limit)
        with open(filepath, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Item", "Quantity Sold"])
            for name, qty in items:
                writer.writerow([name, qty])

    def export_payment_breakdown_csv(self, filepath: str, day: date = None):
        """Export payment breakdown to CSV file."""
        breakdown = self.payment_breakdown(day)
        with open(filepath, mode="w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Payment Method", "Count"])
            for method, count in breakdown.items():
                writer.writerow([method, count])
