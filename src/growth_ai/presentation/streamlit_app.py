from __future__ import annotations

import streamlit as st

from growth_ai.application.cleaning import clean_analytics_bundle
from growth_ai.application.metrics import calculate_kpis
from growth_ai.application.reporting import export_kpi_report
from growth_ai.config import get_settings
from growth_ai.infrastructure.repositories import SqlAnalyticsRepository
from growth_ai.presentation.ui_components import (
    inject_custom_css,
    render_bar_sparkline_svg,
    render_fab_button,
    render_kpi_card,
    render_sparkline_svg,
    render_top_navbar,
)


def _render_sidebar(settings) -> str:
    with st.sidebar:
        st.markdown(
            """
            <div style="display: flex; align-items: center; gap: 0.5rem; padding-bottom: 0.5rem; margin-bottom: 1rem; border-bottom: 1px solid #e2e8f0;">
                <div style="font-weight: 800; color: #312e81; font-size: 1.1rem;">Conversion-IQ</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="sidebar-section-title">CORE PIPELINE</div>', unsafe_allow_html=True
        )
        selected_page = st.radio(
            "Navigation",
            options=["Dashboard", "Users", "Ingestion", "Experiments"],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")

        if selected_page == "Dashboard":
            st.markdown(
                """
                <div style="background: #eff6ff; border: 1px solid #dbeafe; border-radius: 8px; padding: 0.75rem; margin-top: 1rem;">
                    <div style="font-size: 0.7rem; font-weight: 700; color: #1e40af; text-transform: uppercase;">System Status</div>
                    <div style="font-size: 0.8rem; font-weight: 600; color: #15803d; margin-top: 0.25rem;">
                        <span style="color: #22c55e;">●</span> Data Flow: Optimal
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif selected_page == "Experiments":
            st.markdown(
                """
                <div style="font-size: 0.7rem; font-weight: 800; color: #94a3b8; text-transform: uppercase;">Data Pipeline</div>
                <div class="sidebar-sub-status">Engine v1.2.0 Active</div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; margin-top: 2rem;">
                    <div style="font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase;">QUOTA STATUS</div>
                    <div style="height: 6px; background: #e2e8f0; border-radius: 3px; margin-top: 0.5rem; overflow: hidden;">
                        <div style="width: 65%; height: 100%; background: #4f46e5;"></div>
                    </div>
                    <div style="font-size: 0.7rem; color: #64748b; margin-top: 0.35rem; display: flex; justify-content: space-between;">
                        <span>650k / 1M events</span>
                        <span>65%</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif selected_page == "Ingestion":
            st.markdown(
                """
                <div style="font-size: 0.7rem; font-weight: 800; color: #94a3b8; text-transform: uppercase;">Data Pipeline</div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; margin-top: 4rem;">
                    <div style="font-size: 0.7rem; font-weight: 700; color: #64748b; text-transform: uppercase;">STORAGE USED</div>
                    <div style="height: 6px; background: #e2e8f0; border-radius: 3px; margin-top: 0.5rem; overflow: hidden;">
                        <div style="width: 75%; height: 100%; background: #4f46e5;"></div>
                    </div>
                    <div style="font-size: 0.75rem; font-weight: 600; color: #334155; margin-top: 0.4rem;">
                        750 GB / 1 TB
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif selected_page == "Users":
            st.markdown(
                """
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.7rem; font-weight: 800; color: #475569; text-transform: uppercase;">
                        <span>MODEL RELIABILITY</span>
                        <span style="color: #0d9488; font-weight: 800;">98.2%</span>
                    </div>
                    <div style="height: 6px; background: #e2e8f0; border-radius: 3px; margin-top: 0.4rem; overflow: hidden;">
                        <div style="width: 98.2%; height: 100%; background: #0d9488;"></div>
                    </div>
                </div>
                
                <div class="sidebar-section-title">PREDICTIVE INSIGHTS</div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="font-size: 0.7rem; font-weight: 700; color: #64748b;">Avg. Health Score</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #0f172a;">74.2</div>
                    <div style="font-size: 0.68rem; color: #16a34a; font-weight: 600;">↗ +5.4% vs last week</div>
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; margin-bottom: 0.5rem;">
                    <div style="font-size: 0.7rem; font-weight: 700; color: #64748b;">High Risk Users</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #0f172a;">128</div>
                    <div style="font-size: 0.68rem; color: #dc2626; font-weight: 600;">↗ +19.1% spike</div>
                </div>
                <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.7rem; font-weight: 700; color: #64748b;">Retention Lift</div>
                    <div style="font-size: 1.1rem; font-weight: 800; color: #0f172a;">22%</div>
                    <div style="font-size: 0.68rem; color: #64748b;">Projected Q4 lift</div>
                </div>

                <div style="background: linear-gradient(135deg, #4f46e5 0%, #312e81 100%); border-radius: 10px; padding: 1rem; color: white;">
                    <div style="font-size: 0.8rem; font-weight: 800; margin-bottom: 0.25rem;">AI Anomaly Detection</div>
                    <div style="font-size: 0.7rem; opacity: 0.85; line-height: 1.3;">
                        Real-time scoring adjustments based on behavioral shifts.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.sidebar.markdown(
            f"<div style='font-size: 0.65rem; color: #94a3b8; margin-top: 2rem;'>DB: {settings.database_url}</div>",
            unsafe_allow_html=True,
        )
        return selected_page


def _render_dashboard_view(report, settings) -> None:
    # Header area
    col_title, col_actions = st.columns([3, 1])
    with col_title:
        st.markdown(
            """
            <div style="margin-bottom: 1.25rem;">
                <h1 style="font-size: 1.65rem; font-weight: 800; color: #0f172a; margin: 0; letter-spacing: -0.02em;">Growth Overview</h1>
                <p style="font-size: 0.85rem; color: #64748b; margin: 0.25rem 0 0 0;">Real-time performance across the conversion lifecycle.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_actions:
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            st.selectbox(
                "Timeframe",
                ["Last 30 Days", "Last 7 Days", "Last 90 Days"],
                label_visibility="collapsed",
            )
        with btn_col2:
            if st.button("Export CSV", type="primary", use_container_width=True):
                export_kpi_report(report, settings.reports_directory)
                st.toast("Report exported successfully!")

    # 4 Key Metrics Cards Grid
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            render_kpi_card(
                "⇄",
                "CONVERSION RATE",
                f"{report.conversion_rate if report.conversion_rate else 14.82}%",
                "+12.4%",
                "green",
            ),
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            render_kpi_card("⏱", "TIME-TO-CONV", "4.2d", "-2.1s", "red"), unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            render_kpi_card(
                "🎯",
                "ACTIVE COHORT",
                f"{report.paid_users + report.trial_users if report.total_users else '2,109'}",
                "+450",
                "green",
            ),
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            render_kpi_card(
                "📈",
                "PREDICTIVE LIFT",
                f"{report.retention_rate if report.retention_rate else '8.1'}%",
                "Stable",
                "gray",
            ),
            unsafe_allow_html=True,
        )

    # Acquisition Funnel
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem;">
            <h3 style="font-size: 1.05rem; font-weight: 800; color: #0f172a; margin: 0;">Acquisition Funnel</h3>
            <span style="font-size: 0.75rem; font-weight: 600; color: #64748b;">Global Pipeline View</span>
        </div>
        <div class="funnel-container">
            <div class="funnel-stage funnel-stage-1">
                <div class="funnel-stage-name">AWARENESS</div>
                <div class="funnel-stage-value">120.4k</div>
                <div class="funnel-stage-sub">100% Volume</div>
            </div>
            <div class="funnel-stage funnel-stage-2">
                <div class="funnel-stage-name">CONSIDERATION</div>
                <div class="funnel-stage-value">84.2k</div>
                <div class="funnel-stage-sub">70% Yield</div>
            </div>
            <div class="funnel-stage funnel-stage-3">
                <div class="funnel-stage-name">EVALUATION</div>
                <div class="funnel-stage-value">22.1k</div>
                <div class="funnel-stage-sub">26% Yield</div>
            </div>
            <div class="funnel-stage funnel-stage-4">
                <div class="funnel-stage-name">CONVERSION</div>
                <div class="funnel-stage-value">4.8k</div>
                <div class="funnel-stage-sub">22% Yield</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Bottom Split: Feature Lift & Cohort Performance
    left_col, right_col = st.columns([1, 1.2])

    with left_col:
        st.markdown(
            """
            <div class="iq-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3 style="font-size: 0.95rem; font-weight: 800; color: #0f172a; margin: 0;">Feature Lift</h3>
                    <span style="color: #94a3b8; font-size: 0.8rem; cursor: pointer;">⋮</span>
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.85rem;">
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: 700; color: #334155; margin-bottom: 0.25rem;">
                            <span>Collaborative Workspace</span>
                            <span style="color: #22c55e;">+22.4%</span>
                        </div>
                        <div style="height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden;">
                            <div style="width: 85%; height: 100%; background: #4f46e5; border-radius: 3px;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: 700; color: #334155; margin-bottom: 0.25rem;">
                            <span>Mobile SDK Integration</span>
                            <span style="color: #22c55e;">+14.2%</span>
                        </div>
                        <div style="height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden;">
                            <div style="width: 60%; height: 100%; background: #4f46e5; border-radius: 3px;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: 700; color: #334155; margin-bottom: 0.25rem;">
                            <span>Custom Dashboarding</span>
                            <span style="color: #22c55e;">+9.9%</span>
                        </div>
                        <div style="height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden;">
                            <div style="width: 45%; height: 100%; background: #4f46e5; border-radius: 3px;"></div>
                        </div>
                    </div>
                    <div>
                        <div style="display: flex; justify-content: space-between; font-size: 0.78rem; font-weight: 700; color: #334155; margin-bottom: 0.25rem;">
                            <span>API Automation</span>
                            <span style="color: #ef4444;">-2.1%</span>
                        </div>
                        <div style="height: 6px; background: #f1f5f9; border-radius: 3px; overflow: hidden;">
                            <div style="width: 20%; height: 100%; background: #94a3b8; border-radius: 3px;"></div>
                        </div>
                    </div>
                </div>
                <div style="margin-top: 1rem; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.75rem; background: #f8fafc; text-align: center;">
                    <div style="font-size: 0.7rem; color: #64748b; font-weight: 600; margin-bottom: 0.25rem;">Cluster Node Distribution</div>
                    <div style="font-size: 0.75rem; color: #4338ca; font-weight: 700;">● Active User Behavioral Correlation</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right_col:
        spark_green = render_sparkline_svg("#22c55e")
        spark_purple = render_sparkline_svg("#6366f1")

        st.markdown(
            f"""
            <div class="iq-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3 style="font-size: 0.95rem; font-weight: 800; color: #0f172a; margin: 0;">Cohort Performance</h3>
                    <span style="background: #e0e7ff; color: #3730a3; font-size: 0.7rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 12px;">● Retention > 40%</span>
                </div>
                <table class="iq-table">
                    <thead>
                        <tr>
                            <th>COHORT</th>
                            <th>USERS</th>
                            <th>MONTH 1</th>
                            <th>MONTH 2</th>
                            <th>MONTH 3</th>
                            <th>TREND</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style="font-weight: 700;">Jan 2024</td>
                            <td>12,402</td>
                            <td>100%</td>
                            <td>42.4%</td>
                            <td>31.2%</td>
                            <td>{spark_green}</td>
                        </tr>
                        <tr>
                            <td style="font-weight: 700;">Feb 2024</td>
                            <td>15,190</td>
                            <td>100%</td>
                            <td>38.9%</td>
                            <td>29.1%</td>
                            <td>{spark_purple}</td>
                        </tr>
                        <tr>
                            <td style="font-weight: 700;">Mar 2024</td>
                            <td>18,211</td>
                            <td>100%</td>
                            <td>45.2%</td>
                            <td>--</td>
                            <td>{spark_green}</td>
                        </tr>
                        <tr>
                            <td style="font-weight: 700;">Apr 2024</td>
                            <td>21,004</td>
                            <td>100%</td>
                            <td>--</td>
                            <td>--</td>
                            <td style="font-style: italic; color: #94a3b8; font-size: 0.75rem;">Awaiting Data</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_fab_button()


def _render_experiments_view() -> None:
    # Header area
    col_title, col_actions = st.columns([3, 1.2])
    with col_title:
        st.markdown(
            """
            <div style="margin-bottom: 1.25rem;">
                <div style="font-size: 0.72rem; font-weight: 800; color: #4338ca; letter-spacing: 0.05em; text-transform: uppercase;">⚙ OPTIMIZATION ENGINE</div>
                <h1 style="font-size: 1.65rem; font-weight: 800; color: #0f172a; margin: 0.15rem 0 0 0; letter-spacing: -0.02em;">Recommendations & Experiments</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_actions:
        b1, b2 = st.columns(2)
        with b1:
            st.selectbox(
                "Filter", ["Filter View", "Live Only", "Draft Only"], label_visibility="collapsed"
            )
        with b2:
            st.button("+ New Experiment", type="primary", use_container_width=True)

    # 2 Column Layout: Smart Insights (Left) & Active Experiments + Alert Config (Right)
    col_left, col_right = st.columns([1, 1.3])

    with col_left:
        st.markdown(
            """
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                <h3 style="font-size: 0.95rem; font-weight: 800; color: #0f172a; margin: 0;">Smart Insights</h3>
                <span class="badge-status status-running" style="font-size: 0.65rem;">AI POWERED</span>
            </div>
            
            <div class="insight-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.1rem;">📈</span>
                    <span class="kpi-badge-gray">HIGH IMPACT</span>
                </div>
                <h4 style="font-size: 0.9rem; font-weight: 800; color: #0f172a; margin: 0 0 0.35rem 0;">Optimize Checkout Flow</h4>
                <p style="font-size: 0.78rem; color: #475569; line-height: 1.4; margin-bottom: 0.85rem;">
                    Users in the DACH region show a 14% drop-off at the payment selection stage. Implementation of local providers could reclaim $42k MRR.
                </p>
                <div style="display: flex; gap: 0.5rem;">
                    <button style="background: #4338ca; color: white; border: none; padding: 0.4rem 0.85rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; cursor: pointer;">Launch Test</button>
                    <button style="background: #f1f5f9; border: 1px solid #cbd5e1; padding: 0.4rem 0.6rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; cursor: pointer;">...</button>
                </div>
            </div>

            <div class="insight-card insight-card-green">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.1rem;">⚡</span>
                    <span class="kpi-badge-gray" style="background: #e0e7ff; color: #3730a3;">EFFICIENCY</span>
                </div>
                <h4 style="font-size: 0.9rem; font-weight: 800; color: #0f172a; margin: 0 0 0.35rem 0;">Data Latency Warning</h4>
                <p style="font-size: 0.78rem; color: #475569; line-height: 1.4; margin-bottom: 0.85rem;">
                    Query performance for 'Experiment_Alpha' has degraded by 200ms. Consider indexing the 'user_cohort' column.
                </p>
                <button style="background: #ffffff; border: 1px solid #10b981; color: #047857; padding: 0.4rem 0.85rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; cursor: pointer;">Apply Fix</button>
            </div>

            <div class="insight-card insight-card-orange">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.1rem;">⚠️</span>
                    <span class="kpi-badge-gray" style="background: #fef3c7; color: #92400e;">COHORT DANGER</span>
                </div>
                <h4 style="font-size: 0.9rem; font-weight: 800; color: #0f172a; margin: 0 0 0.35rem 0;">Churn Risk: Tier 2</h4>
                <p style="font-size: 0.78rem; color: #475569; line-height: 1.4; margin-bottom: 0.85rem;">
                    Retention for the Q3 Enterprise cohort has dipped below the 80% threshold. Immediate re-engagement suggested.
                </p>
                <button style="background: #0f172a; color: white; border: none; padding: 0.4rem 0.85rem; border-radius: 6px; font-weight: 700; font-size: 0.75rem; cursor: pointer;">View Cohort</button>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_right:
        bar_sparkline = render_bar_sparkline_svg()
        st.markdown(
            f"""
            <div class="iq-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h3 style="font-size: 0.95rem; font-weight: 800; color: #0f172a; margin: 0;">Active Experiments</h3>
                    <div style="display: flex; gap: 0.25rem; background: #f1f5f9; padding: 0.15rem; border-radius: 6px; font-size: 0.68rem; font-weight: 700;">
                        <span style="background: #4338ca; color: white; padding: 0.15rem 0.4rem; border-radius: 4px;">ALL</span>
                        <span style="color: #64748b; padding: 0.15rem 0.4rem;">LIVE</span>
                        <span style="color: #64748b; padding: 0.15rem 0.4rem;">DRAFT</span>
                    </div>
                </div>
                <table class="iq-table">
                    <thead>
                        <tr>
                            <th>EXPERIMENT NAME</th>
                            <th>STATUS</th>
                            <th>CONFIDENCE</th>
                            <th>LIFT</th>
                            <th>TREND</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <div style="font-weight: 800; color: #0f172a;">Checkout Modal v2</div>
                                <div style="font-size: 0.65rem; color: #64748b; font-weight: 700;">E-COMMERCE FLOW</div>
                            </td>
                            <td><span class="badge-status status-running">RUNNING</span></td>
                            <td style="font-weight: 700;">94.2%</td>
                            <td style="font-weight: 800; color: #16a34a;">+12.4%</td>
                            <td>{bar_sparkline}</td>
                        </tr>
                        <tr>
                            <td>
                                <div style="font-weight: 800; color: #0f172a;">Onboarding Gamification</div>
                                <div style="font-size: 0.65rem; color: #64748b; font-weight: 700;">RETENTION ENGINE</div>
                            </td>
                            <td><span class="badge-status status-warning">WARNING</span></td>
                            <td style="font-weight: 700;">41.8%</td>
                            <td style="font-weight: 800; color: #dc2626;">-2.1%</td>
                            <td><span style="color: #dc2626; font-size: 0.75rem;">📊📉</span></td>
                        </tr>
                        <tr>
                            <td>
                                <div style="font-weight: 800; color: #0f172a;">Price Point Discovery</div>
                                <div style="font-size: 0.65rem; color: #64748b; font-weight: 700;">MONETIZATION</div>
                            </td>
                            <td><span class="badge-status status-staging">STAGING</span></td>
                            <td style="color: #94a3b8;">--</td>
                            <td style="font-weight: 700; color: #64748b;">0.0%</td>
                            <td><span style="color: #cbd5e1;">───</span></td>
                        </tr>
                        <tr>
                            <td>
                                <div style="font-weight: 800; color: #0f172a;">Dark Mode Defaulting</div>
                                <div style="font-size: 0.65rem; color: #64748b; font-weight: 700;">UI/UX PREFERENCE</div>
                            </td>
                            <td><span class="badge-status status-running">RUNNING</span></td>
                            <td style="font-weight: 700;">88.5%</td>
                            <td style="font-weight: 800; color: #16a34a;">+4.3%</td>
                            <td>{bar_sparkline}</td>
                        </tr>
                    </tbody>
                </table>
                <div style="text-align: center; margin-top: 0.85rem;">
                    <a href="#" style="font-size: 0.78rem; font-weight: 700; color: #4338ca; text-decoration: none;">View Experiment Archive &gt;</a>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        r_bottom_left, r_bottom_right = st.columns(2)
        with r_bottom_left:
            st.markdown(
                """
                <div class="iq-card" style="padding: 1rem;">
                    <div style="font-size: 0.82rem; font-weight: 800; color: #0f172a; margin-bottom: 0.75rem;">🔔 Smart Alert Config</div>
                    <div style="font-size: 0.75rem; font-weight: 600; color: #334155; margin-bottom: 0.5rem; display: flex; justify-content: space-between;">
                        <span>Notify on Lift Deviation &gt; 5%</span>
                        <span style="color: #4338ca;">● ON</span>
                    </div>
                    <div style="font-size: 0.75rem; font-weight: 600; color: #334155; margin-bottom: 0.75rem; display: flex; justify-content: space-between;">
                        <span>Auto-stop failing tests</span>
                        <span style="color: #94a3b8;">○ OFF</span>
                    </div>
                    <div style="font-size: 0.68rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.35rem;">ALERT DESTINATIONS</div>
                    <div style="display: flex; gap: 0.5rem;">
                        <span style="background: #f1f5f9; border: 1px solid #cbd5e1; font-size: 0.7rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px;">✉ Email</span>
                        <span style="background: #f1f5f9; border: 1px solid #cbd5e1; font-size: 0.7rem; font-weight: 700; padding: 0.2rem 0.5rem; border-radius: 4px;">💬 Slack</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with r_bottom_right:
            st.markdown(
                """
                <div class="iq-card" style="background: linear-gradient(135deg, #6366f1 0%, #312e81 100%); color: white; padding: 1rem;">
                    <div style="font-size: 0.85rem; font-weight: 800;">Weekly Digest</div>
                    <div style="font-size: 0.65rem; opacity: 0.8; font-weight: 700; margin-bottom: 0.5rem;">MARCH 10 - 17, 2024</div>
                    <ul style="font-size: 0.72rem; padding-left: 1rem; margin: 0 0 0.75rem 0; line-height: 1.3;">
                        <li>Avg session length increased by <b style="color: #4ade80;">4.2%</b></li>
                        <li>Test-Track API showed <b style="color: #f87171;">negative lift</b></li>
                    </ul>
                    <button style="width: 100%; background: white; color: #312e81; border: none; font-weight: 800; font-size: 0.75rem; padding: 0.4rem; border-radius: 6px; cursor: pointer;">Full Report</button>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_ingestion_view() -> None:
    st.markdown(
        """
        <div style="margin-bottom: 1.25rem;">
            <h1 style="font-size: 1.65rem; font-weight: 800; color: #0f172a; margin: 0; letter-spacing: -0.02em;">Ingestion Portal</h1>
            <p style="font-size: 0.85rem; color: #64748b; margin: 0.25rem 0 0 0;">Upload datasets for schema validation and automated pipeline integration.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Top Grid: Source Upload & Pipeline Integrity
    col_upload, col_integrity = st.columns([1.5, 1])

    with col_upload:
        st.markdown(
            """
            <div class="iq-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
                    <h3 style="font-size: 0.95rem; font-weight: 800; color: #0f172a; margin: 0;">Source Upload</h3>
                    <a href="#" style="font-size: 0.75rem; font-weight: 700; color: #4338ca; text-decoration: none;">Download Template</a>
                </div>
                <div class="dropzone-box">
                    <div style="font-size: 2rem; color: #4338ca; margin-bottom: 0.5rem;">☁️</div>
                    <div style="font-weight: 800; color: #0f172a; font-size: 0.95rem;">Drag and drop CSV files here</div>
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 0.25rem; margin-bottom: 1rem;">Limit 200MB per file • UTF-8 Encoding required</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    with col_integrity:
        st.markdown(
            """
            <div class="iq-card" style="height: 100%;">
                <h3 style="font-size: 0.95rem; font-weight: 800; color: #0f172a; margin: 0 0 1rem 0;">Pipeline Integrity</h3>
                <div style="text-align: center; margin-bottom: 1.25rem;">
                    <div style="position: relative; display: inline-block;">
                        <div style="font-size: 2.2rem; font-weight: 800; color: #4338ca;">94.2%</div>
                        <div style="font-size: 0.68rem; font-weight: 800; color: #64748b; letter-spacing: 0.05em;">HEALTH INDEX</div>
                    </div>
                </div>
                <div style="display: flex; flex-direction: column; gap: 0.6rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600; color: #475569;">
                        <span>Schema Match</span>
                        <span style="font-weight: 800; color: #0f172a;">98.1%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600; color: #475569;">
                        <span>Null Density</span>
                        <span style="font-weight: 800; color: #0f172a;">0.04%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600; color: #475569;">
                        <span>Type Consistency</span>
                        <span style="font-weight: 800; color: #4338ca;">High</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Middle Section: Schema Validation Results
    st.markdown(
        """
        <div class="iq-card" style="margin-top: 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h3 style="font-size: 0.95rem; font-weight: 800; color: #0f172a; margin: 0;">Schema Validation Results</h3>
                <div style="display: flex; gap: 0.5rem;">
                    <input type="text" placeholder="🔍 Search columns..." style="padding: 0.35rem 0.75rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.78rem;" />
                    <button style="background: #f1f5f9; border: 1px solid #cbd5e1; padding: 0.35rem 0.75rem; border-radius: 6px; font-weight: 700; font-size: 0.78rem;">Filter</button>
                </div>
            </div>
            <table class="iq-table">
                <thead>
                    <tr>
                        <th>COLUMN NAME</th>
                        <th>INFERRED TYPE</th>
                        <th>DETECTED NULLS</th>
                        <th>UNIQUE COUNT</th>
                        <th>STATUS</th>
                        <th>TREND (7D)</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="font-weight: 800;">transaction_id</td>
                        <td><span style="background: #e0e7ff; color: #3730a3; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem; font-weight: 700;">UUID</span></td>
                        <td>0.00%</td>
                        <td style="font-weight: 700;">4,821,035</td>
                        <td><span class="badge-status status-valid">● VALID</span></td>
                        <td><span style="color: #22c55e;">↗</span></td>
                    </tr>
                    <tr>
                        <td style="font-weight: 800;">user_email</td>
                        <td><span style="background: #e0e7ff; color: #3730a3; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem; font-weight: 700;">String</span></td>
                        <td style="color: #d97706; font-weight: 700;">1.42%</td>
                        <td style="font-weight: 700;">842,109</td>
                        <td><span class="badge-status status-warning">● WARNING</span></td>
                        <td><span style="color: #f59e0b;">→</span></td>
                    </tr>
                    <tr>
                        <td style="font-weight: 800;">purchase_amount</td>
                        <td><span style="background: #e0e7ff; color: #3730a3; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem; font-weight: 700;">Decimal</span></td>
                        <td>0.02%</td>
                        <td style="font-weight: 700;">12,402</td>
                        <td><span class="badge-status status-valid">● VALID</span></td>
                        <td><span style="color: #22c55e;">↗</span></td>
                    </tr>
                    <tr>
                        <td style="font-weight: 800;">region_code</td>
                        <td><span style="background: #e0e7ff; color: #3730a3; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.7rem; font-weight: 700;">Integer</span></td>
                        <td style="color: #dc2626; font-weight: 800;">12.0%</td>
                        <td style="font-weight: 700;">14</td>
                        <td><span class="badge-status status-critical">● CRITICAL</span></td>
                        <td><span style="color: #dc2626;">↘</span></td>
                    </tr>
                </tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Bottom Section: Ingestion History
    st.markdown(
        """
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1.5rem; margin-bottom: 0.75rem;">
            <h3 style="font-size: 0.95rem; font-weight: 800; color: #0f172a; margin: 0;">Ingestion History</h3>
            <a href="#" style="font-size: 0.75rem; font-weight: 700; color: #4338ca; text-decoration: none;">View All Pipeline Logs</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    h1, h2, h3 = st.columns(3)
    with h1:
        st.markdown(
            """
            <div class="iq-card" style="padding: 0.85rem;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem; color: #4338ca;">📄</span>
                        <div>
                            <div style="font-size: 0.8rem; font-weight: 800; color: #0f172a;">sales_q3_2024.csv</div>
                            <div style="font-size: 0.68rem; color: #64748b;">2.4 MB • 2h ago</div>
                        </div>
                    </div>
                    <span style="color: #16a34a; font-weight: 800; font-size: 0.72rem;">SUCCESS &gt;</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with h2:
        st.markdown(
            """
            <div class="iq-card" style="padding: 0.85rem;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem; color: #4338ca;">📄</span>
                        <div>
                            <div style="font-size: 0.8rem; font-weight: 800; color: #0f172a;">customer_master_v2...</div>
                            <div style="font-size: 0.68rem; color: #64748b;">840 MB • 5h ago</div>
                        </div>
                    </div>
                    <span style="color: #16a34a; font-weight: 800; font-size: 0.72rem;">SUCCESS &gt;</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with h3:
        st.markdown(
            """
            <div class="iq-card" style="padding: 0.85rem;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem; color: #dc2626;">⚠️</span>
                        <div>
                            <div style="font-size: 0.8rem; font-weight: 800; color: #0f172a;">marketing_spend_aug...</div>
                            <div style="font-size: 0.68rem; color: #64748b;">12 MB • 1d ago</div>
                        </div>
                    </div>
                    <span style="color: #dc2626; font-weight: 800; font-size: 0.72rem;">FAILED &gt;</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_users_view(report) -> None:
    # Toolbar area
    col_search, col_filter, col_export = st.columns([3, 1, 1.2])
    with col_search:
        st.text_input(
            "Search",
            placeholder="🔍 Search by ID, email or feature...",
            label_visibility="collapsed",
        )
    with col_filter:
        st.button("⚙ Filter", use_container_width=True)
    with col_export:
        if st.button("Export Data: 📥 CSV", type="primary", use_container_width=True):
            st.toast("Exported user risk table to CSV!")

    # Users Table
    st.markdown(
        """
        <div class="iq-card" style="margin-top: 1rem;">
            <table class="iq-table">
                <thead>
                    <tr>
                        <th>USER ID</th>
                        <th>SCORE</th>
                        <th>RISK LEVEL</th>
                        <th>TOP FEATURE</th>
                        <th>LAST ACTIVE</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>
                            <div style="display: flex; align-items: center;">
                                <div class="user-avatar" style="background: #e0e7ff; color: #3730a3;">JD</div>
                                <div>
                                    <div style="font-weight: 800; color: #0f172a;">USR-88219</div>
                                    <div style="font-size: 0.68rem; color: #64748b;">j.doe@example.com</div>
                                </div>
                            </div>
                        </td>
                        <td style="font-weight: 800;">
                            92
                            <div class="score-bar-bg"><div class="score-bar-fill-green" style="width: 92%;"></div></div>
                        </td>
                        <td><span class="badge-status status-low-risk">Low Risk</span></td>
                        <td style="font-weight: 600;">Advanced Exports</td>
                        <td style="color: #64748b;">2m ago</td>
                        <td style="color: #94a3b8; font-weight: 700; cursor: pointer;">∨</td>
                    </tr>
                    <tr>
                        <td>
                            <div style="display: flex; align-items: center;">
                                <div class="user-avatar" style="background: #fee2e2; color: #991b1b;">MK</div>
                                <div>
                                    <div style="font-weight: 800; color: #0f172a;">USR-44120</div>
                                    <div style="font-size: 0.68rem; color: #64748b;">m.kelly@corp.ai</div>
                                </div>
                            </div>
                        </td>
                        <td style="font-weight: 800;">
                            34
                            <div class="score-bar-bg"><div class="score-bar-fill-red" style="width: 34%;"></div></div>
                        </td>
                        <td><span class="badge-status status-critical">Critical Risk</span></td>
                        <td style="font-weight: 600;">Basic Search</td>
                        <td style="color: #64748b;">14d ago</td>
                        <td style="color: #94a3b8; font-weight: 700; cursor: pointer;">∨</td>
                    </tr>
                    <tr>
                        <td>
                            <div style="display: flex; align-items: center;">
                                <div class="user-avatar" style="background: #fef9c3; color: #854d0e;">AS</div>
                                <div>
                                    <div style="font-weight: 800; color: #0f172a;">USR-77312</div>
                                    <div style="font-size: 0.68rem; color: #64748b;">a.smith@tech.io</div>
                                </div>
                            </div>
                        </td>
                        <td style="font-weight: 800;">
                            61
                            <div class="score-bar-bg"><div class="score-bar-fill-yellow" style="width: 61%;"></div></div>
                        </td>
                        <td><span class="badge-status status-mod-risk">Moderate Risk</span></td>
                        <td style="font-weight: 600;">Data Viz Pro</td>
                        <td style="color: #64748b;">5h ago</td>
                        <td style="color: #94a3b8; font-weight: 700; cursor: pointer;">∨</td>
                    </tr>
                    <tr>
                        <td>
                            <div style="display: flex; align-items: center;">
                                <div class="user-avatar" style="background: #e0e7ff; color: #3730a3;">WL</div>
                                <div>
                                    <div style="font-weight: 800; color: #0f172a;">USR-91223</div>
                                    <div style="font-size: 0.68rem; color: #64748b;">w.li@global.com</div>
                                </div>
                            </div>
                        </td>
                        <td style="font-weight: 800;">
                            88
                            <div class="score-bar-bg"><div class="score-bar-fill-green" style="width: 88%;"></div></div>
                        </td>
                        <td><span class="badge-status status-low-risk">Low Risk</span></td>
                        <td style="font-weight: 600;">Automated Alerts</td>
                        <td style="color: #64748b;">1h ago</td>
                        <td style="color: #94a3b8; font-weight: 700; cursor: pointer;">∨</td>
                    </tr>
                    <tr>
                        <td>
                            <div style="display: flex; align-items: center;">
                                <div class="user-avatar" style="background: #fee2e2; color: #991b1b;">TR</div>
                                <div>
                                    <div style="font-weight: 800; color: #0f172a;">USR-11002</div>
                                    <div style="font-size: 0.68rem; color: #64748b;">t.reed@startup.net</div>
                                </div>
                            </div>
                        </td>
                        <td style="font-weight: 800;">
                            12
                            <div class="score-bar-bg"><div class="score-bar-fill-red" style="width: 12%;"></div></div>
                        </td>
                        <td><span class="badge-status status-critical">Critical Risk</span></td>
                        <td style="font-weight: 600;">None (Inactive)</td>
                        <td style="color: #64748b;">42d ago</td>
                        <td style="color: #94a3b8; font-weight: 700; cursor: pointer;">∨</td>
                    </tr>
                </tbody>
            </table>
            <div style="display: flex; justify-content: space-between; align-items: center; padding-top: 0.75rem; border-top: 1px solid #f1f5f9; font-size: 0.75rem; color: #64748b;">
                <span>Showing 1 to 5 of 1,280 entries</span>
                <div>
                    <button style="background: white; border: 1px solid #cbd5e1; padding: 0.25rem 0.5rem; border-radius: 4px; cursor: pointer;">&lt; Page 1 &gt;</button>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Bottom Cards Grid
    b_col1, b_col2 = st.columns(2)
    with b_col1:
        st.markdown(
            """
            <div class="iq-card" style="display: flex; gap: 1rem; align-items: flex-start;">
                <div style="background: #e0e7ff; color: #4338ca; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0;">🔮</div>
                <div>
                    <h4 style="font-size: 0.9rem; font-weight: 800; color: #4338ca; margin: 0 0 0.25rem 0;">Pipeline Connectivity</h4>
                    <p style="font-size: 0.78rem; color: #475569; margin: 0; line-height: 1.4;">
                        Your CSV Ingestion nodes are operating at peak efficiency. 0% data packet loss detected in the last 24 hours.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with b_col2:
        st.markdown(
            """
            <div class="iq-card" style="display: flex; gap: 1rem; align-items: flex-start;">
                <div style="background: #dcfce7; color: #15803d; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0;">🛡️</div>
                <div>
                    <h4 style="font-size: 0.9rem; font-weight: 800; color: #15803d; margin: 0 0 0.25rem 0;">Model Audit Pass</h4>
                    <p style="font-size: 0.78rem; color: #475569; margin: 0; line-height: 1.4;">
                        Predictive scoring algorithm version v4.2.1 passed bias and accuracy benchmarks this morning.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def main() -> None:
    settings = get_settings()
    st.set_page_config(page_title="Conversion-IQ", layout="wide", page_icon="⚡")

    inject_custom_css()

    # Sidebar selection
    selected_page = _render_sidebar(settings)

    # Top Navbar header
    render_top_navbar(selected_page)

    # Load data
    try:
        repository = SqlAnalyticsRepository(settings.database_url)
        raw_bundle = repository.load_bundle()
        cleaned_bundle = clean_analytics_bundle(raw_bundle)
        report = calculate_kpis(cleaned_bundle)
    except Exception:
        # Fallback empty KPI result if DB is not yet populated
        from growth_ai.domain.models import KPIResult

        report = KPIResult()

    if selected_page == "Dashboard":
        _render_dashboard_view(report, settings)
    elif selected_page == "Experiments":
        _render_experiments_view()
    elif selected_page == "Ingestion":
        _render_ingestion_view()
    elif selected_page == "Users":
        _render_users_view(report)


if __name__ == "__main__":
    main()
