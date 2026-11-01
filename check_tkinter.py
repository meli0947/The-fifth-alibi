"""The Fifth Alibi graphical interface compatibility check."""

import platform
import sys


def main():
    print("Python version: ", sys.version.split()[0])
    print("Interpreter: ", sys.executable)
    print("System: ", platform.platform())
    try:
        import tkinter as tk
    except ImportError as error:
        print("\nError: this Python installation does not include Tkinter.")
        print("Install a complete Python distribution with Tkinter; do not use pip install tkinter.")
        print("Details: ", error)
        return 1

    print("Tk version: ", tk.TkVersion)
    if sys.platform == "darwin" and tk.TkVersion < 8.6:
        print("\nError: this Mac is using the outdated system Tk 8.5.")
        print("Tk 8.5 may show a blank window on newer macOS versions.")
        print("The Fifth Alibi requires Tk 8.6 or later.")
        print("\nInstall Python 3.12 or later from python.org and select that interpreter in VS Code.")
        print("Then open a new terminal and rerun this check. which python3 must not show /usr/bin/python3.")
        return 1
    try:
        root = tk.Tk()
        root.title("Tkinter compatibility check")
        root.geometry("460x180")
        message = (
            "Tkinter is working.\n\n"
            "This computer can run The Fifth Alibi GUI.\n"
            "This window will close automatically."
        )
        tk.Label(root, text=message, font=("Arial", 14), padx=25, pady=25).pack(
            fill="both", expand=True
        )
        root.after(1800, root.destroy)
        root.mainloop()
    except tk.TclError as error:
        print("\nError: Tkinter imported, but could not create a window.")
        print("Details: ", error)
        return 1

    print("Tkinter window test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
