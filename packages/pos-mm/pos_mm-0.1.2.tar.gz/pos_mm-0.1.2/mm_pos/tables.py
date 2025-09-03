from sqlalchemy.orm import Session
from mm_pos.db import TableDB


class TableManager:
    def __init__(self, session: Session):
        self.session = session

    def open_table(self, number: int):
        """Open a new table if not already in use."""
        table = self.session.query(TableDB).filter_by(number=number).first()
        if table:
            if table.status != "closed":
                raise ValueError(f"Table {number} is already {table.status}.")
            table.status = "open"
        else:
            table = TableDB(number=number, status="open")
            self.session.add(table)
        self.session.commit()
        return table

    def occupy_table(self, number: int):
        """Mark a table as occupied."""
        table = self.session.query(TableDB).filter_by(number=number).first()
        if not table:
            raise ValueError(f"Table {number} does not exist.")
        table.status = "occupied"
        self.session.commit()
        return table

    def close_table(self, number: int):
        """Mark a table as closed (after bill is settled)."""
        table = self.session.query(TableDB).filter_by(number=number).first()
        if not table:
            raise ValueError(f"Table {number} does not exist.")
        table.status = "closed"
        self.session.commit()
        return table

    def merge_tables(self, table1_num: int, table2_num: int):
        """Merge two tables into one (combine orders)."""
        t1 = self.session.query(TableDB).filter_by(number=table1_num).first()
        t2 = self.session.query(TableDB).filter_by(number=table2_num).first()
        if not t1 or not t2:
            raise ValueError("Both tables must exist to merge.")
        if t1.status == "closed" or t2.status == "closed":
            raise ValueError("Cannot merge closed tables.")

        # Move orders from t2 → t1
        for order in t2.orders:
            order.table = t1
        t2.status = "closed"
        self.session.commit()
        return t1
