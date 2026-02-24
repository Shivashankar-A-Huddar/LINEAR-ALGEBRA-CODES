import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Button
import tkinter as tk

# ══════════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════════
SCALAR_DATA = {
    "Charge":        {"value": 1.0,   "unit": "uC",   "symbol": "Q", "range": (-100, 100)},
    "Voltage (DC)":  {"value": 5.0,   "unit": "V",    "symbol": "V", "range": (-20, 20)},
    "Current (DC)":  {"value": 2.3,   "unit": "A",    "symbol": "I", "range": (-10, 10)},
    "Resistance":    {"value": 10.0,  "unit": "Ohm",  "symbol": "R", "range": (0, 1000)},
    "Power":         {"value": 50.0,  "unit": "W",    "symbol": "P", "range": (0, 500)},
    "Energy":        {"value": 120.0, "unit": "J",    "symbol": "E", "range": (0, 1000)},
    "Frequency":     {"value": 2.4,   "unit": "GHz",  "symbol": "f", "range": (0, 100)},
    "Temperature":   {"value": 85.0,  "unit": "degC", "symbol": "T", "range": (-50, 200)},
    "Capacitance":   {"value": 100.0, "unit": "pF",   "symbol": "C", "range": (0, 10000)},
}
VECTOR_DATA = {
    "Electric Field E":   {"x": 3.0,  "y": 2.0,  "unit": "V/m",   "symbol": "E"},
    "Magnetic Field B":   {"x": 1.5,  "y": 2.5,  "unit": "T",     "symbol": "B"},
    "Force F":            {"x": 4.0,  "y": 1.0,  "unit": "N",     "symbol": "F"},
    "Poynting Vector S":  {"x": 2.0,  "y": 3.5,  "unit": "W/m2",  "symbol": "S"},
    "Wave Propagation k": {"x": 3.5,  "y": -1.5, "unit": "rad/m", "symbol": "k"},
    "Antenna Radiation":  {"x": -2.0, "y": 3.0,  "unit": "—",     "symbol": "G"},
    "EM Waves ExB":       {"x": -3.0, "y": -2.0, "unit": "—",     "symbol": "EM"},
    "Current Density J":  {"x": 1.0,  "y": -3.5, "unit": "A/m2",  "symbol": "J"},
    "Flux Density D":     {"x": -1.5, "y": -2.5, "unit": "C/m2",  "symbol": "D"},
}
VEC_COLORS = ["#e63946","#2a9d8f","#e9c46a","#f4a261","#264653",
               "#8338ec","#3a86ff","#fb5607","#06d6a0"]

active_scalar = "Charge"
active_vector = "Electric Field E"
scalar_table_visible = True
vector_table_visible = True

# ══════════════════════════════════════════════════════════════
#  FIGURE  —  3-row layout, QxE panel at centre-bottom
# ══════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(18, 11))
fig.patch.set_facecolor('#f0f2f5')
fig.suptitle("Scalar vs Vector  —  Electronics & Communication Engineering",
             fontsize=14, fontweight='bold', y=0.99)

# Row 1 – number line (left) | vector grid (centre) | [space for tables]
ax_snum    = fig.add_axes([0.03, 0.60, 0.25, 0.26])  # scalar number line
ax_vec     = fig.add_axes([0.31, 0.40, 0.34, 0.52])  # 2D vector grid

# Row 2 – tables (flanks) + QxE panel (centre-bottom, split left/right)
ax_stbl    = fig.add_axes([0.03, 0.04, 0.27, 0.48])  # scalar table
ax_qxe     = fig.add_axes([0.31, 0.04, 0.19, 0.33])  # Q×E arrow diagram  (LEFT half)
ax_qxe_txt = fig.add_axes([0.51, 0.04, 0.14, 0.33])  # Q×E explanation card (RIGHT half)
ax_vtbl    = fig.add_axes([0.68, 0.04, 0.30, 0.88])  # vector table


# ══════════════════════════════════════════════════════════════
#  DRAW  —  Scalar number line
# ══════════════════════════════════════════════════════════════
def draw_scalar_line():
    ax = ax_snum; ax.cla(); ax.set_facecolor('white')
    ds = SCALAR_DATA[active_scalar]
    v = ds["value"]; lo, hi = ds["range"]
    ax.set_title("Scalar  :  " + active_scalar, fontsize=11,
                 fontweight='bold', pad=8, color='#b35c00')
    ax.set_xlim(lo - (hi-lo)*0.1, hi + (hi-lo)*0.1)
    ax.set_ylim(-1.4, 1.4)
    ax.axhline(0, color='#cccccc', linewidth=2.5); ax.set_yticks([])
    ax.tick_params(axis='x', labelsize=8)
    for sp in ['top','right','left']: ax.spines[sp].set_visible(False)
    step = (hi-lo)/8
    for t in np.arange(lo, hi+step, step):
        ax.plot([t,t], [-0.18, 0.18], color='#dddddd', linewidth=1)
    ax.plot([v], [0], 'o', color='#e07b00', markersize=20,
            markeredgecolor='white', markeredgewidth=2.5, zorder=5)
    ax.text(v, 0.45, ds["symbol"]+" = "+str(v)+" "+ds["unit"],
            ha='center', fontsize=11, fontweight='bold', color='#e07b00')
    ax.text((lo+hi)/2, -0.85, 'Magnitude only  —  no direction',
            ha='center', fontsize=9, color='#999999', style='italic')
    ax.text(lo+(hi-lo)*0.01, 1.15, 'Click [Enter Scalar] to select & change',
            fontsize=7.5, color='#bbbbbb')


# ══════════════════════════════════════════════════════════════
#  DRAW  —  Vector grid
# ══════════════════════════════════════════════════════════════
def draw_vector_grid():
    ax = ax_vec; ax.cla(); ax.set_facecolor('white')
    ax.set_xlim(-6,6); ax.set_ylim(-6,6); ax.set_aspect('equal')
    ax.set_title('Vector  —  All Quantities  (active highlighted)',
                 fontsize=11, fontweight='bold', pad=8, color='#0d3b8e')
    ax.set_xticks(range(-5,6,1)); ax.set_yticks(range(-5,6,1))
    ax.tick_params(labelsize=7)
    ax.grid(True, color='#eeeeee', linewidth=0.7)
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)

    for i, (name, dv) in enumerate(VECTOR_DATA.items()):
        vx=dv["x"]; vy=dv["y"]; col=VEC_COLORS[i]; is_a=(name==active_vector)
        lw=3.0 if is_a else 1.2; alp=1.0 if is_a else 0.35; zo=10 if is_a else 3
        ax.annotate('', xy=(vx,vy), xytext=(0,0),
                    arrowprops=dict(arrowstyle='->', color=col, lw=lw,
                                    mutation_scale=18 if is_a else 12, alpha=alp), zorder=zo)
        ax.plot([vx],[vy], 'o', color=col, markersize=7 if is_a else 4, alpha=alp, zorder=zo+1)
        ax.text(vx+0.2, vy+0.2, dv["symbol"],
                fontsize=9 if is_a else 7, color=col,
                fontweight='bold' if is_a else 'normal',
                alpha=1.0 if is_a else 0.5)

    dav = VECTOR_DATA[active_vector]
    vx=dav["x"]; vy=dav["y"]; mag=np.sqrt(vx**2+vy**2)
    col = VEC_COLORS[list(VECTOR_DATA.keys()).index(active_vector)]
    ax.text(-5.8, 5.5,
            active_vector+"\nv = ["+str(round(vx,2))+",  "+str(round(vy,2))+"]  "+dav["unit"]+
            "\n|v| = "+str(round(mag,3)),
            fontsize=8.5, color=col, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#f8f9ff',
                      edgecolor=col, alpha=0.95), zorder=15)
    ax.text(-5.8,-5.8, 'Click [Enter Vector] to select & change',
            fontsize=7.5, color='#bbbbbb')


# ══════════════════════════════════════════════════════════════
#  DRAW  —  Q × E  LEFT: clean arrow diagram
# ══════════════════════════════════════════════════════════════
def draw_qxE():
    ax = ax_qxe
    ax.cla()
    ax.set_facecolor('#ffffff')

    Q_val  = SCALAR_DATA["Charge"]["value"]
    E_data = VECTOR_DATA["Electric Field E"]
    Ex, Ey = E_data["x"], E_data["y"]
    E_mag  = np.sqrt(Ex**2 + Ey**2)
    Q_norm = Q_val / 20.0          # [-100,100] µC  →  [-5,5] display
    Fx, Fy = Q_norm * Ex, Q_norm * Ey
    F_mag  = np.sqrt(Fx**2 + Fy**2)

    LIM = 5.5
    ax.set_xlim(-LIM, LIM); ax.set_ylim(-LIM, LIM)
    ax.set_aspect('equal')
    ax.spines['left'].set_position('zero');   ax.spines['bottom'].set_position('zero')
    ax.spines['top'].set_visible(False);      ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc');   ax.spines['bottom'].set_color('#cccccc')
    ax.set_xticks(range(-5, 6, 1));           ax.set_yticks(range(-5, 6, 1))
    ax.tick_params(labelsize=6, colors='#aaaaaa')
    ax.grid(True, color='#f0f0f0', linewidth=0.5, zorder=0)

    ax.set_title("Q  ×  →E  =  →F", fontsize=10, fontweight='bold',
                 color='#3d1a6e', pad=6)

    # ── →E arrow (blue dashed) ──────────────────────
    ax.annotate('', xy=(Ex, Ey), xytext=(0, 0),
                arrowprops=dict(arrowstyle='-|>', color='#2980b9', lw=2.2,
                                linestyle='dashed', mutation_scale=14), zorder=6)
    # dotted component lines
    ax.plot([0, Ex], [0, 0],   ':', color='#2980b9', lw=1.0, alpha=0.45)
    ax.plot([Ex, Ex], [0, Ey], ':', color='#2980b9', lw=1.0, alpha=0.45)
    # simple tip label only (no bbox clutter)
    ax.text(Ex + 0.25, Ey + 0.20,
            f"→E\n[{Ex:.1f}, {Ey:.1f}]",
            fontsize=7.5, color='#2980b9', fontweight='bold', va='bottom')

    # ── Q dot on the x-axis (orange circle, acts as scalar marker) ──
    q_x = np.clip(Q_norm, -LIM + 0.3, LIM - 0.3)
    ax.plot(q_x, 0, 'o', color='#e07b00', markersize=14,
            markeredgecolor='white', markeredgewidth=2, zorder=9)
    ax.text(q_x, 0.45,
            f"Q={Q_val}µC", ha='center', fontsize=7.5,
            color='#e07b00', fontweight='bold')

    # ── →F arrow (purple thick) ─────────────────────
    if F_mag > 0.01:
        clip = min(1.0, (LIM - 0.4) / F_mag)
        Fdx, Fdy = Fx * clip, Fy * clip
        ax.annotate('', xy=(Fdx, Fdy), xytext=(0, 0),
                    arrowprops=dict(arrowstyle='-|>', color='#8e44ad', lw=3.2,
                                    mutation_scale=18), zorder=10)
        ax.plot(Fdx, Fdy, 'D', color='#8e44ad', markersize=8,
                markeredgecolor='white', markeredgewidth=1.8, zorder=11)
        # label: push to opposite quadrant from E
        tx = np.clip(Fdx * 1.35, -LIM + 1.0, LIM - 1.0)
        ty = np.clip(Fdy * 1.35, -LIM + 1.0, LIM - 1.0)
        ax.text(tx, ty,
                f"→F\n[{Fx:.2f}, {Fy:.2f}]\n|F|={F_mag:.2f}",
                fontsize=7.5, color='#8e44ad', fontweight='bold',
                ha='center', va='center',
                bbox=dict(boxstyle='round,pad=0.28', fc='#f9f0ff',
                          ec='#8e44ad', alpha=0.92, lw=0.9), zorder=12)
    else:
        ax.text(0, 1.2, "→F = 0\n(Q = 0)",
                ha='center', fontsize=9, color='#aaa', style='italic')

    # origin dot
    ax.plot(0, 0, 'o', color='#555', markersize=5, zorder=15)

    # minimal colour legend at bottom
    import matplotlib.lines as mlines
    h1 = mlines.Line2D([], [], color='#2980b9', lw=2, linestyle='--', label='→E  (input vector)')
    h2 = mlines.Line2D([], [], color='#e07b00', marker='o', lw=0, markersize=7, label='Q  (input scalar)')
    h3 = mlines.Line2D([], [], color='#8e44ad', lw=2.5, label='→F  (output vector)')
    ax.legend(handles=[h1, h2, h3], loc='lower right', fontsize=6.5,
              framealpha=0.88, edgecolor='#ccaaee')


# ══════════════════════════════════════════════════════════════
#  DRAW  —  Q × E  RIGHT: clean explanation card
# ══════════════════════════════════════════════════════════════
def draw_qxE_card():
    ax = ax_qxe_txt
    ax.cla()
    ax.axis('off')
    ax.set_facecolor('#fdfbff')

    Q_val  = SCALAR_DATA["Charge"]["value"]
    E_data = VECTOR_DATA["Electric Field E"]
    Ex, Ey = E_data["x"], E_data["y"]
    E_mag  = np.sqrt(Ex**2 + Ey**2)
    Q_norm = Q_val / 20.0
    Fx, Fy = Q_norm * Ex, Q_norm * Ey
    F_mag  = np.sqrt(Fx**2 + Fy**2)

    direction = "Same direction as →E  ✓" if Q_val > 0 else \
                "OPPOSITE direction  (Q < 0)" if Q_val < 0 else "Zero vector  (Q = 0)"
    dir_col   = '#27ae60' if Q_val > 0 else ('#e74c3c' if Q_val < 0 else '#999')
    angle_E   = np.degrees(np.arctan2(Ey, Ex))

    T = ax.transAxes   # shorthand

    # ── Background card ────────────────────────────────────────────
    ax.add_patch(mpatches.FancyBboxPatch((0, 0), 1, 1,
        boxstyle='round,pad=0.02', transform=T,
        facecolor='#fdfbff', edgecolor='#d0b8f0', linewidth=1.2, zorder=0))

    # ── Title band ─────────────────────────────────────────────────
    ax.add_patch(mpatches.FancyBboxPatch((0, 0.88), 1, 0.12,
        boxstyle='square,pad=0', transform=T,
        facecolor='#3d1a6e', edgecolor='none', zorder=1))
    ax.text(0.5, 0.940, "SCALAR × VECTOR", ha='center', va='center',
            fontsize=8.5, fontweight='bold', color='white', transform=T, zorder=2)
    ax.text(0.5, 0.898, "Multiplication Explained", ha='center', va='center',
            fontsize=7, color='#d4b8ff', transform=T, zorder=2, style='italic')

    # ── Formula row ────────────────────────────────────────────────
    y = 0.81
    ax.add_patch(mpatches.FancyBboxPatch((0.02, y - 0.045), 0.96, 0.072,
        boxstyle='round,pad=0.01', transform=T,
        facecolor='#f3eaff', edgecolor='#c9a0f7', linewidth=0.8, zorder=1))
    # Colour each symbol separately
    syms = [("→F",  0.07, '#8e44ad', 'bold', 10),
            ("=",   0.25, '#555555', 'normal', 9),
            ("Q",   0.33, '#e07b00', 'bold', 10),
            ("×",   0.46, '#555555', 'bold',  9),
            ("→E",  0.54, '#2980b9', 'bold', 10)]
    for sym, sx, sc, fw, fs in syms:
        ax.text(sx, y, sym, ha='center', va='center',
                fontsize=fs, color=sc, fontweight=fw, transform=T, zorder=2)

    # Type labels below symbols
    types = [("→F",  0.07, '[vector]', '#8e44ad'),
             ("Q",   0.33, '[scalar]', '#e07b00'),
             ("→E",  0.54, '[vector]', '#2980b9')]
    for _, sx, lbl, lc in types:
        ax.text(sx, y - 0.040, lbl, ha='center', va='center',
                fontsize=6, color=lc, style='italic', transform=T, zorder=2)

    # ── Divider ────────────────────────────────────────────────────
    def hline(y_pos):
        ax.plot([0.04, 0.96], [y_pos, y_pos], '-', color='#e0d0f5',
                lw=0.8, transform=T, zorder=1)

    hline(0.74)

    # ── Input block ────────────────────────────────────────────────
    ax.text(0.05, 0.72, "INPUTS", fontsize=7, fontweight='bold',
            color='#555', transform=T, zorder=2)

    rows_in = [
        (0.67, '#e07b00', f"Q  =  {Q_val} µC",          "Charge  [SCALAR]"),
        (0.61, '#2980b9', f"→E =  [{Ex:.1f}, {Ey:.1f}]", "Electric Field  [VECTOR]"),
        (0.55, '#2980b9', f"|E|=  {E_mag:.2f} V/m",      f"θ = {angle_E:.1f}°"),
    ]
    for ry, rc, rv, rn in rows_in:
        ax.text(0.06, ry, rv, fontsize=7.5, color=rc, fontweight='bold',
                transform=T, zorder=2, fontfamily='monospace')
        ax.text(0.06, ry - 0.048, rn, fontsize=6.5, color='#888',
                transform=T, zorder=2, style='italic')

    hline(0.48)

    # ── Step-by-step ───────────────────────────────────────────────
    ax.text(0.05, 0.46, "CALCULATION", fontsize=7, fontweight='bold',
            color='#555', transform=T, zorder=2)

    steps = [
        (0.41, f"→F  =  Q  ×  →E"),
        (0.35, f"    =  {Q_norm:.3f}  ×  [{Ex}, {Ey}]"),
        (0.29, f"    =  [{Fx:.3f},  {Fy:.3f}]"),
        (0.23, f"|F| =  {F_mag:.3f}  N"),
    ]
    for sy, st in steps:
        ax.text(0.06, sy, st, fontsize=7.2, color='#333',
                transform=T, zorder=2, fontfamily='monospace')

    hline(0.19)

    # ── Output block ───────────────────────────────────────────────
    ax.add_patch(mpatches.FancyBboxPatch((0.02, 0.01), 0.96, 0.17,
        boxstyle='round,pad=0.01', transform=T,
        facecolor='#f5eeff', edgecolor='#8e44ad', linewidth=1.0, zorder=1))
    ax.text(0.5, 0.155, "OUTPUT", ha='center', fontsize=7, fontweight='bold',
            color='#6a0dad', transform=T, zorder=2)
    ax.text(0.5, 0.110,
            f"→F = [{Fx:.3f},  {Fy:.3f}]  N",
            ha='center', fontsize=8, fontweight='bold', color='#8e44ad',
            transform=T, zorder=2, fontfamily='monospace')
    ax.text(0.5, 0.068,
            f"|F| = {F_mag:.3f} N     Type: VECTOR QUANTITY",
            ha='center', fontsize=6.8, color='#6a0dad',
            transform=T, zorder=2)
    ax.text(0.5, 0.030, direction, ha='center', fontsize=7,
            fontweight='bold', color=dir_col, transform=T, zorder=2)


# ══════════════════════════════════════════════════════════════
#  DRAW  —  Scalar Table
# ══════════════════════════════════════════════════════════════
def draw_scalar_table():
    ax = ax_stbl; ax.cla(); ax.axis('off')
    if not scalar_table_visible:
        ax.text(0.5, 0.5, 'Scalar table hidden\n(click  [▼ Scalar Table]  to show)',
                ha='center', va='center', fontsize=10, color='#bbbbbb',
                transform=ax.transAxes, style='italic')
        return
    hdr = mpatches.FancyBboxPatch((0,0.915),1,0.085, boxstyle='square,pad=0',
          transform=ax.transAxes, facecolor='#e07b00', edgecolor='none')
    ax.add_patch(hdr)
    ax.text(0.5,0.955,'Scalar Quantities  —  Electronics', ha='center',
            fontsize=10, fontweight='bold', color='white', transform=ax.transAxes)
    cols=[0.02,0.38,0.58,0.82]; row_h=0.088; y0=0.905
    for j,h in enumerate(['Quantity','Value','Unit','Sym']):
        ax.text(cols[j], y0, h, fontsize=8, fontweight='bold',
                color='#e07b00', transform=ax.transAxes)
    for i,(name,dq) in enumerate(SCALAR_DATA.items()):
        y=y0-(i+1)*row_h; is_a=(name==active_scalar)
        # highlight Charge row always in light purple (it feeds QxE)
        if name == "Charge":
            bg = '#f5eeff' if not is_a else '#e0c8ff'
        else:
            bg = '#fff3e0' if is_a else ('#fff8f0' if i%2==0 else '#ffffff')
        r=mpatches.FancyBboxPatch((0,y-0.012),1,row_h, boxstyle='square,pad=0',
          transform=ax.transAxes, facecolor=bg, edgecolor='none')
        ax.add_patch(r)
        fw='bold' if (is_a or name=="Charge") else 'normal'
        fc='#6a0dad' if name=="Charge" else ('#b35c00' if is_a else '#222222')
        ax.text(cols[0],y,name,           fontsize=8,color=fc,fontweight=fw,transform=ax.transAxes)
        ax.text(cols[1],y,str(dq["value"]),fontsize=8,color='#e07b00',fontweight='bold',transform=ax.transAxes)
        ax.text(cols[2],y,dq["unit"],      fontsize=8,color='#888888',transform=ax.transAxes)
        ax.text(cols[3],y,dq["symbol"],    fontsize=8,color='#555555',transform=ax.transAxes)
    # footnote
    ax.text(0.02, 0.01, "★ Charge (Q) feeds the Q×E graph below",
            fontsize=7, color='#8e44ad', style='italic', transform=ax.transAxes)


# ══════════════════════════════════════════════════════════════
#  DRAW  —  Vector Table
# ══════════════════════════════════════════════════════════════
def draw_vector_table():
    ax = ax_vtbl; ax.cla(); ax.axis('off')
    if not vector_table_visible:
        ax.text(0.5, 0.5, 'Vector table hidden\n(click  [▼ Vector Table]  to show)',
                ha='center', va='center', fontsize=10, color='#bbbbbb',
                transform=ax.transAxes, style='italic')
        return
    hdr = mpatches.FancyBboxPatch((0,0.935),1,0.065, boxstyle='square,pad=0',
          transform=ax.transAxes, facecolor='#1a56db', edgecolor='none')
    ax.add_patch(hdr)
    ax.text(0.5,0.965,'Vector Quantities  —  Electronics & Comm.', ha='center',
            fontsize=10, fontweight='bold', color='white', transform=ax.transAxes)
    cols=[0.02,0.46,0.60,0.74,0.88]; row_h=0.082; y0=0.925
    for j,h in enumerate(['Quantity','x','y','|v|','Unit']):
        ax.text(cols[j],y0,h, fontsize=8, fontweight='bold',
                color='#1a56db', transform=ax.transAxes)
    for i,(name,dv) in enumerate(VECTOR_DATA.items()):
        vx=dv["x"]; vy=dv["y"]; mag=np.sqrt(vx**2+vy**2)
        y=y0-(i+1)*row_h; is_a=(name==active_vector)
        is_E = (name == "Electric Field E")
        if is_E:
            bg = '#f5eeff' if not is_a else '#e0c8ff'
        else:
            bg = '#eef3ff' if is_a else ('#f5f8ff' if i%2==0 else '#ffffff')
        col=VEC_COLORS[i]
        r=mpatches.FancyBboxPatch((0,y-0.010),1,row_h, boxstyle='square,pad=0',
          transform=ax.transAxes, facecolor=bg, edgecolor='none')
        ax.add_patch(r)
        circ=mpatches.Circle((0.015,y+0.022),0.012,
             transform=ax.transAxes, color=col, zorder=5)
        ax.add_patch(circ)
        fw='bold' if (is_a or is_E) else 'normal'
        fc = '#6a0dad' if is_E else col
        ax.text(cols[0]+0.03,y,name,          fontsize=7.8,color=fc,fontweight=fw,transform=ax.transAxes)
        ax.text(cols[1],y,str(round(vx,2)),   fontsize=7.8,color='#1a56db',transform=ax.transAxes)
        ax.text(cols[2],y,str(round(vy,2)),   fontsize=7.8,color='#e02020',transform=ax.transAxes)
        ax.text(cols[3],y,str(round(mag,2)),  fontsize=7.8,color='#333333',fontweight='bold',transform=ax.transAxes)
        ax.text(cols[4],y,dv["unit"],         fontsize=7.5,color='#888888',transform=ax.transAxes)
    ax.text(0.02, 0.01, "★ Electric Field E  feeds the Q×E graph below",
            fontsize=7, color='#8e44ad', style='italic', transform=ax.transAxes)


def redraw_all():
    draw_scalar_line()
    draw_vector_grid()
    draw_scalar_table()
    draw_vector_table()
    draw_qxE()
    draw_qxE_card()
    update_toggle_labels()
    fig.canvas.draw_idle()


# ══════════════════════════════════════════════════════════════
#  POPUP — SCALAR
# ══════════════════════════════════════════════════════════════
def enter_scalar(event):
    global active_scalar
    win = tk.Tk(); win.title("Enter Scalar Value")
    win.configure(bg='#fff8f0'); win.geometry("460x520")
    win.resizable(False,False); win.attributes('-topmost', True)

    tk.Label(win, text="Select Quantity & Enter Value",
             font=("Arial",12,"bold"), fg='#b35c00', bg='#fff8f0').pack(pady=(16,4))
    tk.Label(win, text="★  Changing Charge (Q) updates the Q×E graph in real time.",
             font=("Arial",9,"italic"), fg='#8e44ad', bg='#fff8f0').pack(pady=(0,8))

    frm = tk.Frame(win, bg='#fff8f0'); frm.pack(fill='x', padx=20)
    tk.Label(frm, text="Scalar Quantities:", font=("Arial",9,"bold"),
             fg='#b35c00', bg='#fff8f0').pack(anchor='w')
    lb_frm = tk.Frame(frm, bd=1, relief='solid', bg='white'); lb_frm.pack(fill='x', pady=4)
    sb = tk.Scrollbar(lb_frm, orient='vertical')
    lb = tk.Listbox(lb_frm, height=9, font=("Courier",9),
                     selectbackground='#ffe0b2', selectforeground='#b35c00',
                     yscrollcommand=sb.set, activestyle='none',
                     bg='white', relief='flat', bd=0)
    sb.config(command=lb.yview); sb.pack(side='right', fill='y'); lb.pack(fill='x')

    names = list(SCALAR_DATA.keys())
    for i, nm in enumerate(names):
        d = SCALAR_DATA[nm]
        prefix = "★ " if nm == "Charge" else "  "
        lb.insert('end', f"{prefix}{nm:<22}  =  {d['value']}  {d['unit']}")
        if nm == active_scalar: lb.selection_set(i); lb.see(i)

    vf = tk.Frame(win, bg='#fff8f0'); vf.pack(fill='x', padx=20, pady=(10,0))
    info_lbl = tk.Label(vf, text="", font=("Arial",8), fg='#888888', bg='#fff8f0')
    info_lbl.pack(anchor='w')
    tk.Label(vf, text="Enter new value:", font=("Arial",9,"bold"),
             fg='#b35c00', bg='#fff8f0').pack(anchor='w', pady=(6,2))
    evar = tk.StringVar(value=str(SCALAR_DATA[active_scalar]["value"]))
    entry = tk.Entry(vf, textvariable=evar, font=("Courier",12),
                      width=18, bd=2, relief='groove', justify='center')
    entry.pack(anchor='w'); entry.focus()

    def on_sel(e=None):
        sel = lb.curselection()
        if sel:
            nm=names[sel[0]]; d=SCALAR_DATA[nm]; lo,hi=d["range"]
            info_lbl.config(text=f"Range: {lo} to {hi}  {d['unit']}  |  Symbol: {d['symbol']}")
            evar.set(str(d["value"]))
    lb.bind('<<ListboxSelect>>', on_sel); on_sel()

    msg = tk.Label(win, text="", font=("Arial",9), fg='red', bg='#fff8f0'); msg.pack(pady=2)

    def on_ok():
        global active_scalar
        sel=lb.curselection()
        if not sel: msg.config(text="Please select a quantity."); return
        nm=names[sel[0]]; d=SCALAR_DATA[nm]; lo,hi=d["range"]
        try: val=float(evar.get())
        except: msg.config(text="Invalid number."); return
        if not (lo<=val<=hi): msg.config(text=f"Value must be between {lo} and {hi}."); return
        SCALAR_DATA[nm]["value"]=val; active_scalar=nm; win.destroy(); redraw_all()

    bf=tk.Frame(win,bg='#fff8f0'); bf.pack(pady=14)
    tk.Button(bf,text="  OK  ",command=on_ok,bg='#e07b00',fg='white',
              font=("Arial",10,"bold"),relief='flat',padx=10).pack(side='left',padx=8)
    tk.Button(bf,text="Cancel",command=win.destroy,bg='#eeeeee',fg='#555555',
              font=("Arial",10),relief='flat',padx=10).pack(side='left',padx=8)
    win.bind('<Return>', lambda e: on_ok()); win.mainloop()


# ══════════════════════════════════════════════════════════════
#  POPUP — VECTOR
# ══════════════════════════════════════════════════════════════
def enter_vector(event):
    global active_vector
    win = tk.Tk(); win.title("Enter Vector Components")
    win.configure(bg='#f0f4ff'); win.geometry("480x560")
    win.resizable(False,False); win.attributes('-topmost',True)

    tk.Label(win, text="Select Quantity & Enter X, Y Components",
             font=("Arial",12,"bold"), fg='#0d3b8e', bg='#f0f4ff').pack(pady=(16,4))
    tk.Label(win, text="★  Changing Electric Field E  updates the Q×E graph in real time.",
             font=("Arial",9,"italic"), fg='#8e44ad', bg='#f0f4ff').pack(pady=(0,8))

    frm=tk.Frame(win,bg='#f0f4ff'); frm.pack(fill='x',padx=20)
    tk.Label(frm,text="Vector Quantities:",font=("Arial",9,"bold"),
             fg='#0d3b8e',bg='#f0f4ff').pack(anchor='w')
    lb_frm=tk.Frame(frm,bd=1,relief='solid',bg='white'); lb_frm.pack(fill='x',pady=4)
    sb=tk.Scrollbar(lb_frm,orient='vertical')
    lb=tk.Listbox(lb_frm,height=9,font=("Courier",9),
                   selectbackground='#c5d8fd',selectforeground='#0d3b8e',
                   yscrollcommand=sb.set,activestyle='none',bg='white',relief='flat',bd=0)
    sb.config(command=lb.yview); sb.pack(side='right',fill='y'); lb.pack(fill='x')

    names=list(VECTOR_DATA.keys())
    for i,nm in enumerate(names):
        d=VECTOR_DATA[nm]; mag=np.sqrt(d["x"]**2+d["y"]**2)
        prefix="★ " if nm=="Electric Field E" else "  "
        lb.insert('end',f"{prefix}{nm:<24}  |v|={mag:.2f}  {d['unit']}")
        if nm==active_vector: lb.selection_set(i); lb.see(i)

    cf=tk.Frame(win,bg='#f0f4ff'); cf.pack(fill='x',padx=20,pady=(10,0))
    unit_lbl=tk.Label(cf,text="",font=("Arial",8),fg='#888888',bg='#f0f4ff')
    unit_lbl.pack(anchor='w',pady=(0,6))

    rx=tk.Frame(cf,bg='#f0f4ff'); rx.pack(anchor='w',pady=2)
    tk.Label(rx,text="X component : ",font=("Arial",9,"bold"),fg='#1a56db',bg='#f0f4ff').pack(side='left')
    xvar=tk.StringVar(value=str(VECTOR_DATA[active_vector]["x"]))
    tk.Entry(rx,textvariable=xvar,font=("Courier",12),width=12,bd=2,relief='groove',justify='center').pack(side='left')

    ry=tk.Frame(cf,bg='#f0f4ff'); ry.pack(anchor='w',pady=2)
    tk.Label(ry,text="Y component : ",font=("Arial",9,"bold"),fg='#e02020',bg='#f0f4ff').pack(side='left')
    yvar=tk.StringVar(value=str(VECTOR_DATA[active_vector]["y"]))
    tk.Entry(ry,textvariable=yvar,font=("Courier",12),width=12,bd=2,relief='groove',justify='center').pack(side='left')

    mag_lbl=tk.Label(cf,text="",font=("Courier",9,"bold"),fg='#333333',bg='#f0f4ff')
    mag_lbl.pack(anchor='w',pady=(6,0))

    def upd_mag(*a):
        try: m=np.sqrt(float(xvar.get())**2+float(yvar.get())**2); mag_lbl.config(text=f"|v| = {m:.4f}")
        except: mag_lbl.config(text="")

    def on_sel(e=None):
        sel=lb.curselection()
        if sel:
            nm=names[sel[0]]; d=VECTOR_DATA[nm]
            unit_lbl.config(text=f"Unit: {d['unit']}  |  Symbol: {d['symbol']}  |  Range: -6 to 6")
            xvar.set(str(d["x"])); yvar.set(str(d["y"])); upd_mag()

    lb.bind('<<ListboxSelect>>',on_sel)
    xvar.trace_add('write',upd_mag); yvar.trace_add('write',upd_mag); on_sel()

    msg=tk.Label(win,text="",font=("Arial",9),fg='red',bg='#f0f4ff'); msg.pack(pady=2)

    def on_ok():
        global active_vector
        sel=lb.curselection()
        if not sel: msg.config(text="Please select a quantity."); return
        nm=names[sel[0]]
        try: vx=float(xvar.get()); vy=float(yvar.get())
        except: msg.config(text="Invalid number."); return
        if not(-6<=vx<=6) or not(-6<=vy<=6): msg.config(text="Both components must be -6 to 6."); return
        VECTOR_DATA[nm]["x"]=vx; VECTOR_DATA[nm]["y"]=vy; active_vector=nm
        win.destroy(); redraw_all()

    bf=tk.Frame(win,bg='#f0f4ff'); bf.pack(pady=14)
    tk.Button(bf,text="  OK  ",command=on_ok,bg='#1a56db',fg='white',
              font=("Arial",10,"bold"),relief='flat',padx=10).pack(side='left',padx=8)
    tk.Button(bf,text="Cancel",command=win.destroy,bg='#eeeeee',fg='#555555',
              font=("Arial",10),relief='flat',padx=10).pack(side='left',padx=8)
    win.bind('<Return>',lambda e:on_ok()); win.mainloop()


# ══════════════════════════════════════════════════════════════
#  TOGGLE HANDLERS
# ══════════════════════════════════════════════════════════════
def toggle_scalar_table(event):
    global scalar_table_visible
    scalar_table_visible = not scalar_table_visible
    redraw_all()

def toggle_vector_table(event):
    global vector_table_visible
    vector_table_visible = not vector_table_visible
    redraw_all()

def update_toggle_labels():
    s_arrow = "v" if scalar_table_visible else ">"
    v_arrow = "v" if vector_table_visible else ">"
    btn_toggle_s.label.set_text(f"{s_arrow}  Scalar Table")
    btn_toggle_v.label.set_text(f"{v_arrow}  Vector Table")


# ══════════════════════════════════════════════════════════════
#  BUTTONS
# ══════════════════════════════════════════════════════════════
ax_bs  = fig.add_axes([0.03,  0.89, 0.12, 0.05])
ax_bv  = fig.add_axes([0.33,  0.94, 0.12, 0.05])
ax_ts  = fig.add_axes([0.03,  0.52, 0.14, 0.04])
ax_tv  = fig.add_axes([0.68,  0.94, 0.14, 0.04])

btn_s        = Button(ax_bs, 'Enter Scalar',    color='#fff3e0', hovercolor='#ffe0b2')
btn_v        = Button(ax_bv, 'Enter Vector',    color='#e8f0fe', hovercolor='#c5d8fd')
btn_toggle_s = Button(ax_ts, 'v  Scalar Table', color='#f5e6d0', hovercolor='#f0d0a8')
btn_toggle_v = Button(ax_tv, 'v  Vector Table', color='#dce8ff', hovercolor='#b8d0ff')

for btn, fc, fw, col in [
    (btn_s,        9, 'bold', '#b35c00'),
    (btn_v,        9, 'bold', '#0d3b8e'),
    (btn_toggle_s, 8, 'bold', '#8b4400'),
    (btn_toggle_v, 8, 'bold', '#0a2d7a'),
]:
    btn.label.set_fontsize(fc)
    btn.label.set_fontweight(fw)
    btn.label.set_color(col)

btn_s.on_clicked(enter_scalar)
btn_v.on_clicked(enter_vector)
btn_toggle_s.on_clicked(toggle_scalar_table)
btn_toggle_v.on_clicked(toggle_vector_table)

# ══════════════════════════════════════════════════════════════
#  INITIAL DRAW
# ══════════════════════════════════════════════════════════════
redraw_all()
plt.show()
