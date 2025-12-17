"""UI components for the Streamlit GUI.

This module contains reusable UI components and rendering functions
for the Core Cartographer GUI.
"""

from pathlib import Path

import streamlit as st


def load_css() -> None:
    """Load and inject custom CSS styles."""
    css_path = Path(__file__).parent.parent / "styles.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_step_header(current_step: int) -> None:
    """
    Render the step progress header.

    Args:
        current_step: The current step number (1-3).
    """
    steps = [
        {"id": 1, "label": "Upload"},
        {"id": 2, "label": "Label"},
        {"id": 3, "label": "Extract"},
    ]

    html = '<div class="step-header">'
    for i, step in enumerate(steps):
        active_class = "active" if step["id"] <= current_step else ""
        html += f'<div class="step-item {active_class}">{step["id"]}. {step["label"]}</div>'
        if i < len(steps) - 1:
            loader_active = "active" if step["id"] < current_step else ""
            html += f'<div class="step-loader {loader_active}"></div>'
    html += "</div>"

    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(label: str, value: str) -> None:
    """
    Render a styled metric card.

    Args:
        label: The metric label.
        value: The metric value to display.
    """
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_subtype_color(subtype: str, all_subtypes: list[str]) -> str:
    """
    Assign a colored circle emoji to each subtype for visual distinction.

    Args:
        subtype: The subtype to get a color for.
        all_subtypes: List of all subtypes for consistent color assignment.

    Returns:
        A colored circle emoji.
    """
    colors = [
        "🔵", "🟢", "🟡", "🟠", "🟣", "🔴", "🟤", "⚫", "⚪",
        "🟥", "🟧", "🟨", "🟩", "🟦", "🟪",
    ]
    try:
        idx = all_subtypes.index(subtype) % len(colors)
        return colors[idx]
    except ValueError:
        return "⚪"


def render_subtype_badges(subtypes: list[str]) -> None:
    """
    Render subtype badges as styled tags.

    Args:
        subtypes: List of subtype names to display.
    """
    badges = " ".join([
        f"<span class='badge' style='background: #e2e8f0; color: #1e293b; "
        f"border: 1px solid #cbd5e1;'>{s}</span>"
        for s in subtypes
    ])
    st.markdown(badges, unsafe_allow_html=True)


def render_file_status(file_count: int) -> None:
    """
    Render the file upload status message.

    Args:
        file_count: Number of files uploaded.
    """
    if file_count > 0:
        st.success(f"{file_count} documents ready.")
    else:
        st.markdown(
            "<div style='padding-top: 0.5rem; color: #94a3b8; font-size: 0.9rem;'>"
            "Waiting for files...</div>",
            unsafe_allow_html=True,
        )
