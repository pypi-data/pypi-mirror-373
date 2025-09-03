from mm_pos.db import init_db, OrderDB
from mm_pos.tables import TableManager


def test_table_lifecycle(tmp_path):
    db_path = tmp_path / "tables_test.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()
    manager = TableManager(session)

    # Open new table
    t1 = manager.open_table(1)
    assert t1.status == "open"

    # Occupy table
    t1 = manager.occupy_table(1)
    assert t1.status == "occupied"

    # Close table
    t1 = manager.close_table(1)
    assert t1.status == "closed"


def test_merge_tables(tmp_path):
    db_path = tmp_path / "merge_test.db"
    Session = init_db(f"sqlite:///{db_path}")
    session = Session()
    manager = TableManager(session)

    # Create 2 tables
    t1 = manager.open_table(1)
    t2 = manager.open_table(2)

    # Add order to table 2
    order = OrderDB(table=t2)
    session.add(order)
    session.commit()
    assert len(t2.orders) == 1

    # Merge table 2 into table 1
    t1 = manager.merge_tables(1, 2)
    assert len(t1.orders) == 1
    assert t2.status == "closed"
