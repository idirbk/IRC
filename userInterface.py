import tkinter as tk
from tkinter import scrolledtext
from client import IRCClient
import sys
import logging
import threading
def setup_client():
    port = int(sys.argv[1])
    nickname = sys.argv[2]
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    client = IRCClient(nickname, 'localhost', port)
    client.connect_to_server()
    return client

def send_message(client, event=None):
    message = entry.get()
    if message:
        client.send_command(message)
        text_area.config(state='normal')
        text_area.insert(tk.END, "Vous: " + message + "\n")
        text_area.config(state='disabled')
        text_area.yview(tk.END)  # Fait défiler la zone de texte pour voir le dernier message
        entry.delete(0, tk.END)

def recive_message(client, text_area):
    while True:
        message = client.sock.recv(4096).decode()
        text_area.config(state='normal')
        text_area.insert(tk.END, message + "\n")
        text_area.config(state='disabled')
        text_area.yview(tk.END)
        entry.delete(0, tk.END)

client = setup_client()

root = tk.Tk()
root.title(sys.argv[2])
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.rowconfigure(1, weight=0)
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, state='disabled', height=15)
text_area.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
text_area.insert(tk.END, "ZONE D'AFFICHAGE DES MESSAGES\n")
entry = tk.Entry(root)
entry.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
entry.bind("<Return>", lambda event :send_message(client, event))
entry.focus()


threading.Thread(target=recive_message, args=(client, text_area)).start()

root.mainloop()
