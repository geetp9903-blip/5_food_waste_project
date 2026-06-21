"""
Chart Utility module for consistent monochromatic and semantic visualization themes.
Matches the ZeroWaste dark violet-purple background design system.
"""

import plotly.graph_objects as go

# Custom monochromatic color palettes tailored for high-contrast on dark backgrounds
BLUE_PALETTE = ['#38bdf8', '#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8']
RED_PALETTE = ['#fca5a5', '#f87171', '#ef4444', '#dc2626', '#b91c1c']
GREEN_PALETTE = ['#86efac', '#4ade80', '#22c55e', '#16a34a', '#15803d']
YELLOW_PALETTE = ['#fde047', '#facc15', '#f59e0b', '#d97706', '#b45309']

# Semantic mappings for consistency across visualizations
FOOD_TYPE_COLOR_MAP = {
    'Vegetarian': '#22c55e',      # Green-500
    'Vegan': '#3b82f6',           # Blue-500 (Matches premium vegan theme)
    'Non-Vegetarian': '#ef4444'   # Red-500
}

STATUS_COLOR_MAP = {
    'Completed': '#22c55e',       # Green-500
    'Pending': '#fbbf24',         # Amber-400
    'Cancelled': '#ef4444',       # Red-500
    'Rejected': '#f87171'         # Light Red-400
}

# Distinct categories mapping for provider types
PROVIDER_TYPE_COLOR_MAP = {
    'Restaurant': '#38bdf8',      # Blue
    'Grocery Store': '#22c55e',   # Green
    'Supermarket': '#facc15',     # Yellow
    'Bakery': '#ef4444',          # Red
    'Individual': '#a78bfa',      # Purple
    'Other': '#cbd5e1'            # Slate
}

def apply_premium_chart_layout(fig):
    """
    Applies custom dark mode styling to the chart layout (transparency, fonts, gridlines, hover).
    """
    font_family = "'Plus Jakarta Sans', 'Outfit', sans-serif"
    text_color = '#cbd5e1'
    grid_color = 'rgba(148, 163, 184, 0.08)'  # faint slate-400 grid lines
    
    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family=font_family, color=text_color),
        margin=dict(l=40, r=40, t=50, b=40),
        hoverlabel=dict(
            bgcolor='rgba(15, 23, 42, 0.95)',
            bordercolor='rgba(255, 255, 255, 0.1)',
            font=dict(family=font_family, size=13, color='#f8fafc')
        ),
        legend=dict(
            bgcolor='rgba(15, 23, 42, 0.5)',
            bordercolor='rgba(255, 255, 255, 0.05)',
            borderwidth=1,
            font=dict(size=11, color='#94a3b8')
        )
    )
    
    # Configure axes if present (safely ignored on non-Cartesian charts like Pie/Donut charts)
    try:
        fig.update_xaxes(
            showgrid=True,
            gridcolor=grid_color,
            zeroline=False,
            tickfont=dict(color='#94a3b8'),
            titlefont=dict(color='#cbd5e1')
        )
        fig.update_yaxes(
            showgrid=True,
            gridcolor=grid_color,
            zeroline=False,
            tickfont=dict(color='#94a3b8'),
            titlefont=dict(color='#cbd5e1')
        )
    except Exception:
        pass
    
    # Customise Pie/Donut traces specifically if they are present in the figure
    for trace in fig.data:
        if trace.type == 'pie':
            # Subtle dark purple border matching the linear-gradient container background
            trace.marker.line = dict(color='#1e1b4b', width=2)
            if not hasattr(trace, 'hole') or trace.hole is None or trace.hole == 0:
                trace.hole = 0.4
                
    return fig

def style_expiry_dataframe(df):
    """
    Styles the expiry dataframe using custom CSS background colors without requiring matplotlib.
    Highlights larger quantities in soft red tones.
    """
    def make_red_gradient(val):
        try:
            v = float(val)
            # Map quantity range to intensity (cap at 250 for scaling)
            intensity = min(0.4, max(0.05, v / 250.0))
            return f'background-color: rgba(239, 68, 68, {intensity}); color: #fca5a5; font-weight: 500;'
        except (ValueError, TypeError):
            return ''
    
    # Check for pandas newer styler map vs deprecated applymap
    if hasattr(df.style, 'map'):
        return df.style.map(make_red_gradient, subset=['Quantity'])
    else:
        return df.style.applymap(make_red_gradient, subset=['Quantity'])

