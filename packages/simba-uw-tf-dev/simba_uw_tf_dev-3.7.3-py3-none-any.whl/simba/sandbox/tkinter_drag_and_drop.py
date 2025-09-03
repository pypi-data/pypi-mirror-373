import os
import sys
import traceback
import importlib.util
import tkinter as tk
from tkinter import ttk

def parse_dnd_data_generic(data):
    if not data:
        return []
    out = []
    cur = ""
    in_brace = False
    for ch in data:
        if ch == "{":
            in_brace = True
            cur = ""
        elif ch == "}":
            in_brace = False
            out.append(cur)
            cur = ""
        elif in_brace:
            cur += ch
        elif not ch.isspace():
            cur += ch
        elif cur:
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    # normalize file:// on windows
    norm = []
    for p in out:
        if p.startswith("file://"):
            p = p.replace("file://", "")
            if sys.platform.startswith("win") and p.startswith("/"):
                p = p[1:]
        norm.append(p)
    return norm

def enable_tkdnd_from_tkinterdnd2(root, widget, callback, verbose=True):
    tk_interp = root.tk

    def vprint(*a, **k):
        if verbose:
            print(*a, **k)

    # Try quick package require tkdnd
    try:
        vprint("Trying 'package require tkdnd' (quick)...")
        root.tk.call('package', 'require', 'tkdnd')
        vprint("tkdnd already present in Tcl auto_path.")
    except Exception as e_quick:
        vprint("tkdnd not found by Tcl (quick):", e_quick)

        # Locate tkinterdnd2 package dir
        spec = importlib.util.find_spec("tkinterdnd2")
        if not spec or not getattr(spec, "origin", None):
            vprint("Could not find 'tkinterdnd2' package in sys.path.")
            vprint("Interpreter:", sys.executable)
            vprint("sys.path entries:", sys.path[:6], "...")
            return False

        pkg_dir = os.path.dirname(spec.origin)
        vprint("Found tkinterdnd2 package at:", pkg_dir)

        candidate_dirs = []
        candidate_dirs.append(os.path.join(pkg_dir, "tkdnd2.8"))
        candidate_dirs.append(os.path.join(pkg_dir, "tkdnd"))
        candidate_dirs.append(os.path.join(pkg_dir, "tkdnd2"))
        candidate_dirs.append(os.path.join(pkg_dir, "tkdnd2.8"))
        candidate_dirs.append(os.path.join(pkg_dir, "tcl"))
        candidate_dirs = [p for p in candidate_dirs if os.path.isdir(p)]

        vprint("Candidate tkdnd directories:", candidate_dirs)

        if not candidate_dirs:
            found = []
            for root_dir, dirs, files in os.walk(pkg_dir):
                for fname in files:
                    if "tkdnd" in fname.lower():
                        found.append(root_dir)
                        break
                if len(found) > 3:
                    break
            candidate_dirs = list(dict.fromkeys(found))
            vprint("Scanned and found possible tkdnd dirs:", candidate_dirs)

        if not candidate_dirs:
            vprint("No tkdnd files found inside tkinterdnd2 install.")
            vprint("Package contents at:", sorted(os.listdir(pkg_dir)))
            return False

        appended = []
        for d in candidate_dirs:
            d_tcl = d.replace("\\", "/")
            try:
                vprint("Appending to Tcl's auto_path:", d_tcl)
                tk_interp.eval(f'set ::auto_path [linsert $::auto_path end "{d_tcl}"]')
                appended.append(d)
            except Exception as e:
                vprint("Failed to append to auto_path:", d, "error:", e)

        vprint("Trying 'package require tkdnd' after appending paths...")
        try:
            root.tk.call('package', 'require', 'tkdnd')
            vprint("Success: tkdnd loaded from appended paths.")
        except Exception as e2:
            vprint("Still couldn't load tkdnd after appending paths:", e2)
            vprint("Appended paths:", appended)
            return False

    def _on_drop(event):
        try:
            if verbose:
                print("RAW tkdnd event.data:", repr(event.data))
            paths = parse_dnd_data_generic(event.data)
            callback(paths)
        except Exception:
            if verbose:
                print("Error in drop handler:", traceback.format_exc())

    try:
        vprint("Registering widget as tkdnd drop target...")
        root.tk.call('tkdnd::drop_target', 'register', str(widget), '*')
        widget.bind('<<Drop>>', _on_drop)
        vprint("Widget bound to tkdnd successfully.")
        return True
    except Exception as ebind:
        vprint("Failed to register/bind widget for tkdnd:", ebind)
        vprint(traceback.format_exc())
        return False

# --- app code ---

def on_drop(paths):
    text.config(state="normal")
    for p in paths:
        text.insert("end", p + "\n")
    text.config(state="disabled")

root = tk.Tk()
root.geometry("700x350")
root.title("Drop files here")

label = ttk.Label(root, text="Drop files into the box below:")
label.pack(anchor="w", padx=10, pady=(10,0))

text = tk.Text(root, height=15, state="disabled")
text.pack(fill="both", expand=True, padx=10, pady=10)

# Must update to ensure widget path exists
root.update_idletasks()

ok = enable_tkdnd_from_tkinterdnd2(root, text, on_drop, verbose=True)
print("enable_tkdnd_from_tkinterdnd2 returned:", ok)
if not ok:
    print("\n\nNOTE: If this fails, make sure your python environment has tkinterdnd2 installed.\n"
          "If you want, paste this output here for help debugging.\n")

root.mainloop()
