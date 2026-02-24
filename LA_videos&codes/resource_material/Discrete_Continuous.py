"""
Discrete Signal Array Operations
=================================
Enter two discrete sequences like [4, 7, 2] and [2, 3, 7]
and visualise: Addition · Subtraction · Multiplication
as stem (lollipop) plots with value labels on every sample.
"""

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import messagebox
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Colour theme ─────────────────────────────────────────────
BG       = '#f5f7fa'
PANEL    = '#ffffff'
ENTRY_BG = '#eef1f7'
FG       = '#1a1a2e'
ACCENT   = '#3a5bd9'
COLORS   = {
    'x1':  '#1565C0',   # deep blue
    'x2':  '#E65100',   # deep orange
    'add': '#2E7D32',   # dark green
    'sub': '#C62828',   # dark red
    'mul': '#6A1B9A',   # deep purple
}


# ═══════════════════════════════════════════════════════════════
def parse_array(text: str):
    """Parse '4, 7, 2' or '[4 7 2]' into a numpy int/float array."""
    text = text.strip().strip('[]')
    vals = [float(v) for v in text.replace(',', ' ').split()]
    return np.array(vals)


def pad_to_same(a: np.ndarray, b: np.ndarray):
    """Zero-pad the shorter array so both have the same length."""
    diff = len(a) - len(b)
    if diff > 0:
        b = np.concatenate([b, np.zeros(diff)])
    elif diff < 0:
        a = np.concatenate([a, np.zeros(-diff)])
    return a, b


# ═══════════════════════════════════════════════════════════════
def draw_stem(ax, n, x, color, title, ylabel="x[n]", annotate=True):
    """Draw a single styled stem plot with value annotations."""
    ax.set_facecolor('#ffffff')
    ax.tick_params(colors=FG, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor('#d0d5e8')

    ml, sl, bl = ax.stem(n, x, linefmt=color, markerfmt='o', basefmt='grey')
    ml.set_markerfacecolor(color)
    ml.set_markeredgecolor(color)
    ml.set_markersize(8)
    import matplotlib.pyplot as plt
    plt.setp(sl, linewidth=2.0, alpha=0.8, color=color)
    plt.setp(bl, linewidth=0.8)

    ax.set_title(title, color=color, fontsize=10, pad=5, fontfamily='monospace')
    ax.set_ylabel(ylabel, color=FG, fontsize=9)
    ax.set_xlabel("n  (sample index)", color='#555577', fontsize=8)
    ax.grid(True, alpha=0.25, color='#c0c8e8')
    ax.axhline(0, color='#aaaacc', linewidth=0.9)

    # ── Value label above/below each stem head ────────────────
    if annotate:
        for ni, xi in zip(n, x):
            offset = 9 if xi >= 0 else -14
            ax.annotate(
                f"{xi:g}",
                xy=(ni, xi),
                xytext=(0, offset),
                textcoords='offset points',
                fontsize=9, fontweight='bold',
                color='#ffffff',
                ha='center', va='bottom',
                bbox=dict(boxstyle='round,pad=0.15', fc=color,
                          ec='none', alpha=0.85)
            )

    # ── Tick marks at every integer n ────────────────────────
    ax.set_xticks(n)
    ax.set_xticklabels([str(int(ni)) for ni in n], color=FG, fontsize=8)


# ═══════════════════════════════════════════════════════════════
class DiscreteArrayApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Discrete Signal Array Operations")
        self.root.configure(bg=BG)
        self.root.state('zoomed')
        self._build_ui()
        self._update()

    # ── Layout ────────────────────────────────────────────────
    def _build_ui(self):
        # Top banner
        tk.Frame(self.root, bg=ACCENT, height=4).pack(fill='x')

        hdr = tk.Frame(self.root, bg=BG, pady=8)
        hdr.pack(fill='x')
        tk.Label(hdr, text="Discrete Signal Array Operations",
                 font=('Consolas', 17, 'bold'), bg=BG, fg=ACCENT).pack(side='left', padx=20)
        tk.Label(hdr, text="x\u2081[n] \u25c6 x\u2082[n]  →  Addition · Subtraction · Multiplication",
                 font=('Consolas', 10), bg=BG, fg='#6670aa').pack(side='left', padx=6)

        # Body: left panel + right canvas
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill='both', expand=True, padx=6, pady=4)

        left = tk.Frame(body, bg=PANEL, width=300, relief='flat',
                        highlightbackground='#d0d5e8', highlightthickness=1)
        left.pack(side='left', fill='y', padx=(0, 6))
        left.pack_propagate(False)

        right = tk.Frame(body, bg=BG)
        right.pack(side='left', fill='both', expand=True)

        self._build_controls(left)
        self._build_canvas(right)

    # ── Controls ──────────────────────────────────────────────
    def _build_controls(self, parent):

        def sep(text):
            tk.Label(parent, text=text, font=('Consolas', 11, 'bold'),
                     bg=PANEL, fg=ACCENT).pack(anchor='w', padx=12, pady=(14, 0))
            tk.Frame(parent, bg=ACCENT, height=1).pack(fill='x', padx=12, pady=(2, 6))

        def array_input(label, default, color):
            tk.Label(parent, text=label, font=('Consolas', 10),
                     bg=PANEL, fg=color).pack(anchor='w', padx=14)
            var = tk.StringVar(value=default)
            e = tk.Entry(parent, textvariable=var, font=('Consolas', 12, 'bold'),
                         bg=ENTRY_BG, fg=FG, insertbackground=ACCENT,
                         relief='flat', bd=6)
            e.pack(fill='x', padx=12, pady=(2, 8))
            return var

        sep("  Signal Inputs")
        tk.Label(parent,
                 text="Enter values separated by commas.\nArrays are zero-padded if lengths differ.",
                 font=('Consolas', 8), bg=PANEL, fg='#888899',
                 justify='left').pack(anchor='w', padx=14, pady=(0, 6))

        self.x1_var = array_input("x\u2081[n]  →  Signal 1", "4, 7, 2",    COLORS['x1'])
        self.x2_var = array_input("x\u2082[n]  →  Signal 2", "2, 3, 7",    COLORS['x2'])

        sep("  Starting Index")
        nf = tk.Frame(parent, bg=PANEL); nf.pack(fill='x', padx=12, pady=(0, 8))
        tk.Label(nf, text="n starts at:", font=('Consolas', 9), bg=PANEL, fg=FG).pack(side='left')
        self.n0_var = tk.StringVar(value="0")
        tk.Entry(nf, textvariable=self.n0_var, font=('Consolas', 10),
                 bg=ENTRY_BG, fg=FG, insertbackground=ACCENT,
                 relief='flat', width=6, bd=4).pack(side='left', padx=8)

        sep("  Actions")
        btn = dict(font=('Consolas', 10, 'bold'), relief='flat', bd=0,
                   pady=8, cursor='hand2')
        tk.Button(parent, text="\u25b6  COMPUTE & PLOT",
                  bg=ACCENT, fg='white', activebackground='#2a4bc9',
                  activeforeground='white', command=self._update, **btn).pack(fill='x', padx=12, pady=3)
        tk.Button(parent, text="\U0001f4be  SAVE PLOT",
                  bg='#1565C0', fg='white', activebackground='#0d47a1',
                  activeforeground='white', command=self._save, **btn).pack(fill='x', padx=12, pady=3)
        tk.Button(parent, text="\U0001f504  RESET",
                  bg='#2e7d32', fg='white', activebackground='#1b5e20',
                  activeforeground='white', command=self._reset, **btn).pack(fill='x', padx=12, pady=3)

        # ── Value matrix ──────────────────────────────────────
        sep("  Value Matrix")
        self.matrix = tk.Text(parent, font=('Consolas', 9),
                              bg='#eef1f7', fg='#1a1a2e',
                              relief='flat', height=18)
        self.matrix.pack(padx=12, pady=4, fill='x')

    # ── Canvas ────────────────────────────────────────────────
    def _build_canvas(self, parent):
        self.fig = Figure(figsize=(11, 10), dpi=95, facecolor=BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    # ── Update ────────────────────────────────────────────────
    def _update(self, *_):
        try:
            x1 = parse_array(self.x1_var.get())
            x2 = parse_array(self.x2_var.get())
            n0 = int(self.n0_var.get())
        except Exception:
            messagebox.showerror("Input Error",
                "Could not parse inputs.\n\n"
                "Format: comma-separated numbers, e.g.   4, 7, 2\n"
                "n start: an integer, e.g.  0")
            return

        x1, x2 = pad_to_same(x1, x2)
        N  = len(x1)
        n  = np.arange(n0, n0 + N)

        add = x1 + x2
        sub = x1 - x2
        mul = x1 * x2

        # ── Draw 5 subplots ───────────────────────────────────
        self.fig.clear()
        self.fig.patch.set_facecolor(BG)
        axes = self.fig.subplots(5, 1)

        self.fig.suptitle(
            f"Discrete Signal Operations    x\u2081={list(x1.astype(int) if all(v==int(v) for v in x1) else x1)}    "
            f"x\u2082={list(x2.astype(int) if all(v==int(v) for v in x2) else x2)}",
            color=FG, fontsize=11, fontweight='bold', y=0.995)

        draw_stem(axes[0], n, x1,  COLORS['x1'],  f"x\u2081[n]  =  {fmt(x1)}")
        draw_stem(axes[1], n, x2,  COLORS['x2'],  f"x\u2082[n]  =  {fmt(x2)}")
        draw_stem(axes[2], n, add, COLORS['add'], f"x\u2081[n] + x\u2082[n]  =  {fmt(add)}")
        draw_stem(axes[3], n, sub, COLORS['sub'], f"x\u2081[n] \u2212 x\u2082[n]  =  {fmt(sub)}")
        draw_stem(axes[4], n, mul, COLORS['mul'], f"x\u2081[n] \u00d7 x\u2082[n]  =  {fmt(mul)}")

        self.fig.tight_layout(rect=[0, 0, 1, 0.97])
        self.canvas.draw()

        # ── Update matrix ─────────────────────────────────────
        self.matrix.config(state='normal')
        self.matrix.delete('1.0', 'end')
        hdr = f"{'n':>4} | {'x1[n]':>8} | {'x2[n]':>8} | {'ADD':>8} | {'SUB':>8} | {'MUL':>8}\n"
        self.matrix.insert('end', hdr)
        self.matrix.insert('end', '-' * 58 + '\n')
        for i, ni in enumerate(n):
            row = (f"{int(ni):>4} | {x1[i]:>8.3g} | {x2[i]:>8.3g} | "
                   f"{add[i]:>8.3g} | {sub[i]:>8.3g} | {mul[i]:>8.3g}\n")
            self.matrix.insert('end', row)
        self.matrix.config(state='disabled')

    # ── Save ──────────────────────────────────────────────────
    def _save(self):
        path = os.path.join(OUTPUT_DIR, "discrete_array_operations.png")
        self.fig.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
        messagebox.showinfo("Saved", f"Plot saved to:\n{path}")

    # ── Reset ─────────────────────────────────────────────────
    def _reset(self):
        self.x1_var.set("4, 7, 2")
        self.x2_var.set("2, 3, 7")
        self.n0_var.set("0")
        self._update()


def fmt(arr):
    """Format array as [4 7 2] style."""
    vals = [f"{v:g}" for v in arr]
    return "[" + "  ".join(vals) + "]"


# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    root = tk.Tk()
    DiscreteArrayApp(root)
    root.mainloop()
