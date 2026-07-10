import tkinter as tk
from tkinter import scrolledtext
import threading
from main import get_agent_response

contents = []

def send_message():
    user_query = entry.get()
    if not user_query.strip():
        return
    entry.delete(0, tk.END)

    chat_display.insert(tk.END, f"You: {user_query}\n\n")
    chat_display.see(tk.END)

    # Run the (slow) API call in a background thread, so the window doesn't freeze
    threading.Thread(target=process_query, args=(user_query,)).start()

def process_query(user_query):
    response_text = get_agent_response(user_query, contents)
    chat_display.insert(tk.END, f"Agent: {response_text}\n\n")
    chat_display.see(tk.END)

root = tk.Tk()
root.title("Google Calendar Agent")
root.geometry("500x600")

chat_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='normal')
chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

entry = tk.Entry(root)
entry.pack(fill=tk.X, padx=10, pady=(0, 10))
entry.bind("<Return>", lambda event: send_message())

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(pady=(0, 10))

root.mainloop()