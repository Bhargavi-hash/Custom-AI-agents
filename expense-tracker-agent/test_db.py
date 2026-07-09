from db import init_db, add_expense, get_total, list_expenses, delete_expense

init_db()

id1 = add_expense(12.50, "coffee", "2026-07-09")
id2 = add_expense(45.00, "groceries", "2026-07-08")
id3 = add_expense(8.00, "coffee", "2026-06-20")
print(f"Inserted expense ids: {id1}, {id2}, {id3}")

print("Total (all time):", get_total())
print("Total (coffee only):", get_total(category="coffee"))
print("Total (July 2026):", get_total(month="2026-07"))
print("Total (coffee in July 2026):", get_total(category="coffee", month="2026-07"))

print("All expenses:", list_expenses())
print("July expenses only:", list_expenses(month="2026-07"))

deleted = delete_expense(id1)
print(f"Deleted id {id1}: {deleted}")
print("Total after delete:", get_total())