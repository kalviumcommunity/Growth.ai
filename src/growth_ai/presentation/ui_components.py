from __future__ import annotations

import streamlit as st

CONVERSION_IQ_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* Global Font & Reset */
html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: #f8fafc !important;
    color: #1e293b !important;
}

/* Hide default Streamlit elements */
#MainMenu, header, footer {
    visibility: hidden;
    height: 0px;
}
.block-container {
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    max-width: 1400px !important;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: 0.5rem;
}
.sidebar-section-title {
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    color: #94a3b8;
    text-transform: uppercase;
    margin-top: 1rem;
    margin-bottom: 0.5rem;
    padding-left: 0.5rem;
}
.sidebar-sub-status {
    font-size: 0.75rem;
    color: #64748b;
    font-weight: 500;
    margin-bottom: 1rem;
    padding-left: 0.5rem;
}

/* Custom Navigation Tabs Header */
.top-navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #ffffff;
    padding: 0.75rem 1.5rem;
    border-bottom: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.brand-logo {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.25rem;
    font-weight: 800;
    color: #312e81;
    letter-spacing: -0.02em;
}
.brand-icon {
    width: 28px;
    height: 28px;
    background: #4f46e5;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 900;
    font-size: 0.85rem;
    box-shadow: 0 2px 6px rgba(79, 70, 229, 0.3);
}

/* Card Styling */
.iq-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    margin-bottom: 1rem;
    transition: all 0.2s ease-in-out;
}
.iq-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* Metric Cards */
.kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    position: relative;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}
.kpi-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.75rem;
}
.kpi-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: #e0e7ff;
    color: #4f46e5;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}
.kpi-badge-green {
    background: #dcfce7;
    color: #15803d;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
}
.kpi-badge-red {
    background: #ffe4e6;
    color: #be123c;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
}
.kpi-badge-gray {
    background: #f1f5f9;
    color: #64748b;
    font-size: 0.72rem;
    font-weight: 700;
    padding: 0.2rem 0.5rem;
    border-radius: 12px;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #64748b;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}
.kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.03em;
    line-height: 1.1;
}

/* Acquisition Funnel */
.funnel-container {
    display: flex;
    gap: 4px;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 0.75rem;
    margin-bottom: 1.5rem;
}
.funnel-stage {
    flex: 1;
    padding: 1.25rem 1rem;
    color: #0f172a;
    transition: all 0.2s ease;
}
.funnel-stage-1 { background: #e0e7ff; color: #1e1b4b; }
.funnel-stage-2 { background: #c7d2fe; color: #1e1b4b; }
.funnel-stage-3 { background: #818cf8; color: #ffffff; }
.funnel-stage-4 { background: #3730a3; color: #ffffff; }

.funnel-stage-name {
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    opacity: 0.85;
    margin-bottom: 0.35rem;
}
.funnel-stage-value {
    font-size: 1.5rem;
    font-weight: 800;
    line-height: 1.1;
}
.funnel-stage-sub {
    font-size: 0.75rem;
    font-weight: 600;
    opacity: 0.8;
    margin-top: 0.35rem;
}

/* Status Badges */
.badge-status {
    display: inline-block;
    padding: 0.2rem 0.6rem;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.status-running, .status-valid, .status-low-risk {
    background: #dcfce7;
    color: #166534;
}
.status-warning, .status-mod-risk {
    background: #fef9c3;
    color: #854d0e;
}
.status-staging, .status-info {
    background: #e0e7ff;
    color: #3730a3;
}
.status-critical, .status-danger, .status-failed {
    background: #fee2e2;
    color: #991b1b;
}

/* Custom Table Styling */
.iq-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin-top: 0.5rem;
}
.iq-table th {
    background: #f8fafc;
    color: #64748b;
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #e2e8f0;
    text-align: left;
}
.iq-table td {
    padding: 0.85rem 1rem;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.85rem;
    color: #334155;
    vertical-align: middle;
}
.iq-table tr:hover td {
    background-color: #f8fafc;
}

/* Progress bar inside table */
.score-bar-bg {
    width: 70px;
    height: 6px;
    background: #e2e8f0;
    border-radius: 3px;
    display: inline-block;
    vertical-align: middle;
    margin-left: 8px;
    overflow: hidden;
}
.score-bar-fill-green { height: 100%; background: #22c55e; border-radius: 3px; }
.score-bar-fill-yellow { height: 100%; background: #eab308; border-radius: 3px; }
.score-bar-fill-red { height: 100%; background: #ef4444; border-radius: 3px; }

/* User avatar badge */
.user-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: #e0e7ff;
    color: #4338ca;
    font-weight: 700;
    font-size: 0.75rem;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-right: 0.6rem;
}

/* Dropzone box */
.dropzone-box {
    border: 2px dashed #cbd5e1;
    border-radius: 12px;
    padding: 2.5rem 1.5rem;
    text-align: center;
    background: #f8fafc;
    transition: all 0.2s ease;
}
.dropzone-box:hover {
    border-color: #6366f1;
    background: #f5f3ff;
}

/* Smart Insights Cards */
.insight-card {
    border-left: 4px solid #4f46e5;
    background: #ffffff;
    border-top: 1px solid #e2e8f0;
    border-right: 1px solid #e2e8f0;
    border-bottom: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.insight-card-green { border-left-color: #10b981; }
.insight-card-orange { border-left-color: #f59e0b; }

/* Floating Action Button */
.fab-button {
    position: fixed;
    bottom: 24px;
    right: 24px;
    width: 48px;
    height: 48px;
    background: #4338ca;
    color: white;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: 600;
    box-shadow: 0 4px 14px rgba(67, 56, 202, 0.4);
    cursor: pointer;
    z-index: 9999;
}
.fab-button:hover {
    background: #3730a3;
}
</style>
"""


def inject_custom_css() -> None:
    st.markdown(CONVERSION_IQ_CSS, unsafe_allow_html=True)


def render_top_navbar(active_tab: str) -> None:
    st.markdown(
        f"""
        <div class="top-navbar">
            <div class="brand-logo">
                <div class="brand-icon">IQ</div>
                <span>Conversion-IQ</span>
            </div>
            <div style="display: flex; align-items: center; gap: 2rem;">
                <span style="font-size: 0.85rem; font-weight: {"700" if active_tab == "Dashboard" else "500"}; color: {"#4338ca" if active_tab == "Dashboard" else "#64748b"}; cursor: pointer;">Dashboard</span>
                <span style="font-size: 0.85rem; font-weight: {"700" if active_tab == "Users" else "500"}; color: {"#4338ca" if active_tab == "Users" else "#64748b"}; cursor: pointer;">Users</span>
                <span style="font-size: 0.85rem; font-weight: {"700" if active_tab == "Ingestion" else "500"}; color: {"#4338ca" if active_tab == "Ingestion" else "#64748b"}; cursor: pointer;">Ingestion</span>
                <span style="font-size: 0.85rem; font-weight: {"700" if active_tab == "Experiments" else "500"}; color: {"#4338ca" if active_tab == "Experiments" else "#64748b"}; cursor: pointer;">Experiments</span>
            </div>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="color: #64748b; font-size: 1.1rem; cursor: pointer;">🔔</div>
                <div class="user-avatar" style="margin-right: 0;">JD</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_card(
    icon_symbol: str, title: str, value: str, trend: str, trend_type: str = "green"
) -> str:
    badge_class = "kpi-badge-green"
    if trend_type == "red":
        badge_class = "kpi-badge-red"
    elif trend_type == "gray":
        badge_class = "kpi-badge-gray"

    return f"""
    <div class="kpi-card">
        <div class="kpi-header">
            <div class="kpi-icon">{icon_symbol}</div>
            <span class="{badge_class}">{trend}</span>
        </div>
        <div class="kpi-label">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """


def render_sparkline_svg(
    color: str = "#22c55e", points: str = "0,15 10,12 20,18 30,8 40,10 50,4"
) -> str:
    return f"""
    <svg width="60" height="20" viewBox="0 0 50 20" style="overflow: visible;">
        <polyline fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" points="{points}" />
    </svg>
    """


def render_bar_sparkline_svg() -> str:
    return """
    <svg width="40" height="18" viewBox="0 0 40 18">
        <rect x="2" y="10" width="4" height="8" fill="#22c55e" rx="1"/>
        <rect x="9" y="6" width="4" height="12" fill="#22c55e" rx="1"/>
        <rect x="16" y="8" width="4" height="10" fill="#22c55e" rx="1"/>
        <rect x="23" y="4" width="4" height="14" fill="#22c55e" rx="1"/>
        <rect x="30" y="2" width="4" height="16" fill="#22c55e" rx="1"/>
    </svg>
    """


def render_fab_button() -> None:
    st.markdown('<div class="fab-button">+</div>', unsafe_allow_html=True)
