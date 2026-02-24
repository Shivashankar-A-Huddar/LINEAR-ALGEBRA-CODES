"""
Kirchhoff's Laws Interactive Simulator
========================================
Tab 1 → KVL  : Series Circuit Diagram + Voltage Elevation Map
Tab 2 → KCL  : Fluid Junction Balancer (node current equilibrium)

White theme · Matplotlib + Tkinter
"""

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Rectangle
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
from matplotlib.gridspec import GridSpec
import tkinter as tk
from tkinter import ttk
import os

# ── White Theme Palette ───────────────────────────────────────
BG        = '#f5f7fa'
PANEL     = '#ffffff'
ENTRY_BG  = '#eef1f7'
FG        = '#1a1a2e'
ACCENT    = '#3a5bd9'
ACCENT2   = '#e65c00'
GRIDCLR   = '#dde3f5'
SUBPANEL  = '#f0f3fb'

COLORS = {
    'source':  '#3a5bd9',
    'r1':      '#e65100',
    'r2':      '#2e7d32',
    'r3':      '#6a1b9a',
    'wire':    '#1a1a2e',
    'node':    '#ff6f00',
    'current': '#e53935',
    'kcl_in':  '#1565C0',
    'kcl_out': '#C62828',
    'zero':    '#aaaacc',
}

SLIDER_W = 255

# ══════════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════════
def styled_slider(parent, label, from_, to, default, color, resolution=0.5):
    frame = tk.Frame(parent, bg=PANEL)
    frame.pack(fill='x', padx=14, pady=2)
    var = tk.DoubleVar(value=default)
    top = tk.Frame(frame, bg=PANEL)
    top.pack(fill='x')
    tk.Label(top, text=label, font=('Consolas', 9, 'bold'),
             bg=PANEL, fg=color, anchor='w').pack(side='left')
    val_lbl = tk.Label(top, text=f"{default:.1f}", font=('Consolas', 9),
                       bg=PANEL, fg=FG, width=7, anchor='e')
    val_lbl.pack(side='right')

    def fmt_val(*_):
        val_lbl.config(text=f"{var.get():.1f}")
    var.trace_add('write', fmt_val)

    tk.Scale(frame, variable=var, from_=from_, to=to,
             orient='horizontal', resolution=resolution,
             bg=PANEL, fg=FG, highlightthickness=0,
             troughcolor=ENTRY_BG, activebackground=color,
             sliderrelief='flat', width=11,
             length=SLIDER_W, showvalue=False).pack(fill='x')
    return var


def sep(parent, text, color=ACCENT):
    tk.Label(parent, text=text, font=('Consolas', 10, 'bold'),
             bg=PANEL, fg=color).pack(anchor='w', padx=12, pady=(11, 0))
    tk.Frame(parent, bg=color, height=1).pack(fill='x', padx=12, pady=(2, 3))


def ax_style(ax, title='', xlabel='', ylabel='', title_color=FG, grid=True):
    ax.set_facecolor('#ffffff')
    for sp in ax.spines.values():
        sp.set_edgecolor(GRIDCLR)
    ax.tick_params(colors=FG, labelsize=8)
    if grid:
        ax.grid(True, color=GRIDCLR, linewidth=0.8)
    ax.set_title(title, color=title_color, fontsize=9,
                 fontfamily='monospace', pad=5, fontweight='bold')
    ax.set_xlabel(xlabel, color='#555577', fontsize=8)
    ax.set_ylabel(ylabel, color=FG, fontsize=8)


# ══════════════════════════════════════════════════════════════
#  Circuit Drawing Primitives
# ══════════════════════════════════════════════════════════════
def draw_wire(ax, x0, y0, x1, y1, color=COLORS['wire'], lw=2.5):
    ax.plot([x0, x1], [y0, y1], color=color, linewidth=lw,
            solid_capstyle='round', zorder=2)


def draw_node(ax, x, y, color='#333355', r=0.04):
    c = Circle((x, y), r, color=color, zorder=8)
    ax.add_patch(c)


def draw_current_arrow(ax, x, y, dx, dy, color=COLORS['current'], label=''):
    """Draw a current-direction arrow along a wire."""
    ax.annotate('', xy=(x + dx, y + dy), xytext=(x, y),
                arrowprops=dict(arrowstyle='->', color=color,
                                lw=2.2, mutation_scale=16))
    if label:
        ax.text(x + dx/2, y + dy/2 + 0.10, label,
                ha='center', va='bottom', fontsize=8,
                color=color, fontfamily='monospace', fontweight='bold')


def draw_battery(ax, x, y, height=0.55, color=COLORS['source'], Vs=12):
    """Vertical battery: long line = +, short line = –"""
    # Body lines
    half_l = 0.22   # long (+)
    half_s = 0.13   # short (–)
    gap    = 0.10

    # Long line (top = + terminal)
    ax.plot([x - half_l, x + half_l], [y + gap, y + gap],
            color=color, linewidth=4, solid_capstyle='butt', zorder=6)
    # Short line (bottom = – terminal)
    ax.plot([x - half_s, x + half_s], [y - gap, y - gap],
            color=color, linewidth=2.5, solid_capstyle='butt', zorder=6)

    # Wire stubs
    ax.plot([x, x], [y + gap, y + height/2], color=COLORS['wire'], lw=2.5, zorder=5)
    ax.plot([x, x], [y - gap, y - height/2], color=COLORS['wire'], lw=2.5, zorder=5)

    # Labels
    ax.text(x + 0.16, y + gap + 0.06, '+', fontsize=13, color=color,
            fontweight='bold', ha='left', va='center', zorder=7)
    ax.text(x + 0.16, y - gap - 0.04, '−', fontsize=13, color=color,
            fontweight='bold', ha='left', va='center', zorder=7)
    ax.text(x, y - height/2 - 0.18,
            f"Vs = {Vs:.1f} V", ha='center', va='top',
            fontsize=8.5, fontfamily='monospace', fontweight='bold',
            color=color, zorder=7,
            bbox=dict(boxstyle='round,pad=0.25', fc='white', ec=color, lw=1.2))


def draw_resistor(ax, cx, cy, orientation='h', color='#333355',
                  label='R', value=100.0, voltage=0.0):
    """
    Draw a resistor as a rectangle with zigzag fill hint.
    orientation: 'h' = horizontal (top/bottom of loop)
                 'v' = vertical (left/right of loop)
    """
    rw, rh = (0.38, 0.16) if orientation == 'h' else (0.16, 0.38)

    rect = FancyBboxPatch((cx - rw/2, cy - rh/2), rw, rh,
                          boxstyle='round,pad=0.02',
                          linewidth=2, edgecolor=color,
                          facecolor='white', zorder=6)
    ax.add_patch(rect)

    # Zigzag inside
    if orientation == 'h':
        zx = np.linspace(cx - rw/2 + 0.04, cx + rw/2 - 0.04, 13)
        zy = cy + 0.045 * np.array([0,1,-1,1,-1,1,-1,1,-1,1,-1,1,0])
        ax.plot(zx, zy, color=color, linewidth=1.3, zorder=7)
    else:
        zy = np.linspace(cy - rh/2 + 0.04, cy + rh/2 - 0.04, 13)
        zx = cx + 0.045 * np.array([0,1,-1,1,-1,1,-1,1,-1,1,-1,1,0])
        ax.plot(zx, zy, color=color, linewidth=1.3, zorder=7)

    # Component label (above/below)
    lbl_offset = 0.22 if orientation == 'h' else 0.0
    lbl_x_off  = 0.0  if orientation == 'h' else 0.30
    ax.text(cx + lbl_x_off, cy + lbl_offset,
            f"{label}={value:.0f}Ω",
            ha='center', va='bottom' if orientation == 'h' else 'center',
            fontsize=8, fontfamily='monospace', fontweight='bold',
            color=color, zorder=8)

    # Voltage drop label (below/right)
    v_offset = -0.22 if orientation == 'h' else 0.0
    v_x_off  = 0.0   if orientation == 'h' else -0.30
    vbg = dict(boxstyle='round,pad=0.2', fc=color, ec='none', alpha=0.85)
    ax.text(cx + v_x_off, cy + v_offset,
            f"−{voltage:.2f}V",
            ha='center', va='top' if orientation == 'h' else 'center',
            fontsize=8, fontfamily='monospace', fontweight='bold',
            color='white', zorder=8, bbox=vbg)


def draw_kvl_circuit(ax, Vs, R1, R2, R3, V1, V2, V3, I):
    """
    Draw a full series loop circuit:
        Top:    R1 (left) ─── R2 (right)
        Left:   Vs (battery)
        Right:  R3
        Bottom: wire
    """
    ax.set_facecolor('#ffffff')
    ax.set_xlim(0, 6)
    ax.set_ylim(-0.5, 4.2)
    ax.set_aspect('equal')
    ax.axis('off')

    # ── Corner coordinates ─────────────────────────────────
    # TL = top-left, TR = top-right, BL = bottom-left, BR = bottom-right
    TL = (0.9, 3.4)
    TR = (5.1, 3.4)
    BL = (0.9, 0.7)
    BR = (5.1, 0.7)

    lw = 2.8   # wire width

    # ── Wires ──────────────────────────────────────────────
    # Top: TL → mid1 → mid2 → TR  (split for R1 and R2)
    top_m1 = (2.2, 3.4)   # left of R1
    top_m2 = (2.9, 3.4)   # right of R1 / left of R2
    top_m3 = (3.6, 3.4)   # right of R2
    # Actually place R1 centred at 2.55, R2 centred at 4.05
    r1_cx = (TL[0] + top_m2[0]) / 2 + 0.35   # ~2.3
    r2_cx = (top_m2[0] + TR[0]) / 2           # ~4.0

    draw_wire(ax, TL[0], TL[1], r1_cx - 0.22, TL[1], lw=lw)          # TL→R1 left
    draw_wire(ax, r1_cx + 0.22, TL[1], r2_cx - 0.22, TL[1], lw=lw)  # R1 right→R2 left
    draw_wire(ax, r2_cx + 0.22, TL[1], TR[0], TL[1], lw=lw)          # R2 right→TR

    # Right: TR → BR  (R3 in middle)
    r3_cy = (TR[1] + BR[1]) / 2
    draw_wire(ax, TR[0], TR[1], TR[0], r3_cy + 0.22, lw=lw)
    draw_wire(ax, TR[0], r3_cy - 0.22, TR[0], BR[1], lw=lw)

    # Bottom: BR → BL
    draw_wire(ax, BR[0], BR[1], BL[0], BR[1], lw=lw)

    # Left: BL → battery → TL
    bat_cy = (TL[1] + BL[1]) / 2
    draw_wire(ax, BL[0], BL[1], BL[0], bat_cy - 0.28, lw=lw)
    draw_wire(ax, BL[0], bat_cy + 0.28, BL[0], TL[1], lw=lw)

    # ── Components ─────────────────────────────────────────
    draw_battery(ax, BL[0], bat_cy, height=0.55, Vs=Vs)
    draw_resistor(ax, r1_cx, TL[1], 'h', COLORS['r1'], 'R₁', R1, V1)
    draw_resistor(ax, r2_cx, TL[1], 'h', COLORS['r2'], 'R₂', R2, V2)
    draw_resistor(ax, TR[0], r3_cy,  'v', COLORS['r3'], 'R₃', R3, V3)

    # ── Corner nodes ───────────────────────────────────────
    for pt in [TL, TR, BL, BR]:
        draw_node(ax, pt[0], pt[1], color='#2a2a4a', r=0.06)

    # ── Current arrows ─────────────────────────────────────
    arr_col = COLORS['current']
    i_label = f"I = {I*1000:.2f} mA"

    # Top: left to right
    ax.annotate('', xy=(2.0, TL[1] + 0.22), xytext=(1.4, TL[1] + 0.22),
                arrowprops=dict(arrowstyle='->', color=arr_col, lw=2, mutation_scale=15))
    ax.text(1.7, TL[1] + 0.34, i_label, ha='center', va='bottom',
            fontsize=7.5, fontfamily='monospace', color=arr_col, fontweight='bold')

    # Right: top to bottom
    ax.annotate('', xy=(TR[0] + 0.22, 1.8), xytext=(TR[0] + 0.22, 2.4),
                arrowprops=dict(arrowstyle='->', color=arr_col, lw=2, mutation_scale=15))

    # Bottom: right to left
    ax.annotate('', xy=(2.5, BR[1] - 0.22), xytext=(3.5, BR[1] - 0.22),
                arrowprops=dict(arrowstyle='->', color=arr_col, lw=2, mutation_scale=15))

    # Left: bottom to top (battery charges)
    ax.annotate('', xy=(BL[0] - 0.22, 1.6), xytext=(BL[0] - 0.22, 1.0),
                arrowprops=dict(arrowstyle='->', color=arr_col, lw=2, mutation_scale=15))

    # ── KVL equation overlay ────────────────────────────────
    eq = (f"KVL:  {Vs:.1f} − {V1:.2f} − {V2:.2f} − {V3:.2f} = "
          f"{Vs-V1-V2-V3:.4f} V  ✓")
    ax.text(3.0, -0.22, eq, ha='center', va='top',
            fontsize=9, fontfamily='monospace', fontweight='bold',
            color='#2e7d32',
            bbox=dict(boxstyle='round,pad=0.35', fc='#e8f5e9',
                      ec='#2e7d32', lw=1.5))

    # ── +/- node labels ────────────────────────────────────
    ax.text(TL[0] - 0.15, TL[1] + 0.12, '+', fontsize=11,
            color=COLORS['source'], fontweight='bold', ha='right')
    ax.text(BL[0] - 0.15, BL[1] - 0.08, '−', fontsize=11,
            color=COLORS['source'], fontweight='bold', ha='right')

    # Title
    ax.set_title("Series Circuit — KVL Loop",
                 color=ACCENT, fontsize=10, fontfamily='monospace',
                 fontweight='bold', pad=4)


# ══════════════════════════════════════════════════════════════
#  TAB 1 — KVL
# ══════════════════════════════════════════════════════════════
class KVLTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, bg=BG)
        notebook.add(self.frame, text='  ⚡  KVL — Voltage Elevation  ')
        self._build()

    def _build(self):
        ctrl = tk.Frame(self.frame, bg=PANEL, width=300,
                        highlightbackground=GRIDCLR, highlightthickness=1)
        ctrl.pack(side='left', fill='y', padx=(6, 4), pady=6)
        ctrl.pack_propagate(False)

        right = tk.Frame(self.frame, bg=BG)
        right.pack(side='left', fill='both', expand=True, pady=6, padx=(0, 6))

        # ── Controls ────────────────────────────────────────
        tk.Label(ctrl, text="KVL  ·  Series Loop",
                 font=('Consolas', 13, 'bold'), bg=PANEL, fg=ACCENT
                 ).pack(anchor='w', padx=14, pady=(14, 2))
        tk.Label(ctrl,
                 text="∑V = 0  around any closed loop.\n"
                      "The circuit diagram updates live.\n"
                      "Staircase always lands at 0 V.",
                 font=('Consolas', 8), bg=PANEL, fg='#666688',
                 justify='left').pack(anchor='w', padx=14, pady=(0, 8))

        sep(ctrl, "  Voltage Source", COLORS['source'])
        self.vs = styled_slider(ctrl, "Vs  (V)", 1, 30, 12.0, COLORS['source'], 0.5)

        sep(ctrl, "  Resistors (Ω)", FG)
        self.r1 = styled_slider(ctrl, "R₁  (Ω)", 10, 500, 100.0, COLORS['r1'], 5)
        self.r2 = styled_slider(ctrl, "R₂  (Ω)", 10, 500, 200.0, COLORS['r2'], 5)
        self.r3 = styled_slider(ctrl, "R₃  (Ω)", 10, 500, 150.0, COLORS['r3'], 5)

        sep(ctrl, "  Live Results", COLORS['source'])
        self.info = tk.Text(ctrl, font=('Consolas', 9), bg=SUBPANEL,
                            fg=FG, relief='flat', height=11, state='disabled')
        self.info.pack(padx=12, pady=4, fill='x')

        tk.Label(ctrl, text="⚠  KVL Check:",
                 font=('Consolas', 9, 'bold'), bg=PANEL, fg=ACCENT2
                 ).pack(anchor='w', padx=14, pady=(8, 0))
        self.kvl_check = tk.Label(ctrl,
                 text="Vs − V₁ − V₂ − V₃ = 0.000 V  ✓",
                 font=('Consolas', 9, 'bold'), bg='#e8f5e9', fg='#2e7d32',
                 relief='flat', padx=8, pady=6, wraplength=270, justify='left')
        self.kvl_check.pack(fill='x', padx=12, pady=4)

        # Color legend
        leg_frame = tk.Frame(ctrl, bg=PANEL)
        leg_frame.pack(fill='x', padx=14, pady=(4, 0))
        for col, lbl in [(COLORS['r1'], 'R₁'), (COLORS['r2'], 'R₂'),
                         (COLORS['r3'], 'R₃'), (COLORS['source'], 'Vs')]:
            tk.Label(leg_frame, text=f"■ {lbl}", font=('Consolas', 8, 'bold'),
                     bg=PANEL, fg=col).pack(side='left', padx=4)

        # ── Canvas ──────────────────────────────────────────
        self.fig = Figure(figsize=(10, 7.5), dpi=95, facecolor=BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        for v in (self.vs, self.r1, self.r2, self.r3):
            v.trace_add('write', lambda *_: self._update())

        self._update()

    def _update(self, *_):
        Vs   = max(self.vs.get(), 0.01)
        R1   = max(self.r1.get(), 1)
        R2   = max(self.r2.get(), 1)
        R3   = max(self.r3.get(), 1)
        Rtot = R1 + R2 + R3
        I    = Vs / Rtot
        V1, V2, V3 = I*R1, I*R2, I*R3
        check = Vs - V1 - V2 - V3

        # ── Sidebar text ────────────────────────────────────
        self.info.config(state='normal')
        self.info.delete('1.0', 'end')
        self.info.insert('end', '\n'.join([
            f"  I      = {I*1000:.3f} mA",
            f"  I      = {I:.5f} A",
            f"",
            f"  V₁ = I·R₁ = {V1:.4f} V",
            f"  V₂ = I·R₂ = {V2:.4f} V",
            f"  V₃ = I·R₃ = {V3:.4f} V",
            f"",
            f"  Rtotal = {Rtot:.1f} Ω",
            f"  Power  = {I*Vs:.4f} W",
            f"  P₁     = {I*V1:.4f} W",
            f"  P₂     = {I*V2:.4f} W",
            f"  P₃     = {I*V3:.4f} W",
        ]))
        self.info.config(state='disabled')

        self.kvl_check.config(
            text=f"  {Vs:.2f} − {V1:.3f} − {V2:.3f} − {V3:.3f} = {check:.5f} V  ✓",
            bg='#e8f5e9', fg='#2e7d32')

        # ── Figure layout ───────────────────────────────────
        self.fig.clear()
        self.fig.patch.set_facecolor(BG)

        gs = GridSpec(2, 3, figure=self.fig,
                      hspace=0.50, wspace=0.38,
                      left=0.05, right=0.98, top=0.93, bottom=0.07)

        # ── [0, 0:2]  Circuit diagram ─────────────────────
        ax_ckt = self.fig.add_subplot(gs[0, 0:2])
        draw_kvl_circuit(ax_ckt, Vs, R1, R2, R3, V1, V2, V3, I)

        # ── [0, 2]    Voltage drop bar ────────────────────
        ax_bar = self.fig.add_subplot(gs[0, 2])
        ax_style(ax_bar, title="Voltage Drops", ylabel="Voltage (V)",
                 title_color=FG)
        bar_labels = ['Vs', 'V₁\n(R₁)', 'V₂\n(R₂)', 'V₃\n(R₃)']
        bar_vals   = [Vs, V1, V2, V3]
        bar_cols   = [COLORS['source'], COLORS['r1'], COLORS['r2'], COLORS['r3']]
        bars = ax_bar.bar(bar_labels, bar_vals, color=bar_cols,
                          edgecolor='white', linewidth=1.5, width=0.55)
        for bar, v in zip(bars, bar_vals):
            ax_bar.text(bar.get_x() + bar.get_width()/2,
                        bar.get_height() + 0.18, f"{v:.2f}V",
                        ha='center', va='bottom', fontsize=8,
                        fontfamily='monospace', fontweight='bold', color=FG)
        ax_bar.set_ylim(0, Vs * 1.30)
        ax_bar.tick_params(axis='x', labelsize=8)

        # ── [1, 0:2]  KVL Elevation staircase ────────────
        ax_elev = self.fig.add_subplot(gs[1, 0:2])
        ax_style(ax_elev,
                 title=f"KVL Elevation Map  —  Vs={Vs:.1f}V  I={I*1000:.2f}mA",
                 xlabel="Position around the loop →",
                 ylabel="Electrical Potential (V)",
                 title_color=COLORS['source'])

        seg_lens = [0.5, 1.0, 0.5, 1.5, 0.3, 1.5, 0.3, 1.5, 0.5]
        seg_labs = ['', 'Battery\n+Vs', '', f'R₁\n−{V1:.2f}V', '',
                    f'R₂\n−{V2:.2f}V', '', f'R₃\n−{V3:.2f}V', '']
        seg_cols = [COLORS['zero'], COLORS['source'], COLORS['zero'],
                    COLORS['r1'], COLORS['zero'],
                    COLORS['r2'], COLORS['zero'],
                    COLORS['r3'], COLORS['zero']]
        deltas = [0, +Vs, 0, -V1, 0, -V2, 0, -V3, 0]

        x_pts, y_pts = [0.0], [0.0]
        cur_x, cur_y = 0.0, 0.0
        for sl, dy in zip(seg_lens, deltas):
            if dy != 0:
                x_pts.append(cur_x); y_pts.append(cur_y + dy)
                cur_y += dy
            cur_x += sl
            x_pts.append(cur_x); y_pts.append(cur_y)

        ax_elev.plot(x_pts, y_pts, color=COLORS['source'], linewidth=2.5,
                     drawstyle='steps-post', zorder=3, solid_capstyle='round')
        ax_elev.fill_between(x_pts, y_pts, alpha=0.08,
                             color=COLORS['source'], step='post')

        seg_bx = 0.0
        for sl, lab, col in zip(seg_lens, seg_labs, seg_cols):
            if lab:
                ax_elev.axvspan(seg_bx, seg_bx + sl, alpha=0.07,
                                color=col, zorder=1)
                ax_elev.text(seg_bx + sl/2, -Vs * 0.20, lab,
                             ha='center', va='top', fontsize=7.5,
                             color=col, fontfamily='monospace', fontweight='bold')
            seg_bx += sl

        ax_elev.axhline(0, color=COLORS['zero'], linewidth=1.2,
                        linestyle='--', zorder=2)
        ax_elev.text(x_pts[-1] + 0.05, 0.3, '0 V',
                     color=COLORS['zero'], fontsize=8, fontfamily='monospace')
        ax_elev.text(x_pts[-1] + 0.05, Vs + 0.3, f'{Vs:.1f} V',
                     color=COLORS['source'], fontsize=8, fontfamily='monospace')
        ax_elev.set_ylim(-Vs * 0.38, Vs * 1.38)
        ax_elev.set_xlim(-0.1, x_pts[-1] + 0.5)
        ax_elev.set_xticks([])

        # ── [1, 2]   Resistance pie ────────────────────────
        ax_pie = self.fig.add_subplot(gs[1, 2])
        ax_pie.set_facecolor('#ffffff')
        ax_pie.set_title("Resistance Split", color=FG,
                         fontsize=9, fontfamily='monospace',
                         fontweight='bold', pad=5)
        wedges, texts, autos = ax_pie.pie(
            [R1, R2, R3],
            labels=['R₁', 'R₂', 'R₃'],
            colors=[COLORS['r1'], COLORS['r2'], COLORS['r3']],
            autopct=lambda p: f"{p:.1f}%\n{p*Rtot/100:.0f}Ω",
            startangle=140,
            textprops=dict(fontsize=8, color=FG, fontfamily='monospace'),
            wedgeprops=dict(edgecolor='white', linewidth=2.5))
        for at in autos:
            at.set_fontsize(7.5); at.set_color('white'); at.set_fontweight('bold')

        self.fig.suptitle(
            "Kirchhoff's Voltage Law  (KVL)  —  ∑V = 0  around any closed loop",
            color=FG, fontsize=11, fontweight='bold')

        self.canvas.draw()


# ══════════════════════════════════════════════════════════════
#  TAB 2 — KCL Fluid Junction  (unchanged)
# ══════════════════════════════════════════════════════════════
class KCLTab:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook, bg=BG)
        notebook.add(self.frame, text='  🔵  KCL — Current Junction  ')
        self._build()

    def _build(self):
        ctrl = tk.Frame(self.frame, bg=PANEL, width=310,
                        highlightbackground=GRIDCLR, highlightthickness=1)
        ctrl.pack(side='left', fill='y', padx=(6, 4), pady=6)
        ctrl.pack_propagate(False)

        right = tk.Frame(self.frame, bg=BG)
        right.pack(side='left', fill='both', expand=True, pady=6, padx=(0, 6))

        tk.Label(ctrl, text="KCL  ·  Node Junction",
                 font=('Consolas', 13, 'bold'), bg=PANEL, fg=ACCENT
                 ).pack(anchor='w', padx=14, pady=(14, 2))
        tk.Label(ctrl,
                 text="∑I_in = ∑I_out  at every node.\n"
                      "Three branches connect to a\n"
                      "central node. Arrows show flow.",
                 font=('Consolas', 8), bg=PANEL, fg='#666688',
                 justify='left').pack(anchor='w', padx=14, pady=(0, 8))

        sep(ctrl, "  Branch Voltages (V)", COLORS['source'])
        self.v1 = styled_slider(ctrl, "V₁  (V)", -20, 20,  12.0, COLORS['r1'], 0.5)
        self.v2 = styled_slider(ctrl, "V₂  (V)", -20, 20,  -6.0, COLORS['r2'], 0.5)
        self.v3 = styled_slider(ctrl, "V₃  (V)", -20, 20,   8.0, COLORS['r3'], 0.5)

        sep(ctrl, "  Branch Resistances (Ω)", FG)
        self.r1 = styled_slider(ctrl, "R₁  (Ω)", 10, 500, 100.0, COLORS['r1'], 5)
        self.r2 = styled_slider(ctrl, "R₂  (Ω)", 10, 500, 200.0, COLORS['r2'], 5)
        self.r3 = styled_slider(ctrl, "R₃  (Ω)", 10, 500, 150.0, COLORS['r3'], 5)

        sep(ctrl, "  Live Results", COLORS['source'])
        self.info = tk.Text(ctrl, font=('Consolas', 9), bg=SUBPANEL,
                            fg=FG, relief='flat', height=10, state='disabled')
        self.info.pack(padx=12, pady=4, fill='x')

        self.kcl_check = tk.Label(ctrl,
                 text="  ∑I_in − ∑I_out = 0.000 A  ✓",
                 font=('Consolas', 9, 'bold'), bg='#e8f5e9', fg='#2e7d32',
                 relief='flat', padx=8, pady=6)
        self.kcl_check.pack(fill='x', padx=12, pady=4)

        self.fig = Figure(figsize=(9, 7), dpi=95, facecolor=BG)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        for v in (self.v1, self.v2, self.v3, self.r1, self.r2, self.r3):
            v.trace_add('write', lambda *_: self._update())

        self._update()

    def _update(self, *_):
        V1 = self.v1.get(); V2 = self.v2.get(); V3 = self.v3.get()
        R1 = max(self.r1.get(), 1)
        R2 = max(self.r2.get(), 1)
        R3 = max(self.r3.get(), 1)

        G1, G2, G3 = 1/R1, 1/R2, 1/R3
        Vn = (G1*V1 + G2*V2 + G3*V3) / (G1 + G2 + G3)
        I1 = (V1 - Vn) / R1
        I2 = (V2 - Vn) / R2
        I3 = (V3 - Vn) / R3

        currents = [I1, I2, I3]
        I_in  = sum(i for i in currents if i > 0)
        I_out = sum(abs(i) for i in currents if i < 0)
        check = I_in - I_out

        self.info.config(state='normal')
        self.info.delete('1.0', 'end')
        dirs = ['→ IN' if i > 0 else '← OUT' if i < 0 else '  0  ' for i in currents]
        self.info.insert('end', '\n'.join([
            f"  Node Vn = {Vn:.4f} V",
            f"",
            f"  I₁ = {I1:+.4f} A  {dirs[0]}",
            f"  I₂ = {I2:+.4f} A  {dirs[1]}",
            f"  I₃ = {I3:+.4f} A  {dirs[2]}",
            f"",
            f"  ΣI_in  = {I_in:.4f} A",
            f"  ΣI_out = {I_out:.4f} A",
        ]))
        self.info.config(state='disabled')
        self.kcl_check.config(
            text=f"  ΣI_in − ΣI_out = {check:+.6f} A  ✓",
            bg='#e8f5e9', fg='#2e7d32')

        self.fig.clear()
        self.fig.patch.set_facecolor(BG)
        gs = GridSpec(1, 2, figure=self.fig,
                      left=0.04, right=0.97, top=0.90, bottom=0.06, wspace=0.25)

        # ── Junction diagram ─────────────────────────────────
        ax = self.fig.add_subplot(gs[0, 0])
        ax.set_facecolor('#ffffff')
        ax.set_xlim(-2.8, 2.8); ax.set_ylim(-2.8, 2.8)
        ax.set_aspect('equal'); ax.axis('off')
        ax.set_title("KCL Node Junction Diagram",
                     color=ACCENT, fontsize=10, fontfamily='monospace',
                     fontweight='bold', pad=6)

        angles = [90, 210, 330]
        branch_colors = [COLORS['r1'], COLORS['r2'], COLORS['r3']]
        bVs = [V1, V2, V3]
        bIs = [I1, I2, I3]
        bRs = [R1, R2, R3]
        bLs = ['1', '2', '3']

        for ang, col, Vi, Ii, Ri, bl in zip(angles, branch_colors, bVs, bIs, bRs, bLs):
            rad = np.radians(ang)
            ex = 2.3 * np.cos(rad); ey = 2.3 * np.sin(rad)
            ax.plot([0, ex], [0, ey], color=col,
                    linewidth=max(1.5, abs(Ii)*80), alpha=0.85,
                    solid_capstyle='round', zorder=2)

            if abs(Ii) > 1e-6:
                asc = 0.55
                if Ii > 0:
                    dx = -np.cos(rad)*asc; dy = -np.sin(rad)*asc
                    ax_p, ay_p = ex, ey
                else:
                    dx = np.cos(rad)*asc; dy = np.sin(rad)*asc
                    ax_p = ex - np.cos(rad)*asc*0.3
                    ay_p = ey - np.sin(rad)*asc*0.3
                arr_col = COLORS['kcl_in'] if Ii > 0 else COLORS['kcl_out']
                ax.annotate('', xy=(ax_p+dx*0.6, ay_p+dy*0.6),
                            xytext=(ax_p, ay_p),
                            arrowprops=dict(arrowstyle='->',color=arr_col,
                                            lw=2.5+abs(Ii)*40,mutation_scale=22))

            mx = ex*0.60; my = ey*0.60
            ax.text(mx, my, f"R{bl}={Ri:.0f}Ω\n{abs(Ii)*1000:.1f}mA",
                    ha='center', va='center', fontsize=7.5,
                    fontfamily='monospace', fontweight='bold', color=col,
                    bbox=dict(boxstyle='round,pad=0.35', fc=SUBPANEL,
                              ec=col, lw=1.5, alpha=0.95), zorder=5)
            ax.text(ex*1.05, ey*1.05, f"V={Vi:.1f}V",
                    ha='center', va='center', fontsize=8,
                    fontfamily='monospace', fontweight='bold', color='white',
                    bbox=dict(boxstyle='round,pad=0.3', fc=col, ec='none',
                              alpha=0.85), zorder=5)

        nc = Circle((0,0), 0.22, color=COLORS['node'], zorder=10,
                    linewidth=2, ec='white')
        ax.add_patch(nc)
        ax.text(0, -0.5, f"Vn={Vn:.2f}V", ha='center', va='top',
                fontsize=8, fontfamily='monospace', fontweight='bold',
                color=COLORS['node'],
                bbox=dict(boxstyle='round,pad=0.25', fc='white',
                          ec=COLORS['node'], lw=1.2))
        ax.legend(handles=[
            mpatches.Patch(color=COLORS['kcl_in'],  label='Current IN'),
            mpatches.Patch(color=COLORS['kcl_out'], label='Current OUT')],
            loc='lower right', fontsize=8, framealpha=0.85,
            prop={'family':'monospace','size':8})

        # ── Balance bar ──────────────────────────────────────
        ax2 = self.fig.add_subplot(gs[0, 1])
        ax_style(ax2, title="KCL Balance — ∑I_in = ∑I_out",
                 ylabel="Current  (A)", title_color=ACCENT)

        i_vals = [I1, I2, I3]
        r_cols = [COLORS['r1'], COLORS['r2'], COLORS['r3']]
        r_labs = ['I₁', 'I₂', 'I₃']
        in_vals  = [max(i,0) for i in i_vals]
        out_vals = [abs(min(i,0)) for i in i_vals]
        x_in, x_out = 0.4, 1.6

        bottom_in = 0.0
        for v, col, lab in zip(in_vals, r_cols, r_labs):
            if v > 1e-9:
                ax2.bar(x_in, v, bottom=bottom_in, color=col, width=0.55,
                        edgecolor='white', linewidth=1.2, alpha=0.88)
                ax2.text(x_in, bottom_in + v/2, f"{lab}\n{v*1000:.1f}mA",
                         ha='center', va='center', fontsize=8,
                         fontfamily='monospace', fontweight='bold', color='white')
                bottom_in += v

        bottom_out = 0.0
        for v, col, lab in zip(out_vals, r_cols, r_labs):
            if v > 1e-9:
                ax2.bar(x_out, v, bottom=bottom_out, color=col, width=0.55,
                        edgecolor='white', linewidth=1.2, alpha=0.55, hatch='////')
                ax2.text(x_out, bottom_out + v/2, f"{lab}\n{v*1000:.1f}mA",
                         ha='center', va='center', fontsize=8,
                         fontfamily='monospace', fontweight='bold', color=col)
                bottom_out += v

        max_val = max(bottom_in, bottom_out, 0.001)
        ax2.set_ylim(0, max_val * 1.35)
        ax2.set_xlim(0, 2)
        ax2.set_xticks([x_in, x_out])
        ax2.set_xticklabels([f"IN\n{I_in*1000:.2f}mA",
                              f"OUT\n{I_out*1000:.2f}mA"],
                             fontsize=9, fontfamily='monospace', fontweight='bold')
        ax2.axhline(max(bottom_in, bottom_out), color=ACCENT2,
                    linewidth=2, linestyle='--', alpha=0.7)
        ax2.text(1.0, max_val*1.22,
                 "⚖  BALANCED  ⚖" if abs(check) < 1e-9 else f"Δ={check:.5f}A",
                 ha='center', fontsize=9, fontfamily='monospace', fontweight='bold',
                 color='#2e7d32' if abs(check) < 1e-6 else '#c62828')
        if max(bottom_in, bottom_out) > 1e-9:
            ax2.annotate('',
                         xy=(x_out-0.3, max(bottom_in, bottom_out)*0.5),
                         xytext=(x_in+0.3, max(bottom_in, bottom_out)*0.5),
                         arrowprops=dict(arrowstyle='<->', color=ACCENT,
                                         lw=2, mutation_scale=18))
            ax2.text(1.0, max(bottom_in, bottom_out)*0.5 + max_val*0.04,
                     "=", ha='center', va='bottom', fontsize=18,
                     color=ACCENT, fontweight='bold')

        self.fig.suptitle(
            "Kirchhoff's Current Law  (KCL)  —  ∑I_in = ∑I_out  at every node",
            color=FG, fontsize=11, fontweight='bold')
        self.canvas.draw()


# ══════════════════════════════════════════════════════════════
#  Main App
# ══════════════════════════════════════════════════════════════
class KirchhoffApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kirchhoff's Laws Interactive Simulator")
        self.root.configure(bg=BG)
        self.root.state('zoomed')
        self._build()

    def _build(self):
        tk.Frame(self.root, bg=ACCENT, height=5).pack(fill='x')

        hdr = tk.Frame(self.root, bg=BG, pady=8)
        hdr.pack(fill='x')
        tk.Label(hdr, text="⚡  Kirchhoff's Laws Simulator",
                 font=('Consolas', 16, 'bold'), bg=BG, fg=ACCENT
                 ).pack(side='left', padx=20)
        tk.Label(hdr,
                 text="KVL: ∑V = 0  around any loop   ·   KCL: ∑I_in = ∑I_out  at every node",
                 font=('Consolas', 9), bg=BG, fg='#6670aa'
                 ).pack(side='left', padx=6)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=BG, borderwidth=0)
        style.configure('TNotebook.Tab', background=ENTRY_BG, foreground=FG,
                        font=('Consolas', 10, 'bold'), padding=[14, 6])
        style.map('TNotebook.Tab',
                  background=[('selected', PANEL)],
                  foreground=[('selected', ACCENT)])

        notebook = ttk.Notebook(self.root, style='TNotebook')
        notebook.pack(fill='both', expand=True, padx=6, pady=(0, 6))

        KVLTab(notebook)
        KCLTab(notebook)


# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    root = tk.Tk()
    KirchhoffApp(root)
    root.mainloop()
