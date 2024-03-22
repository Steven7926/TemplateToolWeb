from tkinter import *
from tkinter.ttk import *
from objects.table_editor import TableEditor

# Just the main file, it all kicks off here.

if __name__ == "__main__":
    root = Tk()
    root.geometry('1600x700')
    root.title("TemplateTool")
    root.iconbitmap("./assets/icon.ico")
    root.configure(background='#192428')
    TableEditor(root).buildUI()
    root.mainloop()