import os
import shutil
import tkinter as tk
from tkinter import messagebox

# You can modify this path to check other locations if needed
UPDATE_SOURCE = r"D:\\AstitvaUpdate"

def update_app():
    if not os.path.exists(UPDATE_SOURCE):
        messagebox.showerror("Update Error", f"Update source folder not found: {UPDATE_SOURCE}")
        return

    try:
        current_dir = os.getcwd()
        # Copy all files and folders from update source to current directory
        for item in os.listdir(UPDATE_SOURCE):
            src_path = os.path.join(UPDATE_SOURCE, item)
            dst_path = os.path.join(current_dir, item)
            if os.path.isdir(src_path):
                if os.path.exists(dst_path):
                    shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            else:
                shutil.copy2(src_path, dst_path)
        messagebox.showinfo("Success", "Update Complete")
    except Exception as e:
        messagebox.showerror("Update Error", f"Failed to update: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    update_app()
