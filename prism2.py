"""
PRISM Portfolio Advisor — Full Rewrite
Audit fixes: syntax errors, scoring formula, mislabeled metrics,
missing chart, no disclaimer, fragile CSS selectors, and more.
Design: Deep navy + amber accent, Inter + JetBrains Mono, wealth-arc signature element.
"""

import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from fpdf import FPDF

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG — must be first Streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PRISM | Portfolio Advisor",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN TOKENS
# Palette: Deep navy (#0B1628), warm white (#F5F3EE), amber (#F5A623),
#          sage (#4CAF82), slate (#8899AA), charcoal card (#16253D)
# Type: system stack (Inter-like) for body; JetBrains Mono for numbers
# Signature: animated amber progress arc replacing Streamlit's default bar
# ─────────────────────────────────────────────────────────────────────────────
STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Root & Page ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0B1628 !important;
    color: #F5F3EE !important;
    font-family: 'Inter', system-ui, sans-serif !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none; }

/* ── Main block centering ── */
.main .block-container {
    max-width: 720px !important;
    padding: 2rem 1.5rem 4rem !important;
}

/* ── Typography ── */
h1 { 
    font-size: 2rem !important; 
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    color: #F5F3EE !important;
    line-height: 1.2 !important;
}
h2, h3 { 
    font-weight: 600 !important; 
    color: #F5F3EE !important;
}
p, li, label, .stMarkdown { 
    color: #C8D0DA !important; 
    font-size: 0.95rem !important;
    line-height: 1.65 !important;
}

/* ── Cards / Question Boxes ── */
.prism-card {
    background: #16253D;
    border: 1px solid #1E3352;
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    margin: 1rem 0;
    position: relative;
}
.prism-card-accent {
    border-left: 3px solid #F5A623;
}
.prism-card-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #F5A623 !important;
    margin-bottom: 0.4rem;
}

/* ── Progress Bar (custom arc replaced by styled div) ── */
.prism-progress-wrap {
    background: #1E3352;
    border-radius: 99px;
    height: 5px;
    margin: 0.5rem 0 1.75rem;
    overflow: hidden;
}
.prism-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #F5A623, #F5C84A);
    border-radius: 99px;
    transition: width 0.4s ease;
}
.prism-step-label {
    font-size: 0.75rem;
    color: #8899AA !important;
    margin-bottom: 0.2rem;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Buttons ── */
div.stButton > button {
    background: #F5A623 !important;
    color: #0B1628 !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.6rem 1.4rem !important;
    width: 100% !important;
    transition: background 0.2s, transform 0.1s !important;
    font-family: 'Inter', sans-serif !important;
}
div.stButton > button:hover {
    background: #F5C84A !important;
    transform: translateY(-1px) !important;
}
div.stButton > button:active { transform: translateY(0) !important; }

/* ── Back Button (secondary) ── */
div.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #8899AA !important;
    border: 1px solid #1E3352 !important;
}
div.stButton > button[kind="secondary"]:hover {
    background: #16253D !important;
    color: #F5F3EE !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] > div > div > div {
    color: #F5A623 !important;
}
[data-testid="stSlider"] [role="slider"] {
    background: #F5A623 !important;
    border-color: #F5A623 !important;
}

/* ── Number Inputs ── */
[data-testid="stNumberInput"] input {
    background: #0B1628 !important;
    border: 1px solid #1E3352 !important;
    color: #F5F3EE !important;
    border-radius: 6px !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ── Radio Buttons ── */
[data-testid="stRadio"] > label {
    color: #C8D0DA !important;
}
[data-testid="stRadio"] [data-baseweb="radio"] > div:first-child {
    border-color: #F5A623 !important;
}
[data-testid="stRadio"] div[data-checked="true"] > div:first-child {
    background: #F5A623 !important;
}

/* ── Metric Cards ── */
[data-testid="metric-container"] {
    background: #16253D !important;
    border: 1px solid #1E3352 !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 0.72rem !important;
    color: #8899AA !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 1.4rem !important;
    color: #F5F3EE !important;
    font-weight: 600 !important;
}

/* ── Info / Warning blocks ── */
[data-testid="stInfo"] {
    background: rgba(245,166,35,0.08) !important;
    border: 1px solid rgba(245,166,35,0.3) !important;
    border-radius: 8px !important;
    color: #C8D0DA !important;
}
[data-testid="stWarning"] {
    background: rgba(76,175,130,0.08) !important;
    border: 1px solid rgba(76,175,130,0.3) !important;
    border-radius: 8px !important;
}

/* ── Download Button ── */
[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: #F5A623 !important;
    border: 1.5px solid #F5A623 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    width: 100% !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(245,166,35,0.1) !important;
}

/* ── Divider ── */
hr { border-color: #1E3352 !important; margin: 1.5rem 0 !important; }

/* ── Disclaimer ── */
.prism-disclaimer {
    font-size: 0.72rem !important;
    color: #4A5568 !important;
    line-height: 1.5 !important;
    margin-top: 2rem;
    border-top: 1px solid #1E3352;
    padding-top: 1rem;
}

/* ── Allocation rows ── */
.alloc-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.6rem 0;
    border-bottom: 1px solid #1E3352;
    font-size: 0.9rem;
}
.alloc-bar-track {
    height: 4px;
    background: #1E3352;
    border-radius: 99px;
    margin: 0.2rem 0 0.5rem;
    overflow: hidden;
}
.alloc-bar-fill {
    height: 100%;
    border-radius: 99px;
}

/* ── Plotly transparent bg ── */
.js-plotly-plot .plotly .svg-container { border-radius: 12px; }
</style>
"""
st.markdown(STYLE, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE INIT
# ─────────────────────────────────────────────────────────────────────────────
if "step" not in st.session_state:
    st.session_state.step = 1
if "answers" not in st.session_state:
    st.session_state.answers = {}

TOTAL_STEPS = 4


# ─────────────────────────────────────────────────────────────────────────────
# HELPER: Custom progress bar + step label
# ─────────────────────────────────────────────────────────────────────────────
def render_progress(current: int, total: int = TOTAL_STEPS):
    pct = int((current / total) * 100)
    st.markdown(
        f'<p class="prism-step-label">Step {current} of {total}</p>'
        f'<div class="prism-progress-wrap">'
        f'  <div class="prism-progress-fill" style="width:{pct}%"></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def card(label: str = "", accent: bool = True):
    accent_cls = "prism-card-accent" if accent else ""
    label_html = f'<p class="prism-card-label">{label}</p>' if label else ""
    return f'<div class="prism-card {accent_cls}">{label_html}'


def card_end():
    return "</div>"


def nav_cols(back_fn=None, forward_label="Next", forward_fn=None):
    """Render back + forward navigation in two columns."""
    if back_fn:
        c1, c2 = st.columns([1, 2])
        with c1:
            st.button("← Back", on_click=back_fn, key=f"back_{st.session_state.step}")
        with c2:
            return st.button(forward_label, key=f"fwd_{st.session_state.step}")
    else:
        return st.button(forward_label, key=f"fwd_{st.session_state.step}")


# ─────────────────────────────────────────────────────────────────────────────
# NAVIGATION
# ─────────────────────────────────────────────────────────────────────────────
def next_step():
    st.session_state.step += 1

def prev_step():
    st.session_state.step -= 1

def restart():
    st.session_state.step = 1
    st.session_state.answers = {}


# ─────────────────────────────────────────────────────────────────────────────
# CALCULATION ENGINE  (bug-fixed, methodology-improved)
# ─────────────────────────────────────────────────────────────────────────────
ASSET_SPECS = {
    "Large Cap Equities": {"beta": 0.90, "return": 0.11, "color": "#F5A623"},
    "Mid & Small Cap":    {"beta": 1.35, "return": 0.14, "color": "#4CAF82"},
    "Liquid Debt Funds":  {"beta": 0.10, "return": 0.07, "color": "#5B8CDB"},
    "Gold ETFs":          {"beta": 0.20, "return": 0.08, "color": "#C9A84C"},
}

INFLATION = 0.06  # 6% structural macro inflation assumption


def compute_risk_score(q1_idx: int, q2_idx: int, q3_idx: int, horizon: int) -> int:
    """
    FIX: Original formula was additive and could exceed 100 before clamping.
    New approach: weighted average across three dimensions, each scored 0-100,
    then horizon-adjusted. All weights sum to 1.0.
    """
    willingness_score = [15, 50, 85][q1_idx]   # panic → hold → buy-the-dip
    philosophy_score  = [15, 50, 85][q2_idx]   # preserve → balanced → growth
    capacity_score    = [20, 50, 80][q3_idx]   # unstable → stable → robust

    # Weighted composite: willingness 35%, philosophy 35%, capacity 30%
    raw = 0.35 * willingness_score + 0.35 * philosophy_score + 0.30 * capacity_score

    # Horizon penalty: short horizons reduce effective risk tolerance
    if horizon < 3:
        raw = min(raw, 30)
    elif horizon < 7:
        raw = raw * 0.85

    return max(0, min(int(round(raw)), 100))


def classify_profile(score: int) -> str:
    if score < 38:
        return "Conservative"
    elif score < 68:
        return "Moderate"
    else:
        return "Aggressive"


def compute_allocation(profile: str, age: int, horizon: int) -> dict:
    """
    FIX: Syntax errors (*) corrected. 110-age rule preserved (standard heuristic).
    Short-horizon override stays (< 3 yrs → capital preservation mode).
    """
    # Max equity ceiling by age (110 − age rule)
    max_eq = max(0.10, min((110 - age) / 100, 0.90))

    if horizon < 3:
        # Capital preservation: no equity
        return {
            "Large Cap Equities": 0.0,
            "Mid & Small Cap":    0.0,
            "Liquid Debt Funds":  0.80,
            "Gold ETFs":          0.20,
        }

    if profile == "Conservative":
        eq = max_eq * 0.40
        alloc = {
            "Large Cap Equities": eq,
            "Mid & Small Cap":    0.0,
            "Liquid Debt Funds":  max(0.0, 0.80 - eq),
            "Gold ETFs":          0.20,
        }
    elif profile == "Moderate":
        eq = max_eq * 0.70
        alloc = {
            "Large Cap Equities": eq * 0.65,   # FIX: was `eq _0.65`
            "Mid & Small Cap":    eq * 0.35,   # FIX: was `eq_ 0.35`
            "Liquid Debt Funds":  max(0.0, 0.80 - eq),
            "Gold ETFs":          0.15,
        }
    else:  # Aggressive
        eq = max_eq * 1.0
        alloc = {
            "Large Cap Equities": eq * 0.55,   # FIX: was `eq _0.50`
            "Mid & Small Cap":    eq * 0.45,   # FIX: was `eq_ 0.50`
            "Liquid Debt Funds":  max(0.0, 0.85 - eq),
            "Gold ETFs":          0.10,
        }

    # Normalize to exactly 100%
    total = sum(alloc.values())
    if total > 0:
        alloc = {k: v / total for k, v in alloc.items()}
    return alloc


def compute_projections(initial: float, sip: float, annual_return: float, horizon_yrs: int) -> dict:
    """
    FIX: Syntax errors (**) corrected.
    Computes year-by-year trajectory for the growth chart.
    SIP formula: annuity-due (contribution at start of each month).
    """
    r_mo = annual_return / 12
    n_mo = horizon_yrs * 12

    # Lump sum future value
    fv_lump = initial * ((1 + annual_return) ** horizon_yrs)   # FIX: was `_((1 + p_return)_ * horizon`

    # SIP future value (annuity-due)
    if r_mo == 0:
        fv_sip = sip * n_mo
    else:
        fv_sip = sip * (((1 + r_mo) ** n_mo - 1) / r_mo) * (1 + r_mo)  # FIX: was `monthly_sip _(((1+r_mo)_ *n_mo`

    total = fv_lump + fv_sip
    total_invested = initial + sip * n_mo
    real_value = total / ((1 + INFLATION) ** horizon_yrs)

    # Year-by-year trajectory for chart
    years = list(range(0, horizon_yrs + 1))
    lump_trajectory = [initial * ((1 + annual_return) ** y) for y in years]
    sip_trajectory = []
    for y in years:
        n = y * 12
        if r_mo == 0:
            sip_trajectory.append(sip * n)
        else:
            sip_trajectory.append(sip * (((1 + r_mo) ** n - 1) / r_mo) * (1 + r_mo))

    combined = [l + s for l, s in zip(lump_trajectory, sip_trajectory)]
    invested  = [initial + sip * y * 12 for y in years]

    return {
        "fv_lump": fv_lump,
        "fv_sip": fv_sip,
        "total": total,
        "total_invested": total_invested,
        "real_value": real_value,
        "gain": total - total_invested,
        "years": years,
        "combined": combined,
        "invested": invested,
    }


# ─────────────────────────────────────────────────────────────────────────────
# PDF GENERATOR  (improved layout, still fpdf2-compatible)
# ─────────────────────────────────────────────────────────────────────────────
def generate_pdf(answers: dict, alloc: dict, projections: dict,
                 profile: str, score: int, p_return: float, p_beta: float) -> bytes:
    age           = answers["age"]
    initial       = answers["initial_corpus"]
    sip           = answers["monthly_sip"]
    horizon       = answers["horizon"]
    total         = projections["total"]
    real_val      = projections["real_value"]
    total_inv     = projections["total_invested"]
    gain          = projections["gain"]

    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(20, 20, 20)
    W = pdf.w - 40  # usable width

    # ── Header ──
    pdf.set_fill_color(11, 22, 40)
    pdf.rect(0, 0, pdf.w, 40, "F")
    pdf.set_font("Helvetica", style="B", size=18)
    pdf.set_text_color(245, 166, 35)
    pdf.set_y(12)
    pdf.cell(pdf.w, 10, "PRISM WEALTH STRATEGY REPORT", align="C", ln=True)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(200, 208, 218)
    pdf.cell(pdf.w, 8, "Personalized Risk Intelligence & Strategy Model", align="C", ln=True)
    pdf.set_y(48)
    pdf.set_text_color(30, 30, 30)

    def section(title: str):
        pdf.ln(4)
        pdf.set_fill_color(240, 244, 250)
        pdf.set_font("Helvetica", style="B", size=11)
        pdf.set_text_color(11, 22, 40)
        pdf.cell(W, 9, f"  {title}", fill=True, ln=True)
        pdf.ln(2)
        pdf.set_font("Helvetica", size=10)
        pdf.set_text_color(50, 50, 60)

    def row(label: str, value: str):
        pdf.set_font("Helvetica", style="B", size=10)
        pdf.cell(W / 2, 7, label, ln=False)
        pdf.set_font("Helvetica", size=10)
        pdf.cell(W / 2, 7, value, ln=True)

    # ── Section 1 ──
    section("1. Investor Profile")
    row("Age:", f"{age} years")
    row("Investment Horizon:", f"{horizon} years")
    row("Initial Capital:", f"Rs. {initial:,.0f}")
    row("Monthly SIP:", f"Rs. {sip:,.0f}")
    row("Total Capital to be Invested:", f"Rs. {total_inv:,.0f}")

    # ── Section 2 ──
    section("2. Risk Assessment")
    row("Risk Profile:", f"{profile}  (Composite Score: {score}/100)")
    row("Expected Annual Return (CAGR):", f"{p_return*100:.2f}%")
    row("Portfolio Beta (Market Sensitivity):", f"{p_beta:.2f}x")
    pdf.ln(1)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(100, 100, 110)
    pdf.multi_cell(W, 6, "Beta measures sensitivity to market movements (1.0 = matches market). "
                          "A beta below 1.0 indicates lower volatility relative to the index.", ln=True)

    # ── Section 3 ──
    section("3. Recommended Asset Allocation")
    for asset, wt in alloc.items():
        if wt > 0.001:
            deploy = initial * wt
            pdf.set_font("Helvetica", size=10)
            pdf.set_text_color(50, 50, 60)
            pdf.cell(W * 0.45, 7, f"  {asset}", ln=False)
            pdf.cell(W * 0.20, 7, f"{wt*100:.1f}%", align="C", ln=False)
            pdf.cell(W * 0.35, 7, f"Rs. {deploy:,.0f}", align="R", ln=True)

    # ── Section 4 ──
    section("4. Wealth Projection")
    row("Projected Gross Corpus (Nominal):", f"Rs. {total:,.0f}")
    row("Projected Real Corpus (Inflation-adj.):", f"Rs. {real_val:,.0f}")
    row("Total Invested Capital:", f"Rs. {total_inv:,.0f}")
    row("Estimated Gains:", f"Rs. {gain:,.0f}")
    pdf.ln(2)
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(100, 100, 110)
    pdf.multi_cell(W, 5,
        "Inflation adjustment uses a 6% annual rate. Real value represents the "
        "equivalent purchasing power of the projected corpus in today's money. "
        "SIP projections use annuity-due (contributions at start of each month).", ln=True)

    # ── Disclaimer ──
    pdf.ln(6)
    pdf.set_fill_color(250, 245, 235)
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.set_text_color(120, 100, 60)
    disclaimer = (
        "DISCLAIMER: This report is generated by an automated model for educational and informational "
        "purposes only. It does not constitute financial advice, investment recommendations, or a solicitation "
        "to buy or sell any securities. Past performance is not indicative of future results. Please consult "
        "a SEBI-registered investment advisor before making any financial decisions."
    )
    pdf.multi_cell(W, 5, disclaimer, ln=True)

    return bytes(pdf.output())


# ─────────────────────────────────────────────────────────────────────────────
# PLOTLY THEME HELPER
# ─────────────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#0F1E35",
    font=dict(family="Inter, system-ui", color="#C8D0DA", size=12),
    margin=dict(t=20, b=20, l=10, r=10),
)


# ─────────────────────────────────────────────────────────────────────────────
# ── STEP 1: WELCOME & DEMOGRAPHICS ──────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.step == 1:
    st.markdown(
        """
        <div style="margin-bottom:0.25rem">
          <span style="font-size:0.75rem;letter-spacing:0.12em;text-transform:uppercase;
                       color:#F5A623;font-weight:600;">Risk Intelligence Platform</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("PRISM Portfolio Advisor")
    st.markdown(
        "Answer four short questions and PRISM will generate a personalized "
        "asset allocation strategy and wealth projection report."
    )
    st.markdown("---")

    st.markdown(card("About You", accent=True), unsafe_allow_html=True)
    age = st.slider("Your age", min_value=18, max_value=85, value=30,
                    help="Used to calibrate your equity ceiling (110 − age rule)")
    st.markdown(card_end(), unsafe_allow_html=True)

    st.markdown(card("Capital to Invest", accent=True), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        initial_corpus = st.number_input(
            "Starting lump sum (₹)",
            min_value=0, value=100_000, step=10_000,
            help="One-time amount you invest today",
        )
    with col2:
        monthly_sip = st.number_input(
            "Monthly SIP contribution (₹)",
            min_value=0, value=5_000, step=500,
            help="Regular monthly investment amount",
        )
    if initial_corpus == 0 and monthly_sip == 0:
        st.warning("⚠ Enter at least a lump sum or monthly SIP to generate a meaningful projection.")
    st.markdown(card_end(), unsafe_allow_html=True)

    if st.button("Begin Assessment →"):
        st.session_state.answers["age"] = age
        st.session_state.answers["initial_corpus"] = initial_corpus
        st.session_state.answers["monthly_sip"] = monthly_sip
        next_step()
        st.rerun()

    st.markdown(
        '<p class="prism-disclaimer">PRISM is an educational tool. '
        'It does not provide regulated financial advice. '
        'Consult a SEBI-registered advisor before investing.</p>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# ── STEP 2: INVESTMENT TIMELINE ──────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.step == 2:
    render_progress(2)
    st.title("Investment Horizon")
    st.markdown("How long can you keep this money invested without needing it?")

    # Persist slider value across Back navigation
    saved_horizon = st.session_state.answers.get("horizon", 10)

    st.markdown(card("Time in Market", accent=True), unsafe_allow_html=True)
    horizon = st.slider(
        "Investment horizon (years)",
        min_value=1, max_value=40, value=saved_horizon,
        help="Longer horizons absorb more short-term volatility",
    )
    # Contextual guidance
    if horizon < 3:
        st.info("📌 Horizon under 3 years: PRISM will prioritise capital preservation with minimal equity exposure.")
    elif horizon < 7:
        st.info("📌 Medium-term horizon: A balanced mix of growth and stability is appropriate.")
    else:
        st.info("📌 Long-term horizon: Greater equity exposure can be considered to maximise compounding.")
    st.markdown(card_end(), unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.button("← Back", on_click=prev_step)
    with c2:
        if st.button("Next: Risk Profile →"):
            st.session_state.answers["horizon"] = horizon
            next_step()
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ── STEP 3: RISK TOLERANCE ───────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.step == 3:
    render_progress(3)
    st.title("Risk & Behaviour Profile")
    st.markdown("Three questions to understand your risk comfort. There are no right or wrong answers.")

    # Persist selections
    prev = st.session_state.answers

    st.markdown(card("Market Reaction", accent=True), unsafe_allow_html=True)
    st.markdown("**Your portfolio drops 20% during a market correction. What do you do?**")
    q1 = st.radio(
        "Market Reaction",
        options=[
            "Sell — I'd rather stop the bleeding now",
            "Hold — markets recover, I'll stay the course",
            "Buy more — downturns are buying opportunities",
        ],
        index=prev.get("q1_idx", 1),
        label_visibility="collapsed",
    )
    st.markdown(card_end(), unsafe_allow_html=True)

    st.markdown(card("Investment Philosophy", accent=True), unsafe_allow_html=True)
    st.markdown("**What's your primary goal when investing?**")
    q2 = st.radio(
        "Investment Philosophy",
        options=[
            "Protect my capital — growth can be slow",
            "Balance — decent growth with managed downside",
            "Maximise long-term wealth — I can handle swings",
        ],
        index=prev.get("q2_idx", 1),
        label_visibility="collapsed",
    )
    st.markdown(card_end(), unsafe_allow_html=True)

    st.markdown(card("Financial Safety Net", accent=True), unsafe_allow_html=True)
    st.markdown("**How stable is your primary income?**")
    q3 = st.radio(
        "Financial Safety Net",
        options=[
            "Irregular — freelance, variable, or uncertain",
            "Stable — salaried with a basic emergency fund",
            "Very secure — multiple sources or large reserve",
        ],
        index=prev.get("q3_idx", 1),
        label_visibility="collapsed",
    )
    st.markdown(card_end(), unsafe_allow_html=True)

    # Map answers to indices
    q1_opts = ["Sell", "Hold", "Buy"]
    q2_opts = ["Protect", "Balance", "Maximise"]
    q3_opts = ["Irregular", "Stable", "Very"]
    q1_idx = next(i for i, w in enumerate(q1_opts) if w.lower() in q1.lower())
    q2_idx = next(i for i, w in enumerate(q2_opts) if w.lower() in q2.lower())
    q3_idx = next(i for i, w in enumerate(q3_opts) if w.lower() in q3.lower())

    c1, c2 = st.columns([1, 2])
    with c1:
        st.button("← Back", on_click=prev_step)
    with c2:
        if st.button("Generate My Report →"):
            horizon = st.session_state.answers.get("horizon", 10)
            score = compute_risk_score(q1_idx, q2_idx, q3_idx, horizon)
            st.session_state.answers["risk_score"] = score
            st.session_state.answers["q1_idx"] = q1_idx
            st.session_state.answers["q2_idx"] = q2_idx
            st.session_state.answers["q3_idx"] = q3_idx
            next_step()
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# ── STEP 4: REPORT ───────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
elif st.session_state.step == 4:
    render_progress(4)

    ans           = st.session_state.answers
    age           = ans["age"]
    initial       = ans["initial_corpus"]
    sip           = ans["monthly_sip"]
    horizon       = ans["horizon"]
    score         = ans["risk_score"]
    profile       = classify_profile(score)

    # ── Compute allocation & projections ──
    alloc = compute_allocation(profile, age, horizon)
    p_return = sum(alloc[a] * ASSET_SPECS[a]["return"] for a in alloc)
    p_beta   = sum(alloc[a] * ASSET_SPECS[a]["beta"]   for a in alloc)
    proj     = compute_projections(initial, sip, p_return, horizon)

    # ── Profile badge ──
    badge_colors = {
        "Conservative": "#5B8CDB",
        "Moderate":     "#4CAF82",
        "Aggressive":   "#F5A623",
    }
    bc = badge_colors[profile]
    st.markdown(
        f"""
        <div style="margin-bottom:0.25rem">
          <span style="font-size:0.75rem;letter-spacing:0.12em;text-transform:uppercase;
                       color:{bc};font-weight:600;">Your Strategy</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title(f"{profile} Portfolio")
    st.markdown(
        f'<span style="font-family:\'JetBrains Mono\',monospace;color:#8899AA;'
        f'font-size:0.8rem;">Risk score: {score}/100</span>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Key Metrics ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Expected CAGR", f"{p_return*100:.1f}%")
    c2.metric("Portfolio Beta", f"{p_beta:.2f}×",
              help="Market sensitivity: 1.0 = moves with index. FIX: previously mislabeled as volatility.")
    c3.metric("Projected Corpus", f"₹{proj['total']/1e5:.1f}L" if proj['total'] >= 1e5
              else f"₹{proj['total']:,.0f}")
    c4.metric("Real Value Today", f"₹{proj['real_value']/1e5:.1f}L" if proj['real_value'] >= 1e5
              else f"₹{proj['real_value']:,.0f}",
              help="Inflation-adjusted at 6% p.a.")

    st.markdown("---")

    # ── Wealth Growth Chart ──  (NEW — not in original)
    st.markdown("### Wealth Trajectory")
    fig_line = go.Figure()
    fig_line.add_trace(go.Scatter(
        x=proj["years"], y=proj["invested"],
        name="Capital Invested",
        fill="tozeroy",
        fillcolor="rgba(91,140,219,0.12)",
        line=dict(color="#5B8CDB", width=2, dash="dot"),
    ))
    fig_line.add_trace(go.Scatter(
        x=proj["years"], y=proj["combined"],
        name="Projected Corpus",
        fill="tonexty",
        fillcolor="rgba(245,166,35,0.18)",
        line=dict(color="#F5A623", width=2.5),
    ))
    fig_line.update_layout(
        **PLOTLY_LAYOUT,
        height=280,
        xaxis=dict(title="Years", gridcolor="#1E3352", zeroline=False),
        yaxis=dict(title="₹ Value", gridcolor="#1E3352", zeroline=False,
                   tickformat=",.0f"),
        legend=dict(bgcolor="rgba(0,0,0,0)", x=0.02, y=0.97),
        hovermode="x unified",
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # ── Allocation Chart ──
    col_chart, col_table = st.columns([1, 1])

    with col_chart:
        st.markdown("### Allocation Mix")
        lbls = [k for k, v in alloc.items() if v > 0.001]
        vals = [v * 100 for k, v in alloc.items() if v > 0.001]
        colors = [ASSET_SPECS[k]["color"] for k in lbls]

        fig_pie = go.Figure(data=[go.Pie(
            labels=lbls, values=vals,
            hole=0.48,
            marker=dict(colors=colors, line=dict(color="#0B1628", width=3)),
            textfont=dict(family="Inter, system-ui", size=11, color="#F5F3EE"),
            hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
        )])
        fig_pie.update_layout(
            **PLOTLY_LAYOUT,
            height=260,
            showlegend=False,
            annotations=[dict(
                text=f"<b>{profile}</b>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=13, color="#F5F3EE", family="Inter, system-ui"),
            )],
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_table:
        st.markdown("### Target Allocation")
        alloc_colors = {k: ASSET_SPECS[k]["color"] for k in ASSET_SPECS}
        for asset, wt in alloc.items():
            if wt > 0.001:
                clr = alloc_colors[asset]
                deploy = initial * wt
                st.markdown(
                    f"""
                    <div style="padding:0.5rem 0;border-bottom:1px solid #1E3352;">
                      <div style="display:flex;justify-content:space-between;
                                  font-size:0.85rem;margin-bottom:0.25rem;">
                        <span style="color:#C8D0DA;">{asset}</span>
                        <span style="font-family:'JetBrains Mono',monospace;
                                     color:#F5F3EE;font-weight:600;">{wt*100:.1f}%</span>
                      </div>
                      <div style="height:3px;background:#1E3352;border-radius:99px;">
                        <div style="width:{wt*100:.1f}%;height:100%;background:{clr};border-radius:99px;"></div>
                      </div>
                      <div style="font-size:0.75rem;color:#8899AA;margin-top:0.25rem;
                                  font-family:'JetBrains Mono',monospace;">
                        Deploy ₹{deploy:,.0f}
                      </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    # ── Summary Callout ──
    total_inv = proj["total_invested"]
    gain      = proj["gain"]
    gain_pct  = (gain / total_inv * 100) if total_inv > 0 else 0
    st.info(
        f"💡 **Projection Summary** — Over {horizon} years you'll invest "
        f"₹{total_inv:,.0f} in total. At {p_return*100:.1f}% CAGR, this grows to "
        f"**₹{proj['total']:,.0f}** (nominal), a gain of **₹{gain:,.0f} ({gain_pct:.0f}%)**. "
        f"Adjusted for 6% inflation, your real purchasing power equivalent is "
        f"**₹{proj['real_value']:,.0f}**."
    )

    # ── Horizon override notice ──
    if horizon < 3:
        st.warning(
            "⚠ **Short-horizon override applied.** Your investment timeline is under 3 years. "
            "PRISM has set the allocation to capital-preservation mode (80% Debt / 20% Gold), "
            "regardless of your risk score."
        )

    st.markdown("---")

    # ── PDF & Restart ──
    pdf_bytes = generate_pdf(ans, alloc, proj, profile, score, p_return, p_beta)

    dl_col, restart_col = st.columns(2)
    with dl_col:
        st.download_button(
            label="📥 Download PDF Report",
            data=pdf_bytes,
            file_name="prism_wealth_strategy.pdf",
            mime="application/pdf",
        )
    with restart_col:
        st.button("↺ Start Over", on_click=restart)

    # ── Disclaimer ──
    st.markdown(
        '<p class="prism-disclaimer">'
        "<b>Disclaimer:</b> This report is produced by an automated quantitative model "
        "for educational and illustrative purposes only. It does not constitute financial "
        "advice, an investment recommendation, or a solicitation to buy or sell any "
        "financial instrument. All projections are hypothetical and based on assumed "
        "constant return rates; actual results will vary. Consult a SEBI-registered "
        "investment advisor before making any financial decisions."
        "</p>",
        unsafe_allow_html=True,
    )
