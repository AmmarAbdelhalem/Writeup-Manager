from tkinter import ttk, simpledialog, messagebox, StringVar
from models.database import Database
from PIL import Image, ImageDraw
import tkinter as tk
import threading
import pystray

class FilterWindow(tk.Toplevel):
    def __init__(self, parent_window, app, db):
        super().__init__(parent_window)
        self.title("Filter Writeups")
        self.geometry("350x200")
        self.resizable(False, False)
        self.db = db
        self.app = app
        
        tk.Label(self, text="Filter by Category:", font=("Arial", 10)).pack(pady=5)
        categories = self.db.get_all_categories()
        self.category_var = StringVar()
        self.category_var.set("All")
        category_combo = ttk.Combobox(self, textvariable=self.category_var, values=["All"] + categories, state="readonly", width=30)
        category_combo.pack(pady=5)

        tk.Label(self, text="Filter by Status:", font=("Arial", 10)).pack(pady=5)
        self.status_var = StringVar()
        self.status_var.set("All")
        status_combo = ttk.Combobox(self, textvariable=self.status_var, values=["All", "Readed", "Unreaded"], state="readonly", width=30)
        status_combo.pack(pady=5)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Apply", command=self.apply_filter).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Clear", command=self.clear_filter).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", command=self.destroy).pack(side="left", padx=5)
        
        self.transient(parent_window)
        self.grab_set()
    
    def apply_filter(self):
        category = self.category_var.get()
        status = self.status_var.get()
        
        # Store current filter state
        self.app.current_filter_category = category
        self.app.current_filter_status = status
        
        for row in self.app.table.get_children():
            self.app.table.delete(row)
        
        if category == "All" and status == "All":
            rows = self.db.writeups_all()
        elif category == "All":
            rows = self.db.filter_by_status(status)
        elif status == "All":
            rows = self.db.filter_by_category(category)
        else:
            rows = self.db.filter_by_category_and_status(category, status)
        
        for row in rows:
            self.app.table.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))
    
    def clear_filter(self):
        self.category_var.set("All")
        self.status_var.set("All")
        self.app.current_filter_category = "All"
        self.app.current_filter_status = "All"
        self.app.refresh_writeups()

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
        
        # Filter tracking
        self.current_filter_category = "All"
        self.current_filter_status = "All"
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=6)

        tk.Label(search_frame, text="Search").pack(side="left")
        self.search_var = tk.StringVar()
        entry = tk.Entry(search_frame, textvariable=self.search_var, width=40)
        entry.insert(0, "Search for title")
        entry.config(fg="gray")
        entry.pack(side="left", padx=10)
        entry.bind("<FocusIn>", self.on_entry_focus_in)
        entry.bind("<FocusOut>", self.on_entry_focus_out)
        entry.bind("<KeyRelease>", self.search_writeups)
        ttk.Button(search_frame, text="Add Writeup", command=self.add_writeup).pack(side="right", padx=5)
        ttk.Button(search_frame, text="Filter", command=self.open_filter).pack(side="right", padx=5)
        
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
        ttk.Button(btn_frame, text="Change status", width=16, command=self.change_status).grid(row=0, column=3, padx=10)
        ttk.Button(btn_frame, text="Delete", width=12, command=self.delete).grid(row=0, column=4, padx=10)
        
        self.refresh_writeups()
    
    def change_status(self):
        selected = self.table.focus()
        if not selected:
            messagebox.showwarning("Warning", "No writeup selected!")
            return
        writeup_id = self.table.item(selected)["values"][0]
        writeup = self.db.get_writeup_by_id(writeup_id)
        if writeup:
            if writeup['status'] == 'Unreaded':
                self.db.mark_as_readed(writeup_id)
            elif writeup['status'] == 'Readed':
                self.db.mark_as_unreaded(writeup_id)
        else:
            messagebox.showerror("Error", "Writeup not found!")
        self.reapply_filter()
    
    def search_writeups(self, event=None):
        query = self.search_var.get().strip()
        if query == "Search for title":
            query = ""
        for row in self.table.get_children():
            self.table.delete(row)
        if query:
            rows = self.db.search(query)
        else:
            rows = self.db.writeups_all()
        for row in rows:
            self.table.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))
    
    def on_entry_focus_in(self, event):
        if self.search_var.get() == "Search for title":
            self.search_var.set("")
            event.widget.config(fg="black")
    
    def on_entry_focus_out(self, event):
        if self.search_var.get() == "":
            self.search_var.set("Search for title")
            event.widget.config(fg="gray")
    
    def reapply_filter(self):
        for row in self.table.get_children():
            self.table.delete(row)
        
        if self.current_filter_category == "All" and self.current_filter_status == "All":
            rows = self.db.writeups_all()
        elif self.current_filter_category == "All":
            rows = self.db.filter_by_status(self.current_filter_status)
        elif self.current_filter_status == "All":
            rows = self.db.filter_by_category(self.current_filter_category)
        else:
            rows = self.db.filter_by_category_and_status(self.current_filter_category, self.current_filter_status)
        
        for row in rows:
            self.table.insert("", "end", values=(row[0], row[1], row[2], row[3], row[4]))
    
    def add_writeup(self):
        AddWriteupWindow(self.master, self, self.db)
    
    def open_filter(self):
        FilterWindow(self.master, self, self.db)
        
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

class Tray():
    def __init__(self, master: tk.Tk):
        self.master = master
    
    def hide(self):
        self.master.withdraw()
    
    def open(self):
        self.master.deiconify()
        self.master.after(0, self.master.lift)
    
    def close(self):
        icon.stop()
        self.master.destroy()
    
    def create_image(self):
        img = Image.new("RGB", (64, 64), "black")
        b = ImageDraw.Draw(img)
        b.rectangle([16, 16, 48, 48], fill="white")
        return img
        
        

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    x = Tray(root)
    root.protocol("WM_DELETE_WINDOW", x.hide)
    icon = pystray.Icon(
        name="WriteaupManager",
        icon=x.create_image(),
        title="Writeup Manager",
        menu=pystray.Menu(
            pystray.MenuItem("Open", x.open),
            pystray.MenuItem("Close", x.close),
        )
    )
    threading.Thread(target=icon.run, daemon=True).start()
    app.pack(fill="both", expand=True)
    app.mainloop()