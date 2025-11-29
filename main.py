from tkinter import ttk
import tkinter as tk

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Writeup Manager")

if __name__ == "__main__":
    root = tk.Tk()
    App(root).mainloop()