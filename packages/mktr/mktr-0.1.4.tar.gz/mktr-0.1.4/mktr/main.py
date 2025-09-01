import customtkinter as ctk
from tkinter import messagebox, filedialog
import shutil
import glob
import os
import sys
import argparse


ctk.set_appearance_mode("dark")  # Modes: "dark", "light", "system"
ctk.set_default_color_theme("blue")  # Themes: "blue", "dark-blue", "green"


def parse_tree(tree_str, base_path):
    """
    Parse a tree structure string and create directories/files accordingly.
    :param tree_str: String representation of the tree structure.
    :param base_path: Base directory where the structure will be created.
    """
    path_stack = []
    for line in tree_str.strip().splitlines():
        line = line.rstrip()
        if not any(c in line for c in ('├', '└', '│', '─')) and '/' not in line and '.' not in line:
            continue

        # Strip the line of comments
        stripped = line.split('#', 1)[0]

        # Strip the line of whitespace
        stripped = stripped.strip()

        # Strip the line of tree markers and calculate indentation
        stripped = stripped.lstrip('│├└─ ')

        # Calculate indentation level
        indent = (len(line) - len(stripped)) // 4

        # Determine if the line represents a directory or a file
        is_dir = stripped.endswith('/')

        # Get the name without the trailing slash
        name = stripped.rstrip('/')

        if not name or any(char in name for char in '*<>?"|'):
            continue
        while len(path_stack) > indent:
            path_stack.pop()
        path_stack.append(name)
        full_path = os.path.join(base_path, *path_stack)
        try:
            if is_dir:
                os.makedirs(full_path, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, 'w') as f:
                    pass
        except Exception as e:
            print(f"Failed to create {full_path}: {e}")


class App(ctk.CTk):
    """
    Main application class for the mktr GUI tool.
    This class sets up the main window, handles user interactions, and manages the filesystem creation process.
    """
    def __init__(self):
        super().__init__()

        self.title("mktr - Create Filesystem from Tree")
        self.geometry("600x500")
        self.resizable(False, False)

        # Variables
        self.base_path_var = ctk.StringVar(value=os.getcwd())

        # Widgets
        self.label = ctk.CTkLabel(self, text="Paste Tree Structure:")
        self.label.pack(anchor='w', padx=10, pady=(10, 0))

        self.text_area = ctk.CTkTextbox(self, width=580, height=280)
        self.text_area.pack(padx=10, pady=5)

        folder_frame = ctk.CTkFrame(self)
        folder_frame.pack(fill='x', padx=10, pady=5)

        self.base_label = ctk.CTkLabel(folder_frame, text=" Root Directory:", padx=5)
        self.base_label.pack(side='left', padx=(0, 5), pady=5)

        self.base_entry = ctk.CTkEntry(folder_frame, textvariable=self.base_path_var, width=400)
        self.base_entry.pack(side='left', padx=(5, 0))

        self.browse_btn = ctk.CTkButton(folder_frame, text="Browse...", command=self.choose_folder, width=80)
        self.browse_btn.pack(side='left', padx=5)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)


        self.status_label = ctk.CTkLabel(self, text="...", text_color="#A3BE8C")
        self.status_label.pack(pady=(0, 10))

        # Create Filesystem button - green for success
        self.create_btn = ctk.CTkButton(btn_frame, text="Create Filesystem", command=self.on_create, width=150, fg_color="#418856", hover_color="#226436")
        self.create_btn.pack(side='left', padx=10, pady=10)

        # color red for clear button
        self.clear_btn = ctk.CTkButton(btn_frame, text="Clear", command=self.on_clear, width=150) # , fg_color="#BF616A", hover_color="#922B35")
        self.clear_btn.pack(side='left', padx=10, pady=10)

        # Exit button
        self.exit_btn = ctk.CTkButton(btn_frame, text="Exit", command=self.quit, width=150)
        self.exit_btn.pack(side='left', padx=10, pady=10)


    def choose_folder(self):
        folder = filedialog.askdirectory(initialdir=self.base_path_var.get())
        if folder:
            self.base_path_var.set(folder)
            self.status_label.configure(text=f"Base folder set to: {folder}", text_color="#A3BE8C")

    def on_create(self):
        tree_str = self.text_area.get("1.0", "end")
        base_path = self.base_path_var.get()

        if not os.path.isdir(base_path):
            messagebox.showwarning("Invalid Folder", "Please select a valid base folder.")
            return
        if not tree_str.strip():
            messagebox.showwarning("Empty Input", "Please paste a tree structure.")
            return

        try:
            parse_tree(tree_str, base_path)
            self.status_label.configure(text="Filesystem created successfully.", text_color="#A3BE8C")
            # messagebox.showinfo("Success", "Filesystem created successfully.")
        except Exception as e:
            self.status_label.configure(text=f"Error: {e}", text_color="#BF616A")
            messagebox.showerror("Error", str(e))

    def on_clear(self):
        self.text_area.delete("1.0", "end")
        self.status_label.configure(text="")


def destroy_path_glob(pattern):
    matched = glob.glob(pattern)
    if not matched:
        print(f"Error: No files or directories matching '{pattern}' found.")
        sys.exit(1)

    for path in matched:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"Directory '{path}' destroyed successfully.")
            elif os.path.isfile(path):
                os.remove(path)
                print(f"File '{path}' deleted successfully.")
            else:
                print(f"Skipped '{path}': Not a file or directory.")
        except Exception as e:
            print(f"Error destroying '{path}': {e}")



def run_from_file(filename):
    """
    Run the tree structure parser from a file.
    :param filename: Path to the file containing the tree structure.
    """
    if not os.path.isfile(filename):
        print(f"Error: File '{filename}' does not exist.")
        sys.exit(1)
    with open(filename, 'r', encoding='utf-8') as f:
        tree_str = f.read()
    base_path = os.getcwd()
    try:
        parse_tree(tree_str, base_path)
        print("Filesystem created successfully.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Create or destroy filesystem from a tree structure.")
    parser.add_argument('file', nargs='?', help="Text file containing tree structure")
    parser.add_argument('--destroy', metavar='DIR', help="Recursively delete the specified directory")

    args = parser.parse_args()

    if args.destroy:
        destroy_path_glob(args.destroy)
    elif args.file:
        run_from_file(args.file)
    else:
        app = App()
        app.mainloop()


if __name__ == "__main__":
    main()