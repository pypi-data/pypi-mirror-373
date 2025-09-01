from tkinter import *
from tkinter.messagebox import showinfo
from tkinter.filedialog import askopenfilename, asksaveasfilename
import os
from importlib import resources


class VIEditor:
    def __init__(self, root):
        self.root = root
        self.root.geometry("500x350")
        
        with resources.path("vi_editor.assets", "vi.ico") as icon_path:
            self.root.wm_iconbitmap(default=icon_path)
        self.root.title("VI Editor by Aditya")

        # State variables
        self.key_buffer = ""
        self.text_mode = False
        self.insert_var = False
        self.file = None
        self.last_key_press_time = 0
        self.replace_mode = False
        self.status = StringVar()
        self.yank_buffer = ""
        self.undo_stack = []
        self.status.set("Command mode")

        self.insert_mode_keys = ["i", "a", "A", "o"]

        # Widgets
        self._make_widgets()
        self._make_menu()

    def _make_widgets(self):
        # Status bar
        self.status_bar = Label(self.root, textvariable=self.status)
        self.status_bar.pack(side=BOTTOM, fill=X)

        # Text area with scrollbar
        scroll = Scrollbar(self.root)
        scroll.pack(side=RIGHT, fill=Y)
        self.text = Text(
            self.root, font="lucida 13", yscrollcommand=scroll.set, undo=True
        )
        self.text.pack(expand=True, fill=BOTH)
        scroll.config(command=self.text.yview)

        self.text.config(state="disabled")
        self.text.bind("<Key>", self.key_press)

    def _make_menu(self):
        menubar = Menu(self.root)

        # File menu
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.new_file)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save_file)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=filemenu)

        # Edit menu
        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(
            label="Cut", command=lambda: self.text.event_generate("<<Cut>>")
        )
        editmenu.add_command(
            label="Copy", command=lambda: self.text.event_generate("<<Copy>>")
        )
        editmenu.add_command(
            label="Paste", command=lambda: self.text.event_generate("<<Paste>>")
        )
        menubar.add_cascade(label="Edit", menu=editmenu)

        # Help menu
        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About VI Editor", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.root.config(menu=menubar)

    # ---------------- File ops -----------------
    def new_file(self):
        self.root.title("Untitled - VI Editor")
        self.file = None
        self.text.config(state="normal")
        self.text.delete(1.0, END)
        self.text.config(state="disabled")

    def open_file(self):
        self.file = askopenfilename(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")],
        )
        if not self.file:
            return
        self.root.title(os.path.basename(self.file) + " - VI Editor")
        with open(self.file, "r") as f:
            data = f.read()
        self.text.config(state="normal")
        self.text.delete(1.0, END)
        self.text.insert(1.0, data)
        self.text.config(state="disabled")

    def save_file(self):
        if not self.file:
            self.file = asksaveasfilename(
                initialfile="Untitled.txt",
                defaultextension=".txt",
                filetypes=[("All Files", "*.*"), ("Text Document", "*.txt")],
            )
        if not self.file:
            return
        with open(self.file, "w") as f:
            f.write(self.text.get(1.0, END))
        self.root.title(os.path.basename(self.file) + " - VI Editor")

    def exit_app(self):
        self.root.destroy()

    # ---------------- Utility -----------------
    def about(self):
        info = """Insert Mode - i, a, A, o
Command Mode - dd, ndd, C, D, x, r, R, s, S, cw, dw, cc
Miscellaneous - yy, p, u, w, b, 0, $, h, i, j, k"""
        showinfo("VI Editor", info)

    def get_cursor_position(self):
        return self.text.index("insert")

    def set_cursor_position(self, pos):
        self.text.mark_set(INSERT, str(pos))

    def get_cursor_line(self):
        return self.get_cursor_position().split(".")[0]

    def delete_character(self):
        pos = self.get_cursor_position().split(".")
        self.text.delete(f"{pos[0]}.{pos[1]}", f"{pos[0]}.{int(pos[1])+1}")

    def delete_line(self, n=1):
        line_num = float(self.get_cursor_line())
        self.text.delete(str(line_num), str(line_num + n))

    def yank_line(self):
        line = self.get_cursor_line()
        self.yank_buffer = self.text.get(f"{line}.0", f"{line}.end+1c")

    def put_line(self):
        pos = self.get_cursor_position()
        self.text.insert(pos, self.yank_buffer)

    def undo(self):
        try:
            self.text.edit_undo()
        except:
            pass

    # ---------------- Modes -----------------
    def convert_insert_mode(self, insert_char):
        pos = self.get_cursor_position()
        if insert_char == "a":
            row, col = pos.split(".")
            self.set_cursor_position(f"{row}.{int(col)+1}")
        elif insert_char == "A":
            row = pos.split(".")[0]
            self.set_cursor_position(f"{row}.end")
        elif insert_char == "o":
            row = int(self.get_cursor_line())
            self.text.insert(f"{row}.end", "\n")
            self.set_cursor_position(f"{row+1}.0")

    def command_mode(self, command):
        if command.endswith("dd"):
            n = command.replace("d", "")
            self.delete_line(int(n) if n.isdigit() else 1)

        elif command == "C" or command == "D":
            pos = self.get_cursor_position()
            line = float(self.get_cursor_line())
            self.text.delete(str(pos), str(line + 1))
            if command == "C":
                self.insert_var = True

        elif command == "x":
            self.delete_character()

        elif command == "r":
            self.replace_mode = True

        elif command == "R":
            self.text_mode = False
            self.replace_mode = "continuous"

        elif command == "s":
            self.delete_character()
            self.insert_var = True
            self.status.set("Insert mode")

        elif command == "S":
            self.delete_line()
            row = self.get_cursor_line()
            self.text.insert(f"{row}.0", "\n")
            self.set_cursor_position(f"{row}.0")
            self.insert_var = True
            self.status.set("Insert mode")

        elif command == "yy":
            self.yank_line()

        elif command == "p":
            self.put_line()

        elif command == "u":
            self.undo()

        elif command == "0":
            row = self.get_cursor_line()
            self.set_cursor_position(f"{row}.0")

        elif command == "$":
            row = self.get_cursor_line()
            line_text = self.text.get(f"{row}.0", f"{row}.end")
            last_col = len(line_text)
            self.set_cursor_position(f"{row}.{last_col}")

        elif command == "w":
            self.set_cursor_position(
                self.text.search(r"\W", self.get_cursor_position(), regexp=True)
            )

        elif command == "b":
            row, col = map(int, self.get_cursor_position().split("."))
            if col > 0:
                self.set_cursor_position(f"{row}.{col-1}")

        elif command == "cw":
            self.text.config(state="normal")
            start = self.get_cursor_position()
            end = self.text.search(
                r"\W", start, regexp=True, stopindex=f"{start} lineend"
            )
            if not end:
                end = f"{self.get_cursor_line()}.end"
            self.text.delete(start, end)
            self.text.config(state="disabled")
            self.insert_var = True
            self.status.set("Insert mode")

        elif command == "dw":
            self.text.config(state="normal")
            start = self.get_cursor_position()
            end = self.text.search(
                r"\W", start, regexp=True, stopindex=f"{start} lineend"
            )
            if not end:
                end = f"{self.get_cursor_line()}.end"
            self.text.delete(start, end)
            self.text.config(state="disabled")

        elif command == "cc":
            self.delete_line()
            row = self.get_cursor_line()
            self.text.insert(f"{row}.0", "\n")
            self.set_cursor_position(f"{row}.0")
            self.insert_var = True
            self.status.set("Insert mode")

        elif command == "h":
            row, col = self.get_cursor_position().split(".")
            self.set_cursor_position(f"{row}.{int(col)-1}")

        elif command == "l":
            row, col = self.get_cursor_position().split(".")
            self.set_cursor_position(f"{row}.{int(col)+1}")

        elif command == "j":
            row, col = self.get_cursor_position().split(".")
            self.set_cursor_position(f"{int(row)+1}.{col}")

        elif command == "k":
            row, col = self.get_cursor_position().split(".")
            self.set_cursor_position(f"{int(row)-1}.{col}")

    # ---------------- Key handling -----------------
    def key_press(self, event):
        current_time = event.time

        if self.insert_var:
            self.text_mode = True
            self.text.config(state="normal")

        if self.text_mode and event.keysym == "Escape":
            self.text_mode = False
            self.insert_var = False
            self.text.config(state="disabled")
            self.status.set("Command mode")

        if self.replace_mode == True and not self.text_mode:
            # single-char replace (from 'r')
            self.text.config(state="normal")
            self.delete_character()
            self.text.insert(self.get_cursor_position(), str(event.char))
            self.text.config(state="disabled")
            self.replace_mode = False

        elif self.replace_mode == "continuous":
            if event.keysym == "Escape":
                self.replace_mode = False
                self.status.set("Command mode")
                return "break"

            self.text.config(state="normal")
            self.delete_character()
            self.text.insert(self.get_cursor_position(), str(event.char))
            self.text.config(state="disabled")
            return "break"

        if (
            not self.text_mode
            and event.keysym not in self.insert_mode_keys
            and not self.replace_mode
        ):
            self.key_buffer += str(event.keysym)
            if current_time - self.last_key_press_time > 200:
                self.key_buffer = event.keysym

            self.text.config(state="normal")
            self.command_mode(self.key_buffer)
            self.text.config(state="disabled")
            self.last_key_press_time = current_time

        if (
            not self.text_mode
            and event.keysym in self.insert_mode_keys
            and not self.replace_mode
        ):
            self.insert_var = True
            self.status.set("Insert mode")
            self.convert_insert_mode(event.keysym)


def run():
    root = Tk()
    VIEditor(root)
    root.mainloop()


if __name__ == "__main__":
    root = Tk()
    VIEditor(root)
    root.mainloop()