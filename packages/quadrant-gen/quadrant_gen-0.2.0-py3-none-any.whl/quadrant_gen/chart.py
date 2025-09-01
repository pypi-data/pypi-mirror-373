#!/usr/bin/env python3
"""
Quadrant chart generator module.
Creates a quadrant chart from CSV data and returns base64 encoded output.
"""

import csv
import io
import base64
import matplotlib.pyplot as plt
import numpy as np
from io import StringIO


def read_points_from_csv_string(csv_string):
    """
    Read data points from a CSV string.
    
    Args:
        csv_string (str): CSV content as a string
        
    Returns:
        list: List of data points with label, x, y coordinates
        
    Raises:
        ValueError: If CSV doesn't have required headers or contains invalid data
    """
    pts = []
    f = StringIO(csv_string)
    r = csv.DictReader(f)
    required = {"name", "description", "x", "y"}
    if not required.issubset(set(r.fieldnames or [])):
        raise ValueError(f"CSV must contain headers: {', '.join(sorted(required))}")
    for row in r:
        try:
            x = float(row["x"]); y = float(row["y"])
        except Exception:
            raise ValueError(f"Invalid numeric values for x/y in row: {row}")
        pts.append({
            "label": f'{row["name"]}\n({row["description"]})' if row.get("description") else row["name"],
            "x": x, "y": y
        })
    return pts


def sample_points():
    """
    Generate sample data points for demonstration.
    
    Returns:
        list: List of sample data points
    """
    # Example data you can replace or remove
    return [
        {"label": "Product A\n(High quality)", "x": 0.18, "y": 0.75},
        {"label": "Product B\n(Low cost)", "x": 0.35, "y": 0.25},
        {"label": "Product C\n(Innovative)", "x": 0.80, "y": 0.68},
        {"label": "Product D\n(Traditional)", "x": 0.65, "y": 0.40},
    ]


def generate_quadrant_chart(points, title="", x_left="", x_right="", y_bottom="", y_top="", format="png", dpi=200):
    """
    Create a quadrant chart and return as base64 encoded string.
    
    Args:
        points (list): List of data points with label, x, y coordinates
        title (str): Chart title
        x_left (str): Label for left side of x-axis
        x_right (str): Label for right side of x-axis
        y_bottom (str): Label for bottom of y-axis
        y_top (str): Label for top of y-axis
        format (str): Output format ('png' or 'pdf')
        dpi (int): Resolution of the output image
        
    Returns:
        str: Base64 encoded image with appropriate mime type prefix
    """
    buffer = io.BytesIO()
    
    fig, ax = plt.subplots(figsize=(12, 9), dpi=dpi)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # Central guides
    ax.axvline(0.5, linestyle="--", linewidth=1)
    ax.axhline(0.5, linestyle="--", linewidth=1)

    # Clean frame
    for s in ["top", "right", "left", "bottom"]:
        ax.spines[s].set_visible(False)

    # Axis ticks as quadrant labels
    ax.set_xticks([0.0, 0.5, 1.0], labels=[x_left, "", x_right])
    ax.set_yticks([0.0, 0.5, 1.0], labels=[y_bottom, "", y_top])
    ax.tick_params(axis="both", which="both", length=0, pad=10, labelsize=11)

    # Titles
    if title:
        plt.suptitle(title, fontsize=20, fontweight="bold", y=0.95)
        # Only show subtitle if both labels are provided
        if y_bottom and y_top:
            plt.title(f"{y_bottom} vs {y_top}", fontsize=12, color="dimgray")

    # Plot points (default Matplotlib colors)
    markers = ["o", "X", "s", "D", "^", "v", "<", ">", "P", "*"]
    sizes = [150] * len(points)
    
    # Sort points by proximity to center to place central points first
    sorted_points = sorted(enumerate(points), 
                          key=lambda x: abs(x[1]["x"]-0.5) + abs(x[1]["y"]-0.5))
    
    for idx, p in sorted_points:
        m = markers[idx % len(markers)]
        ax.scatter(p["x"], p["y"], s=sizes[idx], marker=m, edgecolors="black", linewidths=1.1, zorder=3)
        
        # Create text with background box for better readability
        text = ax.annotate(
            p["label"], (p["x"], p["y"]),
            xytext=(15, 15), textcoords="offset points",
            fontsize=11, ha="left", va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.1", color="gray")
        )

    # Optional quadrant captions - only show if labels are provided
    if x_left and y_top:
        ax.text(0.07, 0.92, f"{x_left} • {y_top}", fontsize=10, color="gray")
    if x_left and y_bottom:
        ax.text(0.07, 0.05, f"{x_left} • {y_bottom}", fontsize=10, color="gray")
    if x_right and y_top:
        ax.text(0.62, 0.92, f"{x_right} • {y_top}", fontsize=10, color="gray")
    if x_right and y_bottom:
        ax.text(0.62, 0.05, f"{x_right} • {y_bottom}", fontsize=10, color="gray")

    plt.tight_layout()
    fig.savefig(buffer, format=format, bbox_inches="tight")
    plt.close(fig)  # Close to prevent memory leaks
    
    buffer.seek(0)  # Reset buffer position to the beginning
    
    # Convert to base64
    encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
    mime_type = 'image/png' if format == 'png' else 'application/pdf'
    data_url = f"data:{mime_type};base64,{encoded}"
    
    return data_url


def csv_to_quadrant_chart(csv_string, title="", x_left="", x_right="", y_bottom="", y_top="", format="png"):
    """
    Create a quadrant chart from CSV string and return as base64 encoded image.
    
    Args:
        csv_string (str): CSV content as a string
        title (str): Chart title
        x_left (str): Label for left side of x-axis
        x_right (str): Label for right side of x-axis
        y_bottom (str): Label for bottom of y-axis
        y_top (str): Label for top of y-axis
        format (str): Output format ('png' or 'pdf')
        
    Returns:
        str: Base64 encoded image with appropriate mime type prefix
    """
    points = read_points_from_csv_string(csv_string)
    return generate_quadrant_chart(
        points=points,
        title=title,
        x_left=x_left,
        x_right=x_right,
        y_bottom=y_bottom,
        y_top=y_top,
        format=format
    )
