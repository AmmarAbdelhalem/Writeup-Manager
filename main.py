from models.database import Database
from tkinter import ttk, simpledialog, messagebox
import tkinter as tk

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Writeup Manager")
        self.master.geometry("800x600")
        self.master.minsize(600, 400)
        self.db = Database()
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=6)

        tk.Label(search_frame, text="Search").pack(side="left")
        self.search_var = tk.StringVar()
        entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        ttk.Button(search_frame, text="Add Writeup", command=self.add_writeup).pack(side="right")
        entry.pack(side="left", padx=10)
        entry.bind("<KeyRelease>", self.search_writeups)
        
        columns = ("id", "title", "category", "url")
        self.table = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            if col == "id":
                self.table.heading(col, text="")
                self.table.column(col, anchor="w", width=0, stretch=False)
            else:
                self.table.heading(col, text=col.capitalize(), anchor="w")
                self.table.column(col, anchor="w", width=170)

        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Details", width=12, command=self.details).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Oepn", width=12, command=self.Open_url).grid(row=0, column=1, padx=10)
        ttk.Button(btn_frame, text="Delete", width=12, command=self.delete).grid(row=0, column=3, padx=10)

        self.refresh_writeups()
    
    def search_writeups(self, event=None):
        query = self.search_var.get().lower()

        for row in self.table.get_children():
            self.table.delete(row)

        rows = self.db.search(query) if query else self.db.writeups_all()
        for row in rows:
            self.table.insert("", "end", values=(row[0], row[1], row[2], row[3]))
    
    def add_writeup(self):
        title = simpledialog.askstring("Input", "Enter writeup title:", parent=self)
        if not title:
            return
        category = simpledialog.askstring("Input", "Enter writeup category:", parent=self)
        if category is None:
            return
        url = simpledialog.askstring("Input", "Enter writeup URL:", parent=self)
        if url is None:
            return
        self.db.add_writeup(title, category, url)
        messagebox.showinfo("Success", "Writeup added successfully!")
        self.refresh_writeups()
        
    def details(self):
        selected = self.table.focus()
        if not selected:
            messagebox.showwarning("Warning", "No writeup selected!")
            return
        writeup_id = self.table.item(selected)["values"][0]
        writeup = self.db.get_writeup_by_id(writeup_id)
        if writeup:
            details = f"Title: {writeup['title']}\nCategory: {writeup['category']}\nURL: {writeup['url']}"
            messagebox.showinfo("Writeup Details", details)
        else:
            messagebox.showerror("Error", "Writeup not found!")
    
    def Open_url(self):
        selected = self.table.focus()
        if not selected:
            messagebox.showwarning("Warning", "No writeup selected!")
            return
        writeup_id = self.table.item(selected)["values"][0]
        writeup = self.db.get_writeup_by_id(writeup_id)
        if writeup and writeup['url']:
            import webbrowser
            webbrowser.open(writeup['url'])
        else:
            messagebox.showerror("Error", "Writeup URL not found!")
    
    def delete(self):
        selected = self.table.focus()
        if not selected:
            messagebox.showwarning("Warning", "No writeup selected!")
            return
        writeup_id = self.table.item(selected)["values"][0]
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this writeup?")
        if confirm:
            self.db.delete_writeup(writeup_id)
            messagebox.showinfo("Success", "Writeup deleted successfully!")
            self.refresh_writeups()
    
    def refresh_writeups(self):
        for row in self.table.get_children():
            self.table.delete(row)
        rows = self.db.writeups_all()
        for row in rows:
            self.table.insert("", "end", values=(row[0], row[1], row[2], row[3]))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    app.pack(fill="both", expand=True)
    app.mainloop()