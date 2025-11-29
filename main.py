from models.database import Database
from tkinter import ttk, simpledialog, messagebox, StringVar
import tkinter as tk

class AddWriteupWindow(tk.Toplevel):
    def __init__(self, parent_window, app, db):
        super().__init__(parent_window)
        self.title("Add New Writeup")
        self.geometry("400x300")
        self.resizable(False, False)
        self.db = db
        self.app = app
        
        categories = [
            "Reverse engineering",
            "Web exploitation",
            "Binary exploitation",
            "Cryptography",
            "miscellaneous",
            "Add new"
        ]
        
        # Title
        tk.Label(self, text="Title:", font=("Arial", 10)).pack(pady=5)
        self.title_entry = tk.Entry(self, width=40)
        self.title_entry.pack(pady=5)
        
        # Category
        tk.Label(self, text="Category:", font=("Arial", 10)).pack(pady=5)
        self.category_combo = ttk.Combobox(self, values=categories, state="readonly", width=37)
        self.category_combo.pack(pady=5)
        
        # URL
        tk.Label(self, text="URL:", font=("Arial", 10)).pack(pady=5)
        self.url_entry = tk.Entry(self, width=40)
        self.url_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Add", command=self.add_clicked).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side="left", padx=5)
        
        self.transient(parent_window)
        self.grab_set()
    
    def add_clicked(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Please enter a title!")
            return
        
        category = self.category_combo.get()
        if not category:
            messagebox.showwarning("Warning", "Please select a category!")
            return
        
        if category == "Add new":
            custom_category = simpledialog.askstring("Input", "Enter custom category name:", parent=self)
            if custom_category:
                category = custom_category
            else:
                return
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL!")
            return
        
        self.db.add_writeup(title, category, url)
        messagebox.showinfo("Success", "Writeup added successfully!")
        self.app.refresh_writeups()
        self.destroy()
    
    def cancel_clicked(self):
        self.destroy()

class EditWriteupWindow(tk.Toplevel):
    def __init__(self, parent_window, app, db, writeup_id, writeup):
        super().__init__(parent_window)
        self.title("Edit Writeup")
        self.geometry("400x300")
        self.resizable(False, False)
        self.db = db
        self.app = app
        self.writeup_id = writeup_id
        
        categories = [
            "Reverse engineering",
            "Web exploitation",
            "Binary exploitation",
            "Cryptography",
            "miscellaneous",
            "Add new"
        ]
        
        # Title
        tk.Label(self, text="Title:", font=("Arial", 10)).pack(pady=5)
        self.title_entry = tk.Entry(self, width=40)
        self.title_entry.insert(0, writeup['title'])
        self.title_entry.pack(pady=5)
        
        # Category
        tk.Label(self, text="Category:", font=("Arial", 10)).pack(pady=5)
        self.category_combo = ttk.Combobox(self, values=categories, state="readonly", width=37)
        self.category_combo.set(writeup['category'])
        self.category_combo.pack(pady=5)
        
        # URL
        tk.Label(self, text="URL:", font=("Arial", 10)).pack(pady=5)
        self.url_entry = tk.Entry(self, width=40)
        self.url_entry.insert(0, writeup['url'])
        self.url_entry.pack(pady=5)
        
        # Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save_clicked).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side="left", padx=5)
        
        self.transient(parent_window)
        self.grab_set()
    
    def save_clicked(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Warning", "Please enter a title!")
            return
        
        category = self.category_combo.get()
        if not category:
            messagebox.showwarning("Warning", "Please select a category!")
            return
        
        if category == "Add new":
            custom_category = simpledialog.askstring("Input", "Enter custom category name:", parent=self)
            if custom_category:
                category = custom_category
            else:
                return
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL!")
            return
        
        self.db.update_writeup(self.writeup_id, title, category, url)
        messagebox.showinfo("Success", "Writeup updated successfully!")
        self.app.refresh_writeups()
        self.destroy()
    
    def cancel_clicked(self):
        self.destroy()

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
        categories = ("Reverse Engineering", "Web Exploitation", "Forensics", "Cryptography", "Miscellaneous", "Binary Exploitation")
        ttk.Button(search_frame, text="Add Writeup", command=self.add_writeup).pack(side="right")
        entry.pack(side="left", padx=10)
        entry.bind("<KeyRelease>", self.search_writeups)
        
        columns = ("id", "title", "category", "url", "status")
        self.table = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            if col == "id":
                self.table.heading(col, text="")
                self.table.column(col, anchor="w", width=0, stretch=False)
            elif col == "status":
                self.table.heading(col, text="Status", anchor="w")
                self.table.column(col, anchor="w", width=100)
            else:
                self.table.heading(col, text=col.capitalize(), anchor="w")
                self.table.column(col, anchor="w", width=150)

        self.table.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Details", width=12, command=self.details).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Edit", width=12, command=self.edit).grid(row=0, column=1, padx=10)
        ttk.Button(btn_frame, text="Open", width=12, command=self.Open_url).grid(row=0, column=2, padx=10)
        ttk.Button(btn_frame, text="Delete", width=12, command=self.delete).grid(row=0, column=3, padx=10)

        self.refresh_writeups()
    
    def search_writeups(self, event=None):
        query = self.search_var.get().lower()

        for row in self.table.get_children():
            self.table.delete(row)

        rows = self.db.search(query) if query else self.db.writeups_all()
        for row in rows:
            self.table.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))
    
    def add_writeup(self):
        AddWriteupWindow(self.master, self, self.db)
        
    def edit(self):
        selected = self.table.focus()
        if not selected:
            messagebox.showwarning("Warning", "No writeup selected!")
            return
        writeup_id = self.table.item(selected)["values"][0]
        writeup = self.db.get_writeup_by_id(writeup_id)
        if writeup:
            EditWriteupWindow(self.master, self, self.db, writeup_id, writeup)
        else:
            messagebox.showerror("Error", "Writeup not found!")
        
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
            self.db.mark_as_readed(writeup_id)
            self.refresh_writeups()
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
            self.table.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    app.pack(fill="both", expand=True)
    app.mainloop()