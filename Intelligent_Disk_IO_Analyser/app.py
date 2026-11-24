import streamlit as st
import pandas as pd

from reports.pdf_report import generate_pdf_report
from algorithms.disk_algorithms import run_algorithm
from core.metrics import calculate_metrics
from core.recommender import recommend_algorithm
from visualisation.charts import (
    create_movement_chart,
    create_performance_chart,
    create_ranking_chart,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Intelligent Disk I/O Analyser",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# DESIGN SYSTEM
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700;800;900&family=Outfit:wght@500;600;700;800;900&display=swap');

    :root {
        --app-bg: #F4F8EF;
        --surface: #FFFFFF;
        --surface-soft: #EAF3E3;
        --sidebar: #173D30;
        --text: #203D2F;
        --muted: #718477;
        --primary: #4E9566;
        --primary-dark: #2F704A;
        --lime: #C6E58C;
        --mint: #DDF0D9;
        --border: #DCE8D7;
    }

    html, body, [class*="css"] {
        font-family: 'Nunito', sans-serif;
    }

    .stApp, [data-testid="stMain"] {
        background:
            radial-gradient(circle at 95% 7%, rgba(197, 226, 157, .30), transparent 22rem),
            radial-gradient(circle at 4% 65%, rgba(210, 236, 210, .34), transparent 25rem),
            var(--app-bg);
        color: var(--text);
    }

    [data-testid="stHeader"] {
        background: rgba(244, 248, 239, .88);
        backdrop-filter: blur(12px);
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 2.7rem;
    }

    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background: linear-gradient(160deg, #173D30 0%, #20563D 62%, #2E704C 100%);
        border-right: 1px solid #2E6548;
    }

    section[data-testid="stSidebar"] * { color: #F5FBF1; }

    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    section[data-testid="stSidebar"] label {
        color: #C7DDC7 !important;
    }

    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #FFFFFF !important;
        font-family: 'Outfit', sans-serif;
    }

    section[data-testid="stSidebar"] [data-testid="stRadio"] > label {
        color: #C7DDC7 !important;
        font-size: .73rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .13em;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] { gap: .42rem; }

    section[data-testid="stSidebar"] [role="radiogroup"] label {
        background: rgba(255,255,255,.035);
        border: 1px solid transparent;
        border-radius: 999px;
        padding: .55rem .85rem;
        transition: all .2s ease;
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(221,245,221,.13);
        border-color: rgba(221,245,221,.18);
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: #DDF0D9;
        border: 1px solid #DDF0D9;
        box-shadow: 0 5px 16px rgba(0,0,0,.12);
    }

    section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) * {
        color: #174631 !important;
        font-weight: 900;
    }

    section[data-testid="stSidebar"] [data-testid="stNumberInput"] input,
    section[data-testid="stSidebar"] [data-testid="stTextInput"] input,
    section[data-testid="stSidebar"] [data-testid="stTextArea"] textarea,
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] {
        background: #F8FCF5 !important;
        color: #203D2F !important;
        border: 1px solid #CFE0C8 !important;
        border-radius: 15px !important;
    }

    section[data-testid="stSidebar"] [data-testid="stNumberInput"] button {
        color: #203D2F !important;
        border-radius: 50% !important;
    }

    .sidebar-brand {
        padding: .45rem 0 1.2rem 0;
        border-bottom: 1px solid rgba(220,244,222,.2);
        margin-bottom: 1.25rem;
    }

    /* Preserve the leaf logo from the previous version */
    .sidebar-brand-mark {
        width: 62px;
        height: 62px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        background: linear-gradient(145deg, #DDF1D9, #A9D3AE);
        color: #174631;
        font-size: 1.85rem;
        line-height: 1;
        box-shadow: 0 7px 18px rgba(0,0,0,.16);
    }

    .sidebar-brand-name {
        color: #FFFFFF;
        font-family: 'Outfit', sans-serif;
        font-size: 1.08rem;
        font-weight: 900;
        margin-top: .75rem;
    }

    .sidebar-brand-caption {
        color: #C7DDC7;
        font-size: .74rem;
        margin-top: .22rem;
    }

    .sidebar-section {
        color: #F5FBF1;
        font-size: .84rem;
        font-weight: 900;
        margin: 1.3rem 0 .55rem 0;
    }

    .sidebar-help {
        color: #C7DDC7;
        font-size: .75rem;
        line-height: 1.6;
        margin-top: .65rem;
    }

    h1, h2, h3 {
        color: var(--text) !important;
        font-family: 'Outfit', sans-serif;
        letter-spacing: -.035em;
    }

    h1 { font-weight: 900 !important; }
    h2, h3 { font-weight: 800 !important; }
    p, li, span, label { color: inherit; }
    [data-testid="stMarkdownContainer"] p { color: var(--muted); }

    .page-eyebrow {
        display: inline-block;
        color: #347A55;
        background: #E2F0D8;
        border: 1px solid #CFE4C5;
        border-radius: 999px;
        padding: .34rem .85rem;
        font-size: .68rem;
        font-weight: 900;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin-bottom: .55rem;
    }

    .page-subtitle {
        color: var(--muted);
        font-size: .96rem;
        margin-top: -.35rem;
        margin-bottom: 1.45rem;
        line-height: 1.65;
    }

    .section-kicker {
        color: var(--muted);
        font-size: .74rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .1em;
        margin-bottom: .45rem;
    }

    .hero-card {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(circle at 92% 18%, rgba(216,244,163,.25), transparent 12rem),
            linear-gradient(115deg, #173F30 0%, #286A48 58%, #5A9B65 100%);
        border: 1px solid #3F8056;
        border-radius: 30px 30px 62px 30px;
        padding: 1.85rem 2rem;
        margin: .35rem 0 1.45rem 0;
        box-shadow: 0 13px 30px rgba(27,83,52,.16);
    }

    .hero-title {
        color: #F6FFF3;
        font-family: 'Outfit', sans-serif;
        font-size: 1.55rem;
        font-weight: 900;
        letter-spacing: -.04em;
        margin-bottom: .4rem;
    }

    .hero-copy {
        color: #DCEEDB;
        font-size: .92rem;
        line-height: 1.65;
        max-width: 760px;
    }

    .metric-shell, [data-testid="stMetric"] {
        background: linear-gradient(145deg, #FFFFFF 0%, #F4FAF0 100%);
        border: 1px solid #D9E8D4;
        border-radius: 25px 25px 42px 25px;
        padding: 1.05rem 1.1rem;
        box-shadow: 0 7px 20px rgba(36,83,52,.055);
        min-height: 112px;
    }

    [data-testid="stMetricLabel"] {
        color: #718477 !important;
        font-size: .79rem !important;
        font-weight: 800 !important;
    }

    [data-testid="stMetricValue"] {
        color: #24583D !important;
        font-family: 'Outfit', sans-serif;
        font-weight: 900 !important;
    }

    .recommendation-card {
        background:
            radial-gradient(circle at 95% 10%, rgba(185,222,145,.36), transparent 11rem),
            linear-gradient(120deg, #E4F2DC 0%, #FAFCF6 100%);
        border: 1px solid #C9DFC0;
        border-left: 6px solid #4E9566;
        border-radius: 24px 24px 45px 24px;
        padding: 1.35rem 1.55rem;
        margin: .7rem 0 1.1rem 0;
        box-shadow: 0 6px 18px rgba(36,83,52,.05);
    }

    .recommendation-label {
        color: #347A55;
        font-size: .72rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: .13em;
    }

    .recommendation-name {
        color: #1D6240;
        font-family: 'Outfit', sans-serif;
        font-size: 2rem;
        font-weight: 900;
        margin: .2rem 0 .3rem 0;
        letter-spacing: -.045em;
    }

    .recommendation-copy {
        color: #527660;
        font-size: .9rem;
        line-height: 1.6;
    }

    .info-strip {
        background: #FFFFFF;
        border: 1px solid #D8E8D8;
        border-radius: 22px 22px 38px 22px;
        padding: 1rem 1.1rem;
        color: #527064;
        font-size: .86rem;
        line-height: 1.65;
        box-shadow: 0 5px 15px rgba(36,83,52,.035);
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 999px !important;
        font-family: 'Nunito', sans-serif !important;
        font-weight: 900 !important;
        border: 1px solid #C7DEC9 !important;
        min-height: 2.85rem;
        padding: .48rem 1.45rem;
        transition: all .2s ease;
        box-shadow: 0 4px 12px rgba(38,91,55,.06);
    }

    div.stButton > button:hover,
    div.stDownloadButton > button:hover {
        border-color: #75AD81 !important;
        transform: translateY(-2px);
        box-shadow: 0 7px 16px rgba(38,91,55,.12);
    }

    div.stButton > button[kind="primary"],
    div.stDownloadButton > button[kind="primary"] {
        background: linear-gradient(110deg, #4E9566, #2F7650) !important;
        border-color: #438B62 !important;
        color: #FFFFFF !important;
    }

    div.stButton > button[kind="primary"]:hover,
    div.stDownloadButton > button[kind="primary"]:hover {
        background: #286B48 !important;
        border-color: #286B48 !important;
        color: #FFFFFF !important;
    }

    [data-testid="stTextInput"] input,
    [data-testid="stTextArea"] textarea,
    [data-testid="stNumberInput"] input,
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        border-radius: 15px !important;
        border-color: #CFE2D1 !important;
        background: #FCFEFB;
    }

    [data-testid="stNumberInput"] button { border-radius: 50% !important; }

    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        border: 1px solid #D8E8D8;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 5px 16px rgba(36,83,52,.04);
    }

    [data-testid="stAlert"] { border-radius: 18px; }

    [data-testid="stExpander"] {
        border: 1px solid #D8E8D8;
        border-radius: 18px;
        overflow: hidden;
    }

    /* Leafy: a tiny CSS mascot that gently bobs and points toward the simulator */
    .leafy-card {
        background: linear-gradient(155deg, #F0F8E9 0%, #FFFFFF 100%);
        border: 1px solid #D6E8CE;
        border-radius: 26px;
        min-height: 330px;
        padding: 1rem .8rem 1.1rem;
        text-align: center;
        box-shadow: 0 9px 22px rgba(45,95,56,.07);
        overflow: hidden;
        position: relative;
    }

    .leafy-card:before {
        content: "";
        position: absolute;
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: #E1F0D8;
        top: 48px;
        left: 50%;
        transform: translateX(-50%);
    }

    .leafy-caption {
        position: relative;
        z-index: 2;
        color: #39764D;
        font-size: .68rem;
        font-weight: 900;
        letter-spacing: .14em;
        text-transform: uppercase;
    }

    .leafy-stage {
        height: 220px;
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .leafy-person {
        position: relative;
        width: 142px;
        height: 196px;
        animation: leafy-bob 2.8s ease-in-out infinite;
        transform-origin: 50% 100%;
    }

    .leafy-head {
        position: absolute;
        width: 77px;
        height: 77px;
        top: 13px;
        left: 34px;
        border-radius: 52% 48% 50% 50%;
        background: linear-gradient(145deg, #A9D978, #5DA765);
        border: 4px solid #397F4E;
        box-shadow: inset -7px -7px 0 rgba(38,105,58,.10);
    }

    .leafy-head:before {
        content: "";
        position: absolute;
        width: 25px;
        height: 13px;
        background: #79B96D;
        border: 3px solid #397F4E;
        border-radius: 100% 0 100% 0;
        top: -12px;
        left: 30px;
        transform: rotate(-25deg);
    }

    .leafy-eye {
        position: absolute;
        width: 6px;
        height: 8px;
        border-radius: 50%;
        background: #214B35;
        top: 34px;
    }

    .leafy-eye.left { left: 21px; }
    .leafy-eye.right { right: 21px; }

    .leafy-smile {
        position: absolute;
        width: 18px;
        height: 9px;
        border-bottom: 2.5px solid #214B35;
        border-radius: 0 0 18px 18px;
        left: 27px;
        top: 48px;
    }

    .leafy-body {
        position: absolute;
        width: 62px;
        height: 75px;
        top: 88px;
        left: 41px;
        border-radius: 28px 28px 20px 20px;
        background: linear-gradient(145deg, #5EAA69, #28734B);
        border: 3px solid #286441;
    }

    .leafy-body:after {
        content: "✦";
        color: #DDF0C7;
        position: absolute;
        font-size: 18px;
        top: 22px;
        left: 20px;
    }

    .leafy-arm {
        position: absolute;
        width: 48px;
        height: 13px;
        top: 103px;
        left: 5px;
        border-radius: 999px;
        background: #67AD6D;
        border: 3px solid #286441;
        transform: rotate(-28deg);
        transform-origin: right center;
        animation: leafy-point 2.8s ease-in-out infinite;
    }

    .leafy-arm:after {
        content: "";
        position: absolute;
        width: 17px;
        height: 10px;
        right: -12px;
        top: -1px;
        border-radius: 999px;
        background: #8ACB78;
        border: 2px solid #286441;
    }

    .leafy-arm.other {
        left: 91px;
        top: 105px;
        width: 39px;
        transform: rotate(35deg);
        animation: leafy-wave 2.8s ease-in-out infinite;
    }

    .leafy-leg {
        position: absolute;
        width: 16px;
        height: 36px;
        top: 153px;
        left: 48px;
        border-radius: 999px;
        background: #397F54;
        border: 2px solid #286441;
    }

    .leafy-leg.right { left: 79px; }

    .leafy-foot {
        position: absolute;
        width: 25px;
        height: 12px;
        top: 182px;
        left: 39px;
        border-radius: 999px 999px 8px 8px;
        background: #285D40;
    }

    .leafy-foot.right { left: 74px; }

    .leafy-message {
        position: relative;
        z-index: 2;
        color: #557460;
        font-size: .83rem;
        line-height: 1.5;
        font-weight: 700;
        margin: -.1rem auto 0;
        max-width: 230px;
    }

    .leafy-message strong { color: #286B48; }

    @keyframes leafy-bob {
        0%, 100% { transform: translateY(0) rotate(-1deg); }
        50% { transform: translateY(-7px) rotate(1deg); }
    }

    @keyframes leafy-point {
        0%, 100% { transform: rotate(-28deg); }
        50% { transform: rotate(-42deg); }
    }

    @keyframes leafy-wave {
        0%, 100% { transform: rotate(35deg); }
        50% { transform: rotate(52deg); }
    }

    .app-footer {
        border-top: 1px solid #D8E8D8;
        margin-top: 2.6rem;
        padding-top: 1.1rem;
        color: #8AA495;
        font-size: .75rem;
        text-align: center;
    }

    @media (max-width: 768px) {
        .block-container { padding: 1.1rem 1rem 2rem 1rem; }
        .hero-card { border-radius: 23px 23px 42px 23px; padding: 1.35rem; }
        .hero-title { font-size: 1.22rem; }
        .recommendation-name { font-size: 1.65rem; }
        .leafy-card { min-height: 290px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR: NAVIGATION AND DISK CONFIGURATION
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-mark">🌿</div>
            <div class="sidebar-brand-name">Disk I/O Analyser</div>
            <div class="sidebar-brand-caption">Advanced Operating Systems Project</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="sidebar-section">Workspace</div>', unsafe_allow_html=True)

    page = st.radio(
        "Select module",
        [
            "Dashboard",
            "Disk Simulator",
            "Performance Analysis",
            "Intelligent Recommendation",
            "Reports",
        ],
        label_visibility="collapsed",
    )

    st.divider()
    st.markdown('<div class="sidebar-section">Disk configuration</div>', unsafe_allow_html=True)

    disk_size = st.number_input(
        "Disk size (cylinders)",
        min_value=2,
        max_value=10000,
        value=250,
        step=1,
    )

    head = st.number_input(
        "Initial head position",
        min_value=0,
        max_value=int(disk_size) - 1,
        value=min(72, int(disk_size) - 1),
        step=1,
    )

    request_input = st.text_area(
        "Disk request queue",
        value="45, 132, 18, 210, 86, 164, 57, 119",
        height=88,
        help="Enter cylinder numbers separated by commas.",
    )

    direction = st.selectbox(
        "Initial direction",
        ["right", "left"],
        format_func=lambda value: "Right" if value == "right" else "Left",
    )

    seek_time = st.number_input(
        "Seek time per cylinder (ms)",
        min_value=0.001,
        max_value=100.0,
        value=0.1,
        step=0.01,
        format="%.3f",
    )

    objective = st.selectbox(
        "Recommendation objective",
        ["balanced", "minimum_movement"],
        format_func=lambda value: (
            "Balanced performance"
            if value == "balanced"
            else "Minimum head movement"
        ),
    )

    st.markdown(
        """
        <div class="sidebar-help">
            Change the configuration above to recalculate all six scheduling
            algorithms and update the analysis throughout the application.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# INPUT VALIDATION
# ============================================================

try:
    raw_items = [item.strip() for item in request_input.split(",") if item.strip()]

    if not raw_items:
        raise ValueError("Enter at least one disk request.")

    try:
        requests = [int(item) for item in raw_items]
    except ValueError:
        raise ValueError("All disk requests must be whole numbers separated by commas.")

    if any(value < 0 or value >= int(disk_size) for value in requests):
        raise ValueError(
            f"Every request must be between 0 and {int(disk_size) - 1}."
        )

    if len(requests) != len(set(requests)):
        raise ValueError(
            "Duplicate requests are not supported in the current algorithm implementation."
        )

    if not 0 <= int(head) < int(disk_size):
        raise ValueError("Initial head position is outside the disk range.")

    input_valid = True

except ValueError as error:
    requests = []
    input_valid = False
    validation_error = str(error)


# ============================================================
# SHARED SIMULATION DATA
# ============================================================

algorithm_names = ["FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK"]

results = {}
all_metrics = []
recommendation = None
metrics_df = pd.DataFrame()

if input_valid:
    for algorithm_name in algorithm_names:
        result = run_algorithm(
            name=algorithm_name,
            requests=requests,
            head=int(head),
            disk_size=int(disk_size),
            direction=direction,
        )

        metrics = calculate_metrics(
            result,
            seek_time_per_cylinder=seek_time,
            direction=direction,
        )

        results[algorithm_name] = result
        all_metrics.append(metrics)

    recommendation = recommend_algorithm(
        all_metrics,
        objective=objective,
    )
    metrics_df = pd.DataFrame(all_metrics)


# ============================================================
# REUSABLE UI HELPERS
# ============================================================

def page_header(eyebrow, title, subtitle):
    st.markdown(f'<div class="page-eyebrow">{eyebrow}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="page-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def show_recommendation_card(recommendation_data, compact=False):
    best = recommendation_data["recommended_algorithm"]
    reason = recommendation_data["reason"]
    score = recommendation_data.get("recommended_score")

    score_line = ""
    if score is not None and not compact:
        score_line = f'<div class="recommendation-copy">Performance score: <strong>{score}</strong></div>'

    st.markdown(
        f"""
        <div class="recommendation-card">
            <div class="recommendation-label">Recommended algorithm</div>
            <div class="recommendation-name">{best}</div>
            <div class="recommendation-copy">{reason}</div>
            {score_line}
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_chart(figure):
    """Apply the application's soft green palette to existing Plotly charts."""
    palette = ["#2F7650", "#83B98D", "#A7D1A8", "#477F65", "#C2DDBD", "#6B9E7A"]
    figure.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#F7FBF5",
        font=dict(family="Segoe UI, Arial, sans-serif", color="#355B46"),
        title_font=dict(color="#24583D"),
        legend=dict(font=dict(color="#527064")),
        margin=dict(l=35, r=25, t=55, b=40),
    )
    figure.update_xaxes(
        gridcolor="#DDEBDD",
        linecolor="#CFE2D1",
        zerolinecolor="#D5E7D7",
        tickfont=dict(color="#668174"),
    )
    figure.update_yaxes(
        gridcolor="#DDEBDD",
        linecolor="#CFE2D1",
        zerolinecolor="#D5E7D7",
        tickfont=dict(color="#668174"),
    )
    for index, trace in enumerate(figure.data):
        color = palette[index % len(palette)]
        if hasattr(trace, "marker") and trace.marker is not None:
            trace.marker.color = color
            trace.marker.line.color = "#FFFFFF"
        if hasattr(trace, "line") and trace.line is not None:
            trace.line.color = color
    return figure


def show_leafy_mascot(message):
    """Display Leafy, the animated guide beside the simulator. UI only."""
    st.markdown(
        f"""
        <div class="leafy-card">
            <div class="leafy-caption">Your little lab assistant</div>
            <div class="leafy-stage">
                <div class="leafy-person">
                    <div class="leafy-head">
                        <span class="leafy-eye left"></span>
                        <span class="leafy-eye right"></span>
                        <span class="leafy-smile"></span>
                    </div>
                    <div class="leafy-arm"></div>
                    <div class="leafy-arm other"></div>
                    <div class="leafy-body"></div>
                    <div class="leafy-leg"></div>
                    <div class="leafy-leg right"></div>
                    <div class="leafy-foot"></div>
                    <div class="leafy-foot right"></div>
                </div>
            </div>
            <div class="leafy-message">{message}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_metrics_table(dataframe):
    display_df = dataframe.copy()

    column_labels = {
        "algorithm": "Algorithm",
        "total_head_movement": "Total movement",
        "average_head_movement": "Average movement",
        "direction_changes": "Direction changes",
        "requests_serviced": "Requests serviced",
        "estimated_seek_time_ms": "Estimated seek time (ms)",
    }

    display_df = display_df.rename(columns=column_labels)

    numeric_formats = {}
    for column in ["Average movement", "Estimated seek time (ms)"]:
        if column in display_df.columns:
            numeric_formats[column] = "{:.2f}"

    st.dataframe(
        display_df.style.format(numeric_formats),
        use_container_width=True,
        hide_index=True,
    )


def show_footer():
    st.markdown(
        """
        <div class="app-footer">
            Intelligent Disk I/O Scheduling Analyser
            &nbsp;•&nbsp; Advanced Operating Systems Mini Project
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# APPLICATION HEADER
# ============================================================

st.markdown(
    """
    <div class="hero-card">
        <div class="hero-title">Welcome to the Green Disk Lab 🌿</div>
        <div class="hero-copy">
            A little control room for your disk requests. Explore the movement, compare strategies, and let Leafy guide you through the results.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not input_valid:
    st.error(f"Disk configuration needs attention: {validation_error}")
    st.info("Correct the highlighted configuration in the sidebar. The analysis will update automatically.")


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":
    page_header(
        "Overview",
        "Your disk at a glance",
        "Your workload, head position and best-fit scheduling strategy — all in one place.",
    )

    if input_valid:
        best = recommendation["recommended_algorithm"]

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Disk cylinders", f"{int(disk_size):,}")
        k2.metric("Initial head", f"{int(head):,}")
        k3.metric("Requests in queue", len(requests))
        k4.metric("Recommended", best)

        st.write("")
        show_recommendation_card(recommendation, compact=True)

        left, right = st.columns([1.5, 1], gap="large")

        with left:
            st.subheader("Head movement comparison")
            st.plotly_chart(
                style_chart(create_performance_chart(all_metrics)),
                use_container_width=True,
                config={"displayModeBar": True, "displaylogo": False},
            )

        with right:
            st.subheader("Inside your workload")
            show_leafy_mascot(
                f"Your queue has <strong>{len(requests)} requests</strong>. "
                "Change the settings in the sidebar and I'll keep an eye on the simulation!"
            )
            st.markdown(
                f"""
                <div class="info-strip">
                    <strong>Request queue</strong><br>
                    {", ".join(map(str, requests))}
                    <br><br>
                    <strong>Initial direction</strong><br>
                    {direction.title()}
                    <br><br>
                    <strong>Seek time per cylinder</strong><br>
                    {seek_time:g} ms
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.subheader("Algorithm performance summary")
        show_metrics_table(metrics_df)

    else:
        st.warning("Enter a valid disk configuration to view the dashboard.")


# ============================================================
# DISK SIMULATOR
# ============================================================

elif page == "Disk Simulator":
    page_header(
        "Simulation lab",
        "Watch the disk head in action",
        "Choose a scheduling method and follow the route as requests get serviced.",
    )

    if input_valid:
        selected_algorithm = st.selectbox(
            "Scheduling algorithm",
            algorithm_names,
            help="Choose one of the six implemented disk scheduling algorithms.",
        )

        result = results[selected_algorithm]
        selected_metric = metrics_df.loc[
            metrics_df["algorithm"] == selected_algorithm
        ].iloc[0]

        a, b, c = st.columns(3)
        a.metric("Selected algorithm", selected_algorithm)
        b.metric("Total head movement", f"{selected_metric['total_head_movement']} cylinders")
        c.metric("Estimated seek time", f"{selected_metric['estimated_seek_time_ms']:.2f} ms")

        st.subheader("The head's journey")
        chart_col, leafy_col = st.columns([3.2, 1.15], gap="large")

        with chart_col:
            st.plotly_chart(
                style_chart(create_movement_chart(result, int(disk_size))),
                use_container_width=True,
                config={"displayModeBar": True, "displaylogo": False},
            )

        with leafy_col:
            show_leafy_mascot(
                f"You're viewing <strong>{selected_algorithm}</strong>. "
                "I'm pointing to the movement path — switch the algorithm and I'll update my tip!"
            )

        st.subheader("Simulation details")
        detail_left, detail_right = st.columns(2, gap="large")

        with detail_left:
            st.markdown("**Service order**")
            st.code("  →  ".join(map(str, result["service_order"])), language=None)

        with detail_right:
            st.markdown("**Movement path**")
            st.code("  →  ".join(map(str, result["movement_path"])), language=None)

        st.caption(
            "The movement chart visualises the calculated service path. "
            "The displayed seek time is an estimate based on the configured "
            "time per cylinder, not a measurement from physical disk hardware."
        )
    else:
        st.warning("Enter a valid disk configuration to run the simulator.")


# ============================================================
# PERFORMANCE ANALYSIS
# ============================================================

elif page == "Performance Analysis":
    page_header(
        "Analytics",
        "Which algorithm moves smarter?",
        "Compare the six algorithms using total movement, average movement and seek-time estimates.",
    )

    if input_valid:
        st.subheader("Total disk head movement")
        st.plotly_chart(
            style_chart(create_performance_chart(all_metrics)),
            use_container_width=True,
            config={"displayModeBar": True, "displaylogo": False},
        )

        st.subheader("Detailed performance metrics")
        show_metrics_table(metrics_df)

        st.subheader("Algorithm ranking")
        st.plotly_chart(
            style_chart(create_ranking_chart(recommendation)),
            use_container_width=True,
            config={"displayModeBar": True, "displaylogo": False},
        )
    else:
        st.warning("Enter a valid disk configuration to analyse performance.")


# ============================================================
# INTELLIGENT RECOMMENDATION
# ============================================================

elif page == "Intelligent Recommendation":
    page_header(
        "Decision support",
        "Meet your algorithm match",
        "The recommendation is calculated from the selected objective and the current simulation metrics.",
    )

    if input_valid:
        show_recommendation_card(recommendation)

        st.subheader("Algorithm ranking")
        ranking_df = pd.DataFrame(recommendation["rankings"])

        ranking_labels = {
            "algorithm": "Algorithm",
            "total_head_movement": "Total movement",
            "direction_changes": "Direction changes",
            "score": "Performance score",
        }
        ranking_df = ranking_df.rename(columns=ranking_labels)

        st.dataframe(
            ranking_df.style.format(
                {
                    "Performance score": "{:.2f}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.subheader("Ranking visualisation")
        st.plotly_chart(
            style_chart(create_ranking_chart(recommendation)),
            use_container_width=True,
            config={"displayModeBar": True, "displaylogo": False},
        )

        st.subheader("System warnings and limitations")
        if recommendation.get("warnings"):
            for warning in recommendation["warnings"]:
                st.warning(warning)
        else:
            st.success("No recommendation warnings were returned for this configuration.")

        st.info(
            "The recommendation engine is rule-based and compares simulated "
            "metrics. It is not a machine-learning model and does not measure "
            "real hardware latency or live request-arrival behaviour."
        )
    else:
        st.warning("Enter a valid disk configuration to generate a recommendation.")


# ============================================================
# REPORTS
# ============================================================

elif page == "Reports":
    page_header(
        "Export centre",
        "Your results, ready to take away",
        "Review the current results and export a PDF report or CSV performance dataset.",
    )

    if input_valid:
        st.subheader("Report summary")
        k1, k2, k3 = st.columns(3)
        k1.metric("Algorithms analysed", len(all_metrics))
        k2.metric("Requests serviced per algorithm", len(requests))
        k3.metric("Recommended algorithm", recommendation["recommended_algorithm"])

        st.subheader("Performance preview")
        show_metrics_table(metrics_df)

        st.subheader("Recommended algorithm")
        show_recommendation_card(recommendation, compact=True)

        st.divider()

        pdf_col, csv_col = st.columns(2, gap="large")

        with pdf_col:
            st.markdown("**Complete PDF report**")
            st.caption("Includes disk configuration, performance comparison, recommendation, rankings and simulation details.")

            try:
                pdf_data = generate_pdf_report(
                    disk_size=int(disk_size),
                    head=int(head),
                    requests=requests,
                    direction=direction,
                    seek_time=seek_time,
                    metrics_list=all_metrics,
                    recommendation=recommendation,
                    results=results,
                )

                st.download_button(
                    label="Download PDF report",
                    data=pdf_data,
                    file_name="Disk_IO_Analysis_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                )
                st.success("PDF report is ready.")
            except Exception as error:
                st.error(f"PDF generation failed: {error}")

        with csv_col:
            st.markdown("**Performance data (CSV)**")
            st.caption("A spreadsheet-friendly export of the six algorithm metrics.")
            st.download_button(
                label="Download performance CSV",
                data=metrics_df.to_csv(index=False),
                file_name="disk_scheduling_results.csv",
                mime="text/csv",
                use_container_width=True,
            )
    else:
        st.warning("Enter a valid disk configuration before generating reports.")


# ============================================================
# FOOTER
# ============================================================

show_footer()
