import sqlite3

DB_PATH = "expenses.db"

def init_db():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    note TEXT
                );
                """ 
            )
            conn.commit()
            print(f"Database '{DB_PATH}' initialized.")


    except sqlite3.OperationalError as e:
        print(f"Init failed: {e}")


def add_expense(amount: float, category: str, date: str, note: str = "") -> int:
    """Insert a new expense, return its id."""
    sql = '''INSERT INTO expenses(amount, category, date, note)
             VALUES(?, ?, ?, ?)
          '''
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (amount, category, date, note))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.OperationalError as e:
        print(f"Insert failed: {e}")
        return None

def get_total(category: str = None, month: str = None) -> float:

    """Sum amounts, optionally filtered by category and/or month (e.g. '2026-07')."""
    
    sql = '''
        SELECT SUM(amount) FROM expenses
        WHERE 1=1
    '''

    params = []
    if category:
        sql += " AND category = ?"
        params.append(category)
    if month:
        sql += " AND strftime('%Y-%m', date) = ?"
        params.append(month)

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            result = cursor.fetchone()[0]
        
            return result if result is not None else 0.0
        
    except sqlite3.OperationalError as e:
        print(f"Fetch failed: {e}")
        return None

def list_expenses(category: str = None, month: str = None) -> list[dict]:
    """Return matching expense rows as a list of dicts."""
    
    sql = '''
        SELECT * FROM expenses
        WHERE 1=1
    '''

    params = []
    if category:
        sql += " AND category = ?"
        params.append(category)
    if month:
        sql += " AND strftime('%Y-%m', date) = ?"
        params.append(month)


    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            result = cursor.fetchall()
            return [
                {"id": r[0], "amount": r[1], "category": r[2], "date": r[3], "note": r[4]}
                for r in result
            ]
    except sqlite3.OperationalError as e:
        print(f"Fetch failed: {e}")
        return None

def delete_expense(expense_id: int) -> bool:
    """Delete by id, return True if a row was actually deleted."""
    
    sql = '''
        DELETE FROM expenses WHERE id=?
    '''

    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (expense_id,))
            conn.commit()
            
            return cursor.rowcount > 0
        
    except sqlite3.OperationalError as e:
        print(f"Delete failed: {e}")
        return None
    
