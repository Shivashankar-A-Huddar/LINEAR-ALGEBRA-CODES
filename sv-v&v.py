import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, RadioButtons

# ==============================================================================
#  CONFIGURATION & STYLING
# ==============================================================================
COLORS = {
    'v1': '#1f77b4',      # Blue (Input 1)
    'v2': '#2ca02c',      # Green (Input 2)
    'res': '#9467bd',     # Purple (Positive Result)
    'scalar': '#ff7f0e',  # Orange (Scalar Input)
    'neg': '#d62728',     # Red (Negative Result)
    'grid': '#e5e5e5'
}

class DualVectorVisualizer:
    def __init__(self):
        self.fig = plt.figure(figsize=(16, 8))
        self.fig.canvas.manager.set_window_title("Vector Operations Comparison")
        self.fig.patch.set_facecolor('#fafafa')

        # Top 60%: Plot Areas
        # [left, bottom, width, height]
        self.ax_left = self.fig.add_axes([0.05, 0.40, 0.40, 0.50])
        self.ax_right = self.fig.add_axes([0.55, 0.40, 0.40, 0.50])
        
        # Text/Formula Output Boxes
        self.ax_txt_l = self.fig.add_axes([0.05, 0.90, 0.40, 0.08])
        self.ax_txt_l.axis('off')
        self.ax_txt_r = self.fig.add_axes([0.55, 0.90, 0.30, 0.08])
        self.ax_txt_r.axis('off')

        # Mode switch for Right Plot (Dot vs Cross)
        self.ax_radio = self.fig.add_axes([0.80, 0.88, 0.15, 0.10])
        self.ax_radio.set_facecolor('#f0f0f0')
        self.radio = RadioButtons(self.ax_radio, ('Dot Product', 'Cross Product'), activecolor=COLORS['v1'])
        self.radio.on_clicked(self.update)
        
        self.setup_sliders()
        self.update(None)

    def setup_sliders(self):
        # Bottom Left: Sliders for Scalar x Vector
        self.sl_sigma = Slider(self.fig.add_axes([0.1, 0.20, 0.3, 0.03]), 'Scalar (σ)', -3.0, 3.0, valinit=1.5, color=COLORS['scalar'])
        self.sl_ex = Slider(self.fig.add_axes([0.1, 0.15, 0.3, 0.03]), 'Vx', -5, 5, valinit=2.0, color=COLORS['v1'])
        self.sl_ey = Slider(self.fig.add_axes([0.1, 0.10, 0.3, 0.03]), 'Vy', -5, 5, valinit=1.0, color=COLORS['v1'])

        # Bottom Right: Sliders for Vector x Vector
        self.sl_v1x = Slider(self.fig.add_axes([0.6, 0.20, 0.3, 0.03]), 'V1x', -5, 5, valinit=3.0, color=COLORS['v1'])
        self.sl_v1y = Slider(self.fig.add_axes([0.6, 0.15, 0.3, 0.03]), 'V1y', -5, 5, valinit=1.0, color=COLORS['v1'])
        self.sl_v2x = Slider(self.fig.add_axes([0.6, 0.10, 0.3, 0.03]), 'V2x', -5, 5, valinit=-1.0, color=COLORS['v2'])
        self.sl_v2y = Slider(self.fig.add_axes([0.6, 0.05, 0.3, 0.03]), 'V2y', -5, 5, valinit=3.0, color=COLORS['v2'])

        # Attach update function
        for s in [self.sl_sigma, self.sl_ex, self.sl_ey, self.sl_v1x, self.sl_v1y, self.sl_v2x, self.sl_v2y]:
            s.on_changed(self.update)

    def draw_grid(self, ax, title):
        ax.clear()
        ax.grid(True, which='both', color=COLORS['grid'], linestyle='-')
        ax.axhline(0, color='black', linewidth=1)
        ax.axvline(0, color='black', linewidth=1)
        ax.set_xlim(-8, 8)
        ax.set_ylim(-8, 8)
        ax.set_aspect('equal')
        ax.set_title(title, fontweight='bold', pad=10)

    def draw_arrow(self, ax, vec, color, label, origin=(0,0)):
        ax.annotate('', xy=(origin[0]+vec[0], origin[1]+vec[1]), xytext=origin,
                    arrowprops=dict(arrowstyle='-|>', color=color, lw=2, mutation_scale=15))
        
        # Offset label slightly based on vector direction
        offset_x = 0.3 if vec[0] >= 0 else -0.8
        offset_y = 0.3 if vec[1] >= 0 else -0.8
        ax.text(origin[0]+vec[0]+offset_x, origin[1]+vec[1]+offset_y, label, color=color, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.1", fc="white", ec="none", alpha=0.7))

    def update(self, val):
        self.draw_left()
        self.draw_right()
        self.fig.canvas.draw_idle()

    # ==========================================================================
    # LEFT PLOT: SCALAR x VECTOR
    # ==========================================================================
    def draw_left(self):
        self.draw_grid(self.ax_left, "Scalar × Vector (Scaling)")
        self.ax_txt_l.clear(); self.ax_txt_l.axis('off')

        sigma = self.sl_sigma.val
        V_in = np.array([self.sl_ex.val, self.sl_ey.val])
        V_out = sigma * V_in

        # Draw Vectors
        self.draw_arrow(self.ax_left, V_in, COLORS['v1'], "Input")
        self.draw_arrow(self.ax_left, V_out, COLORS['res'], f"Result ({sigma:.1f}×)")

        # Status Text
        self.ax_txt_l.text(0.5, 0.5, f"$\\vec{{V}}_{{out}} = {sigma:.1f} \\cdot \\vec{{V}}_{{in}}$\nResult is a VECTOR.", 
                           ha='center', va='center', fontsize=12, color=COLORS['res'], fontweight='bold')

    # ==========================================================================
    # RIGHT PLOT: VECTOR x VECTOR
    # ==========================================================================
    def draw_right(self):
        mode = self.radio.value_selected
        self.draw_grid(self.ax_right, f"Vector × Vector ({mode})")
        self.ax_txt_r.clear(); self.ax_txt_r.axis('off')

        v1 = np.array([self.sl_v1x.val, self.sl_v1y.val])
        v2 = np.array([self.sl_v2x.val, self.sl_v2y.val])

        # Draw Vectors
        self.draw_arrow(self.ax_right, v1, COLORS['v1'], "V1")
        self.draw_arrow(self.ax_right, v2, COLORS['v2'], "V2")

        if mode == 'Dot Product':
            dot = np.dot(v1, v2)
            res_col = COLORS['res'] if dot >= 0 else COLORS['neg']
            
            self.ax_txt_r.text(0.5, 0.5, f"$\\vec{{V}}_1 \\cdot \\vec{{V}}_2 = {dot:.2f}$\nResult is a SCALAR.", 
                               ha='center', va='center', fontsize=12, color=res_col, fontweight='bold')
            
            # Show Projection for visual intuition
            v2_norm = np.linalg.norm(v2)
            if v2_norm > 0:
                proj = (dot / (v2_norm**2)) * v2
                self.ax_right.plot([v1[0], proj[0]], [v1[1], proj[1]], '--', color='gray')
                self.ax_right.plot([0, proj[0]], [0, proj[1]], color='orange', lw=4, alpha=0.5)
                self.ax_right.text(proj[0], proj[1], " Projection", color='orange', fontsize=9)

        else: # Cross Product
            cross_z = np.cross(v1, v2)
            res_col = COLORS['res'] if cross_z >= 0 else COLORS['neg']
            
            # Determine Z-axis direction text
            dir_str = "OUT of page ⊙" if cross_z > 0 else "INTO page ⊗"
            if abs(cross_z) < 0.1: dir_str = "Zero"
            
            self.ax_txt_r.text(0.5, 0.5, f"$\\vec{{V}}_1 \\times \\vec{{V}}_2 = {cross_z:.2f} \\hat{{k}}$\nResult is a VECTOR ({dir_str}).", 
                               ha='center', va='center', fontsize=12, color=res_col, fontweight='bold')
            
            # Draw Z-axis marker (Circle or X)
            marker = 'o' if cross_z > 0 else 'x'
            msize = 10 + min(abs(cross_z)*2, 40) # Scale marker size by magnitude
            self.ax_right.plot(0, 0, marker=marker, markersize=msize, color=res_col, markeredgewidth=2)

if __name__ == "__main__":
    app = DualVectorVisualizer()
    plt.show()
