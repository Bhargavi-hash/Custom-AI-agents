# eval_cases.py — just the data, no logic yet
test_cases = [
    {
        "query": "I spent $12 on coffee today",
        "expected_tool": "add_expense",
        "expected_args": {"amount": 12.0, "category": "coffee"},  
    },
    {
        "query": "How much have I spent on groceries?",
        "expected_tool": "get_total",
        "expected_args": {"category": "groceries"},
    },
    {
        "query": "Delete expense number 5",
        "expected_tool": "delete_expense",
        "expected_args": {"expense_id": 5},
    },
]
    