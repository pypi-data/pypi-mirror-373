import matplotlib.pyplot as plt
import matplotlib as mpl
import squarify
import numpy as np
from matplotlib import colormaps


def _contrast_text_color(rgb):
    # rgb in 0-1 range
    r, g, b = rgb[:3]
    hue=r+b+g
    hue/=3
    hue
    # Relative luminance (sRGB)
    lum = 0.2126*r + 0.7152*g + 0.0722*b
    g_new=0 if lum>0.5 else 1
    return g_new,g_new,1
    #return 'black' if lum > 0.53 else 'white'

def _place_text_fit(ax, label, x, y, w, h, init_fs=18, min_fs=8, color='white', max_shrink_steps=40):
    # Try to place label, shrinking font until it fits. Ellipsize if needed.
    fig = ax.figure
    # Convert rect size to display pixels
    (x0_disp, y0_disp) = ax.transData.transform((x, y))
    (x1_disp, y1_disp) = ax.transData.transform((x + w, y + h))
    rect_w_px = abs(x1_disp - x0_disp)
    rect_h_px = abs(y1_disp - y0_disp)
    margin_px = 6.0

    txt = None
    fs = int(init_fs)
    text_str = label
    for _ in range(max_shrink_steps):
        if txt is not None:
            txt.remove()
        txt = ax.text(x + w/2, y + h/2, text_str,
                      ha='center', va='center', fontsize=fs, color=color,
                      wrap=False, clip_on=True)
        fig.canvas.draw_idle()
        fig.canvas.flush_events()
        renderer = fig.canvas.get_renderer()
        bbox = txt.get_window_extent(renderer=renderer)
        fits_w = (bbox.width <= max(1.0, rect_w_px - margin_px))
        fits_h = (bbox.height <= max(1.0, rect_h_px - margin_px))
        if fits_w and fits_h:
            return
        # Shrink first, then ellipsize if at min
        if fs > min_fs:
            fs -= 1
            continue
        # Try ellipsizing if still not fit at min font
        if len(text_str) > 4:
            text_str = text_str[:-2] + '…'
        else:
            break  # give up
    # Final fallback: keep smallest text or clear
    if txt is None:
        ax.text(x + w/2, y + h/2, '', ha='center', va='center')

def valued_buzzwords(data, figsize=(20, 5), cmap='YlGn',
                      min_font=8, max_font=100, show_values=False, edgecolor='black',stretch=2):
    # Validate and prep data
    if not isinstance(data, dict) or len(data) == 0:
        raise ValueError("Provide a non-empty dict like {'Python': 10, 'NumPy': 8, ...}")
    items = [(k, float(v)) for k, v in data.items() if v is not None and float(v) > 0]
    if len(items) == 0:
        raise ValueError("All weights are non-positive. Use positive numbers.")
    # Sort for nicer layout
    items.sort(key=lambda kv: kv[1], reverse=True)
    labels = [k for k, _ in items]
    sizes = [v for _, v in items]
    width,height=figsize

    # Normalize and layout in unit square
    norm_sizes = squarify.normalize_sizes(sizes,height*stretch, width)
    #norm_sizes = squarify.normalize_sizes(sizes, float(width), float(height))
    rects = squarify.squarify(norm_sizes, 0, 0, width, height*stretch)

    # Colors based on size
    cm = mpl.cm.get_cmap(cmap)
    vmin, vmax = min(sizes), max(sizes)
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    fig, ax = plt.subplots(figsize=figsize)
    ax.axis('off')
    ax.set_xlim(0, width)
    full_height=height*stretch
    ax.set_ylim(0,full_height)

    for (label, val), r in zip(items, rects):
        x, y, w, h = r['x'],r['y'], r['dx'], r['dy']
        y=full_height-y-h
        face = cm(norm(val))
        ax.add_patch(plt.Rectangle((x,y), w, h, facecolor=face, edgecolor=edgecolor, linewidth=1.0))
        # Initial font size scaled by sqrt(area)
        area = w * h
        init_fs = min_font + (max_font - min_font) * area/full_height/width
        text_color = _contrast_text_color(face)
        main_label = f"{label}" if not show_values else f"{label}\n{val:g}"
        _place_text_fit(ax, main_label, x, y, w, h, init_fs=init_fs, min_fs=min_font, color=text_color)

    # Optional colorbar indicating value scale
    sm = mpl.cm.ScalarMappable(norm=norm, cmap=cm)
    sm.set_array([])
    #cbar = plt.colorbar(sm, ax=ax, fraction=0.035, pad=0.02)
    #cbar.set_label('Experience score', rotation=90)
    plt.tight_layout()
    return fig, ax