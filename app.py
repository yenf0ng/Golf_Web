# ============================================================
#  Golf Swing Tracker & Analytics Dashboard  v3
#  app.py  --  Streamlit + Supabase
#  Changes: title field, edit modal, Golf Knowledge page
# ============================================================

import datetime
import hashlib

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from supabase import create_client, Client

# -- Page config ----------------------------------------------
st.set_page_config(
    page_title="Golf Swing Tracker",
    page_icon=":golfer:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Theme definitions ----------------------------------------
THEMES = {
    "light": {
        # Green fairway + parchment beige
        "bg":          "#f5f0e8",   # warm parchment
        "bg2":         "#ede8dc",   # slightly darker parchment
        "sidebar_bg":  "#2d5a27",   # deep fairway green
        "sidebar_txt": "#f5f0e8",
        "card_bg":     "#fffdf7",
        "card_border": "#d4c9a8",
        "text":        "#1a2e18",   # dark forest
        "text_muted":  "#6b7c69",
        "accent":      "#2d7a22",   # fairway green
        "accent2":     "#8b6914",   # warm gold
        "heading":     "#1e5c19",
        "btn_bg":      "linear-gradient(135deg, #2d7a22, #4a9e3f)",
        "btn_color":   "#ffffff",
        "badge_on_accent": "#ffffff",
        "input_bg":    "#fffdf7",
        "input_border":"#c4b88a",
        "hr":          "#d4c9a8",
        "tab_active":  "#2d7a22",
        "tip_bg":      "#e8f5e5",
        "tip_border":  "#2d7a22",
        "tip_color":   "#1e5c19",
        "plot_paper":  "#f5f0e8",
        "plot_bg":     "#ede8dc",
        "plot_font":   "#1a2e18",
        "plot_grid":   "#c4b88a",
        "plot_zero":   "#2d7a22",
        "plot_colors": ["#2d7a22","#8b6914","#c0392b","#1a6b8a","#7d3c98","#d4892a","#2e86c1"],
    },
    "dark": {
        # Original dark slate theme
        "bg":          "#0d1117",
        "bg2":         "#161b22",
        "sidebar_bg":  "#161b22",
        "sidebar_txt": "#e6edf3",
        "card_bg":     "#161b22",
        "card_border": "#21262d",
        "text":        "#e6edf3",
        "text_muted":  "#8b949e",
        "accent":      "#58a6ff",
        "accent2":     "#3fb950",
        "heading":     "#58a6ff",
        "btn_bg":      "linear-gradient(135deg, #1f6feb, #388bfd)",
        "btn_color":   "#ffffff",
        "badge_on_accent": "#ffffff",
        "input_bg":    "#0d1117",
        "input_border":"#30363d",
        "hr":          "#21262d",
        "tab_active":  "#58a6ff",
        "tip_bg":      "#1c2333",
        "tip_border":  "#58a6ff",
        "tip_color":   "#79c0ff",
        "plot_paper":  "#161b22",
        "plot_bg":     "#161b22",
        "plot_font":   "#e6edf3",
        "plot_grid":   "#21262d",
        "plot_zero":   "#30363d",
        "plot_colors": ["#58a6ff","#3fb950","#e3b341","#f78166","#bc8cff","#79c0ff","#56d364"],
    },
}

def get_theme():
    return THEMES["dark"] if st.session_state.get("dark_theme", False) else THEMES["light"]

def inject_css(t: dict):
    st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

  /* ── Base ── */
  html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    color: {t["text"]};
  }}
  .stApp {{
    background-color: {t["bg"]} !important;
  }}

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] > div {{
    background-color: {t["sidebar_bg"]} !important;
  }}
  section[data-testid="stSidebar"],
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span,
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] div,
  section[data-testid="stSidebar"] small,
  section[data-testid="stSidebar"] a {{
    color: {t["sidebar_txt"]} !important;
  }}
  section[data-testid="stSidebar"] hr {{
    border-color: {t["sidebar_txt"]}33 !important;
  }}

  /* ── Headings ── */
  h1, h2, h3, h4 {{
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 2px;
  }}
  h1 {{ font-size: 2.6rem !important; color: {t["heading"]} !important; }}
  h2 {{ font-size: 1.9rem !important; color: {t["heading"]} !important; }}
  h3 {{ font-size: 1.4rem !important; color: {t["heading"]} !important; }}

  /* ── Global text nodes ── */
  p, span, li, td, th, label, div {{
    color: {t["text"]};
  }}
  small, .stCaption, [data-testid="stCaptionContainer"] {{
    color: {t["text_muted"]} !important;
  }}
  a {{ color: {t["accent"]}; }}

  /* ── Markdown ── */
  .stMarkdown p,
  .stMarkdown li,
  .stMarkdown span {{
    color: {t["text"]} !important;
  }}

  /* ── Custom cards ── */
  .metric-card {{
    background: {t["card_bg"]};
    border: 1px solid {t["card_border"]};
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  }}
  .metric-card .label {{
    font-size: 0.72rem; text-transform: uppercase;
    letter-spacing: 1.5px; color: {t["text_muted"]}; margin-bottom: 0.25rem;
  }}
  .metric-card .value {{
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem; color: {t["accent"]}; line-height: 1;
  }}
  .metric-card .sub {{
    font-size: 0.75rem; color: {t["text_muted"]}; margin-top: 0.2rem;
  }}

  /* ── Badges ── */
  .badge {{
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 6px;
  }}
  .badge-Driver  {{ background:{t["accent"]};   color:{t["sidebar_txt"]}; }}
  .badge-Irons   {{ background:transparent; color:{t["accent"]};  border:2px solid {t["accent"]}; }}
  .badge-Woods   {{ background:transparent; color:{t["accent2"]}; border:2px solid {t["accent2"]}; }}
  .badge-Putting {{ background:transparent; color:{t["accent2"]}; border:2px solid {t["accent2"]}; }}

  /* ── Media / know cards ── */
  .media-wrapper, .know-card {{
    background: {t["card_bg"]};
    border: 1px solid {t["card_border"]};
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  }}
  .media-title {{
    padding: 0.5rem 0.8rem 0.1rem;
    font-size: 0.95rem; font-weight: 600; color: {t["text"]};
  }}
  .media-meta {{
    padding: 0.35rem 0.8rem 0.6rem;
    font-size: 0.78rem; color: {t["text_muted"]};
  }}
  .media-meta strong {{ color: {t["text"]}; }}
  .know-card {{ padding: 1.2rem 1.4rem; overflow: visible; }}
  .know-card h4 {{
    font-family: 'Bebas Neue', sans-serif; font-size: 1.2rem;
    letter-spacing: 1.5px; color: {t["heading"]} !important; margin-bottom: 0.4rem;
  }}
  .know-card p {{ font-size: 0.88rem; color: {t["text"]}; line-height: 1.65; margin: 0; }}

  /* ── Level pills ── */
  .level-pill {{
    display: inline-block; padding: 1px 9px; border-radius: 20px;
    font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1px; margin-left: 8px; vertical-align: middle;
  }}
  .level-beginner     {{ background:#2ea04318; color:#1e6b14; border:1px solid #2ea043; }}
  .level-intermediate {{ background:#d2992218; color:#7a5800; border:1px solid #d29922; }}
  .level-advanced     {{ background:#6e40c918; color:#5a2d91; border:1px solid #6e40c9; }}

  /* ── Tip box ── */
  .tip-box {{
    background: {t["tip_bg"]};
    border-left: 3px solid {t["tip_border"]};
    border-radius: 0 8px 8px 0;
    padding: 0.7rem 1rem; margin-top: 0.7rem;
    font-size: 0.84rem; color: {t["tip_color"]};
  }}

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {{
    background: transparent !important;
    gap: 4px;
  }}
  .stTabs [role="tab"] {{
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 1.05rem; letter-spacing: 1.5px;
    color: {t["text_muted"]} !important;
    background: transparent !important;
  }}
  .stTabs [aria-selected="true"] {{
    color: {t["tab_active"]} !important;
    border-bottom: 2px solid {t["tab_active"]} !important;
  }}

  /* ── Form inputs ── */
  input, textarea, select,
  [data-baseweb="input"] input,
  [data-baseweb="textarea"] textarea,
  [data-baseweb="select"] div {{
    background-color: {t["input_bg"]} !important;
    border-color: {t["input_border"]} !important;
    color: {t["text"]} !important;
    border-radius: 8px !important;
  }}
  [data-baseweb="input"],
  [data-baseweb="textarea"],
  [data-baseweb="base-input"] {{
    background-color: {t["input_bg"]} !important;
    border-color: {t["input_border"]} !important;
    border-radius: 8px !important;
  }}
  /* Placeholder text */
  input::placeholder, textarea::placeholder {{
    color: {t["text_muted"]} !important;
    opacity: 0.7;
  }}
  /* Dropdown options */
  [data-baseweb="popover"] li,
  [data-baseweb="menu"] li {{
    background-color: {t["card_bg"]} !important;
    color: {t["text"]} !important;
  }}
  [data-baseweb="popover"] li:hover {{
    background-color: {t["accent"]}22 !important;
  }}

  /* ── Buttons — ALL variants ── */
  .stButton > button,
  .stFormSubmitButton > button,
  button[kind="primary"],
  button[kind="secondary"] {{
    background: {t["btn_bg"]} !important;
    color: {t["btn_color"]} !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.55rem 1.4rem !important;
    transition: opacity .15s !important;
  }}
  .stButton > button:hover,
  .stFormSubmitButton > button:hover {{
    opacity: 0.85 !important;
    color: {t["btn_color"]} !important;
  }}

  /* ── Alerts / info boxes ── */
  [data-testid="stAlert"],
  [data-testid="stAlert"] p,
  [data-testid="stAlert"] span {{
    color: {t["text"]} !important;
  }}

  /* ── Expander ── */
  [data-testid="stExpander"] summary,
  [data-testid="stExpander"] summary p,
  .streamlit-expanderHeader p {{
    color: {t["text"]} !important;
    font-weight: 600;
  }}
  [data-testid="stExpander"] {{
    background: {t["card_bg"]} !important;
    border: 1px solid {t["card_border"]} !important;
    border-radius: 10px !important;
  }}

  /* ── Dataframe ── */
  [data-testid="stDataFrame"] *,
  .stDataFrame * {{
    color: {t["text"]} !important;
  }}
  [data-testid="stDataFrame"] th {{
    background: {t["card_border"]} !important;
    color: {t["text"]} !important;
  }}

  /* ── Radio / checkbox ── */
  [data-testid="stRadio"] label p,
  [data-testid="stCheckbox"] label p {{
    color: {t["text"]} !important;
  }}

  /* ── Multiselect tags ── */
  [data-baseweb="tag"] {{
    background-color: {t["accent"]}22 !important;
    color: {t["accent"]} !important;
  }}
  [data-baseweb="tag"] span {{ color: {t["accent"]} !important; }}

  /* ── Divider ── */
  hr {{ border-color: {t["hr"]} !important; }}

  /* ── Mobile ── */
  @media (max-width: 640px) {{
    h1 {{ font-size: 2rem !important; }}
    .metric-card .value {{ font-size: 1.7rem; }}
  }}
</style>
""", unsafe_allow_html=True)

# -- Supabase client ------------------------------------------
@st.cache_resource
def get_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = get_supabase()
BUCKET   = st.secrets.get("STORAGE_BUCKET", "swing-clips")

# -- Session state defaults -----------------------------------
defaults = {
    "is_admin": False,
    "shot_shape": "Straight",
    "auth_error": False,
    "edit_id": None,
    "dark_theme": False,      # False = green/beige light, True = dark
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Inject theme CSS (must run before any widgets render)
inject_css(get_theme())

# -- Plotly theme (built dynamically per render) --------------
def get_plot_layout():
    t = get_theme()
    return dict(
        paper_bgcolor=t["plot_paper"], plot_bgcolor=t["plot_bg"],
        font_color=t["plot_font"], font_family="DM Sans",
        colorway=t["plot_colors"],
        margin=dict(l=16, r=16, t=40, b=16),
    )

def get_axis_style():
    t = get_theme()
    return dict(gridcolor=t["plot_grid"], zerolinecolor=t["plot_zero"])

# -- Media helpers --------------------------------------------
VIDEO_EXTS = {"mp4","mov","webm","avi"}
GIF_EXTS   = {"gif"}

MIME_MAP = {
    "mp4":"video/mp4","mov":"video/quicktime","webm":"video/webm","avi":"video/x-msvideo",
    "jpg":"image/jpeg","jpeg":"image/jpeg","png":"image/png","webp":"image/webp","gif":"image/gif",
}

def media_ext(path: str) -> str:
    return path.rsplit(".", 1)[-1].lower().split("?")[0]

def media_type_label(ext: str) -> str:
    if ext in VIDEO_EXTS: return "Video"
    if ext in GIF_EXTS:   return "GIF"
    return "Image"

def render_media(url: str, ext: str):
    if ext in VIDEO_EXTS:
        try:
            st.video(url)
        except Exception:
            st.markdown(f'<a href="{url}" target="_blank">Open video</a>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<img src="{url}" style="width:100%;border-radius:6px;display:block;" alt="media">',
            unsafe_allow_html=True)

# =============================================================
#  SIDEBAR
# =============================================================
with st.sidebar:
    st.markdown("## Golf Swing Tracker")
    st.caption("Personal Golf Analytics")
    st.divider()

    if not st.session_state.is_admin:
        st.markdown("**Admin Login**")
        pw_input = st.text_input("Password", type="password", key="pw_field",
                                 placeholder="Enter admin password...")
        if st.button("Unlock Admin", use_container_width=True):
            if pw_input == st.secrets.get("ADMIN_PASSWORD", ""):
                st.session_state.is_admin  = True
                st.session_state.auth_error = False
                st.rerun()
            else:
                st.session_state.auth_error = True
        if st.session_state.auth_error:
            st.error("Incorrect password.")
        st.caption("Viewing in read-only mode")
    else:
        st.success("Admin Mode Active")
        if st.button("Lock & Sign Out", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()

    st.divider()
    st.markdown("**Navigate**")
    page = st.radio(
        "", ["Dashboard", "Media Vault", "Golf Knowledge", "Log Session", "Upload Media"],
        label_visibility="collapsed"
    )
    if page in ["Log Session", "Upload Media"] and not st.session_state.is_admin:
        st.warning("Admin access required.")
        page = "Dashboard"

    st.divider()
    theme_label = "Switch to Dark Theme" if not st.session_state.dark_theme else "Switch to Green Theme"
    if st.button(theme_label, use_container_width=True):
        st.session_state.dark_theme = not st.session_state.dark_theme
        st.rerun()
    st.caption("Built with Streamlit + Supabase")

# =============================================================
#  CONSTANTS & DATA HELPERS
# =============================================================
CLUB_ORDER  = ["Driver","3-Wood","5-Wood","Hybrid",
               "3-Iron","4-Iron","5-Iron","6-Iron","7-Iron","8-Iron","9-Iron",
               "PW","GW","SW","LW","Putter"]
SHOT_SHAPES = ["Straight","Draw","Fade","Push","Pull","Slice","Hook"]
CATEGORIES  = ["Driver","Irons","Woods","Putting"]

@st.cache_data(ttl=60)
def fetch_performance_logs() -> pd.DataFrame:
    res = supabase.table("performance_logs").select("*").order("session_date", desc=True).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df["session_date"] = pd.to_datetime(df["session_date"])
        return df
    return pd.DataFrame(columns=["id","created_at","session_date","club_used",
                                  "total_distance","carry_distance","shot_shape","notes"])

@st.cache_data(ttl=60)
def fetch_video_vault() -> pd.DataFrame:
    res = supabase.table("video_vault").select("*").order("clip_date", desc=True).execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df["clip_date"] = pd.to_datetime(df["clip_date"])
        # back-fill title column if it doesn't exist yet in old rows
        if "title" not in df.columns:
            df["title"] = ""
        df["title"] = df["title"].fillna("")
        return df
    return pd.DataFrame(columns=["id","created_at","clip_date","category",
                                  "title","notes","storage_path","public_url"])

def invalidate_cache():
    fetch_performance_logs.clear()
    fetch_video_vault.clear()

# =============================================================
#  PAGE: DASHBOARD
# =============================================================
if page == "Dashboard":
    st.markdown("# Analytics Dashboard")
    df = fetch_performance_logs()

    if df.empty:
        st.info("No performance data yet. Log some sessions to see analytics here.")
        st.stop()

    total_shots = len(df)
    avg_dist    = df["total_distance"].mean()
    best_dist   = df["total_distance"].max()
    sessions    = df["session_date"].dt.date.nunique()

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub in [
        (c1, "Total Shots",  f"{total_shots:,}", "logged"),
        (c2, "Avg Distance", f"{avg_dist:.0f}",  "yards"),
        (c3, "Best Shot",    f"{best_dist:,}",   "yards"),
        (c4, "Sessions",     f"{sessions}",      "days out"),
    ]:
        col.markdown(f"""<div class="metric-card">
          <div class="label">{label}</div>
          <div class="value">{val}</div>
          <div class="sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # Chart 1: Club Distance Avg vs Max
    st.markdown("### Club Distance Overview")
    grp = df.groupby("club_used")["total_distance"].agg(Avg="mean", Max="max").reset_index()
    grp = grp[grp["club_used"].isin(CLUB_ORDER)]
    grp["club_used"] = pd.Categorical(grp["club_used"], categories=CLUB_ORDER, ordered=True)
    grp = grp.sort_values("club_used")
    fig1 = go.Figure()
    fig1.add_bar(name="Avg Distance", x=grp["club_used"], y=grp["Avg"],
                 marker_color="#388bfd", opacity=0.85,
                 text=grp["Avg"].round(0).astype(int),
                 textposition="outside", textfont_color="#8b949e")
    fig1.add_bar(name="Max Distance", x=grp["club_used"], y=grp["Max"],
                 marker_color="#3fb950", opacity=0.55,
                 text=grp["Max"], textposition="outside", textfont_color="#8b949e")
    fig1.update_layout(**get_plot_layout(), barmode="group",
                       legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#8b949e"),
                       yaxis_title="Yards", xaxis_title=None, height=380)
    fig1.update_xaxes(**get_axis_style())
    fig1.update_yaxes(**get_axis_style())
    st.plotly_chart(fig1, use_container_width=True)
    st.divider()

    # Chart 2: Shot Dispersion
    st.markdown("### Shot Shape Dispersion")
    col_a, _ = st.columns([1, 2])
    with col_a:
        disp_clubs = st.multiselect("Filter Clubs", options=sorted(df["club_used"].unique()),
                                    default=sorted(df["club_used"].unique())[:4], key="disp_clubs")
    disp_df   = df[df["club_used"].isin(disp_clubs)] if disp_clubs else df
    shape_grp = disp_df.groupby(["club_used","shot_shape"]).size().reset_index(name="count")
    shape_grp["shot_shape"] = pd.Categorical(shape_grp["shot_shape"], categories=SHOT_SHAPES, ordered=True)
    fig2 = px.bar(shape_grp.sort_values("shot_shape"), x="shot_shape", y="count",
                  color="club_used", barmode="group",
                  labels={"shot_shape":"Shot Shape","count":"# of Shots","club_used":"Club"})
    fig2.update_layout(**get_plot_layout(), height=380,
                       legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#8b949e"),
                       xaxis_title=None, yaxis_title="Shots")
    fig2.update_xaxes(**get_axis_style())
    fig2.update_yaxes(**get_axis_style())
    st.plotly_chart(fig2, use_container_width=True)
    st.divider()

    # Chart 3: Consistency Score
    st.markdown("### Consistency Score  (lower = more consistent)")
    cons = df.groupby("club_used")["total_distance"].agg(SD="std", Count="count").dropna().reset_index()
    cons = cons[(cons["Count"] >= 2) & cons["club_used"].isin(CLUB_ORDER)]
    cons["club_used"] = pd.Categorical(cons["club_used"], categories=CLUB_ORDER, ordered=True)
    cons = cons.sort_values("club_used")
    cons["color"] = cons["SD"].apply(lambda v: "#3fb950" if v < 10 else ("#e3b341" if v < 20 else "#f78166"))
    fig3 = go.Figure(go.Bar(x=cons["club_used"], y=cons["SD"].round(1), marker_color=cons["color"],
                             text=cons["SD"].round(1), textposition="outside", textfont_color="#8b949e"))
    fig3.update_layout(**get_plot_layout(), height=340, yaxis_title="Std Dev (yards)", xaxis_title=None,
                       annotations=[dict(text="Green < 10 yds  |  Yellow 10-20 yds  |  Red > 20 yds",
                                        xref="paper", yref="paper", x=1, y=1.06, showarrow=False,
                                        font_color="#8b949e", font_size=11, xanchor="right")])
    fig3.update_xaxes(**get_axis_style())
    fig3.update_yaxes(**get_axis_style())
    st.plotly_chart(fig3, use_container_width=True)
    st.divider()

    # Chart 4: Distance Trend
    st.markdown("### Distance Trend")
    trend_club = st.selectbox("Club", options=sorted(df["club_used"].unique()), key="trend_club")
    trend_df   = df[df["club_used"] == trend_club].sort_values("session_date")
    fig4 = go.Figure()
    fig4.add_scatter(x=trend_df["session_date"], y=trend_df["total_distance"],
                     mode="lines+markers", line=dict(color="#58a6ff", width=2),
                     marker=dict(size=7, color="#79c0ff"), name="Total Dist")
    fig4.add_scatter(x=trend_df["session_date"], y=trend_df["carry_distance"],
                     mode="lines+markers", line=dict(color="#3fb950", width=2, dash="dot"),
                     marker=dict(size=6, color="#56d364"), name="Carry")
    fig4.update_layout(**get_plot_layout(), height=320, yaxis_title="Yards", xaxis_title=None,
                       legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#8b949e"))
    fig4.update_xaxes(**get_axis_style())
    fig4.update_yaxes(**get_axis_style())
    st.plotly_chart(fig4, use_container_width=True)

    with st.expander("Raw Session Data"):
        st.dataframe(df.sort_values("session_date", ascending=False)
                       .drop(columns=["id","created_at"], errors="ignore")
                       .rename(columns={"session_date":"Date","club_used":"Club",
                                        "total_distance":"Total (yds)","carry_distance":"Carry (yds)",
                                        "shot_shape":"Shape","notes":"Notes"}),
                     use_container_width=True, hide_index=True)

# =============================================================
#  PAGE: MEDIA VAULT
# =============================================================
elif page == "Media Vault":
    st.markdown("# Media Vault")
    st.caption("Videos, GIFs & images of your swings")
    vdf = fetch_video_vault()

    # Filters
    col_f1, col_f2, col_f3 = st.columns([3, 1, 1])
    with col_f1:
        cat_filter  = st.multiselect("Category", options=CATEGORIES, default=CATEGORIES, key="cat_filter")
    with col_f2:
        sort_order  = st.selectbox("Sort", ["Newest First","Oldest First"], key="vsort")
    with col_f3:
        type_filter = st.selectbox("Media Type", ["All","Video","Image","GIF"], key="type_filter")

    if vdf.empty:
        st.info("No media uploaded yet. Admins can upload via Upload Media.")
        st.stop()

    vdf["ext"]        = vdf["storage_path"].apply(media_ext)
    vdf["type_label"] = vdf["ext"].apply(media_type_label)
    fdf = vdf[vdf["category"].isin(cat_filter)] if cat_filter else vdf
    if type_filter != "All":
        fdf = fdf[fdf["type_label"] == type_filter]
    fdf = fdf.sort_values("clip_date", ascending=(sort_order == "Oldest First"))

    if fdf.empty:
        st.warning("No items match the selected filters.")
        st.stop()

    st.caption(f"Showing **{len(fdf)}** item(s)")

    # ── Edit modal (shown above grid when edit_id is set) ────────
    if st.session_state.is_admin and st.session_state.edit_id is not None:
        eid  = st.session_state.edit_id
        erow = vdf[vdf["id"] == eid]
        if not erow.empty:
            erow = erow.iloc[0]
            st.markdown("---")
            st.markdown("### Edit Media Item")
            with st.form("edit_form"):
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_title = st.text_input("Title", value=erow.get("title","") or "", key="e_title")
                    e_cat   = st.selectbox("Category", CATEGORIES,
                                           index=CATEGORIES.index(erow["category"]) if erow["category"] in CATEGORIES else 0,
                                           key="e_cat")
                    e_date  = st.date_input("Date",
                                            value=erow["clip_date"].date() if pd.notna(erow["clip_date"]) else datetime.date.today(),
                                            key="e_date")
                with ec2:
                    e_notes = st.text_area("Notes / Description", value=erow.get("notes","") or "", key="e_notes", height=120)
                    e_file  = st.file_uploader("Replace file (optional)",
                                               type=["mp4","mov","webm","avi","jpg","jpeg","png","webp","gif"],
                                               key="e_file")

                col_save, col_cancel = st.columns(2)
                with col_save:
                    save_btn = st.form_submit_button("Save Changes", use_container_width=True)
                with col_cancel:
                    cancel_btn = st.form_submit_button("Cancel", use_container_width=True)

            if cancel_btn:
                st.session_state.edit_id = None
                st.rerun()

            if save_btn:
                update_payload = {
                    "title"    : e_title.strip() or None,
                    "category" : e_cat,
                    "clip_date": str(e_date),
                    "notes"    : e_notes.strip() or None,
                }
                # Replace file if provided
                if e_file is not None:
                    ext       = e_file.name.rsplit(".", 1)[-1].lower()
                    mime_type = MIME_MAP.get(ext, "application/octet-stream")
                    ts        = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                    new_path  = f"{e_cat}/{ts}_{e_file.name.replace(' ','_')}"
                    try:
                        # Remove old file
                        supabase.storage.from_(BUCKET).remove([erow["storage_path"]])
                    except Exception:
                        pass
                    supabase.storage.from_(BUCKET).upload(
                        path=new_path, file=e_file.read(),
                        file_options={"content-type": mime_type})
                    new_url = supabase.storage.from_(BUCKET).get_public_url(new_path)
                    update_payload["storage_path"] = new_path
                    update_payload["public_url"]   = new_url

                supabase.table("video_vault").update(update_payload).eq("id", eid).execute()
                invalidate_cache()
                st.session_state.edit_id = None
                st.success("Item updated.")
                st.rerun()
            st.markdown("---")

    # ── Media grid ───────────────────────────────────────────────
    cols_per_row = 2
    rows = [fdf.iloc[i:i+cols_per_row] for i in range(0, len(fdf), cols_per_row)]
    for row in rows:
        grid_cols = st.columns(cols_per_row)
        for col, (_, clip) in zip(grid_cols, row.iterrows()):
            badge_cls = f"badge-{clip['category']}"
            date_str  = clip["clip_date"].strftime("%d %b %Y") if pd.notna(clip["clip_date"]) else "-"
            title_str = clip.get("title","") or ""
            notes_str = clip.get("notes","") or "No notes"
            ext       = clip["ext"]
            with col:
                st.markdown(f"""
                <div class="media-wrapper">
                  <div style="padding:0.6rem 0.8rem 0.2rem;display:flex;gap:6px;align-items:center;">
                    <span class="badge {badge_cls}">{clip['category']}</span>
                    <span style="font-size:0.7rem;color:#8b949e;">{clip['type_label']}</span>
                  </div>
                  {'<div class="media-title">' + title_str + '</div>' if title_str else ''}
                """, unsafe_allow_html=True)
                render_media(clip["public_url"], ext)
                st.markdown(f"""
                  <div class="media-meta"><strong>{date_str}</strong><br>{notes_str}</div>
                </div>""", unsafe_allow_html=True)

                if st.session_state.is_admin:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("Edit", key=f"edit_{clip['id']}", use_container_width=True):
                            st.session_state.edit_id = int(clip["id"])
                            st.rerun()
                    with btn_col2:
                        if st.button("Delete", key=f"del_{clip['id']}", use_container_width=True):
                            try:
                                supabase.storage.from_(BUCKET).remove([clip["storage_path"]])
                            except Exception:
                                pass
                            supabase.table("video_vault").delete().eq("id", int(clip["id"])).execute()
                            invalidate_cache()
                            st.success("Deleted.")
                            st.rerun()

# =============================================================
#  PAGE: GOLF KNOWLEDGE
# =============================================================
elif page == "Golf Knowledge":
    st.markdown("# Golf Knowledge Base")
    st.caption("Ball flight, shot shapes, spin physics, swing mechanics -- filterable by level")

    level_filter = st.radio(
        "Knowledge Level",
        ["All Levels", "Beginner", "Intermediate", "Advanced"],
        horizontal=True, key="know_level"
    )

    def show_card(title, level, body, tip=None):
        if level_filter not in ("All Levels", level):
            return
        lvl_cls = f"level-{level.lower()}"
        tip_html = f'<div class="tip-box">Pro tip: {tip}</div>' if tip else ""
        st.markdown(f"""
        <div class="know-card">
          <h4>{title} <span class="level-pill {lvl_cls}">{level}</span></h4>
          <p>{body}</p>
          {tip_html}
        </div>""", unsafe_allow_html=True)

    # ── TAB STRUCTURE ────────────────────────────────────────────
    tabs = st.tabs(["Ball Flight Laws", "Shot Shapes", "Spin & Physics",
                    "Swing Mechanics", "Club Selection", "Practice Drills"])

    # ── TAB 1: Ball Flight Laws ──────────────────────────────────
    with tabs[0]:
        st.markdown("### The New Ball Flight Laws")
        show_card(
            "What Actually Starts the Ball",
            "Beginner",
            "The ball starts <b>where the clubface is pointing</b> at impact — not where the swing path goes. "
            "This overturned the old 'ball starts on the path' myth. Face angle accounts for roughly 75-85% "
            "of the initial launch direction.",
            tip="If you want to fix your starting line, fix your face angle first."
        )
        show_card(
            "Path vs Face: The Curvature Equation",
            "Intermediate",
            "The ball curves away from the path <b>relative to the face</b>. If your face is 2 degrees open "
            "to the path, the ball fades. The bigger the gap between face and path, the more curve. "
            "Formula: <code>Curve = k * (Path - Face)</code> where k is a spin constant (~0.7 for iron shots).",
            tip="A 5-degree path-face gap produces roughly a 15-20 yard curve at 150 yards carry."
        )
        show_card(
            "Dynamic Loft & Launch Angle",
            "Advanced",
            "Dynamic loft (the loft of the face at impact) is what actually controls launch angle and spin rate. "
            "A 7-iron with 34 degrees static loft might deliver only 26 degrees dynamic loft at impact due to "
            "shaft lean. Optimal launch angle is roughly 75-80% of dynamic loft. Spin loft (dynamic loft minus "
            "angle of attack) drives spin rate -- higher spin loft = more backspin.",
            tip="Use Trackman or Garmin to track dynamic loft. Pros typically deloft by 4-8 degrees vs static loft."
        )

        # Plotly: Face Angle vs Path Visualisation
        st.markdown("#### Face / Path Relationship Chart")
        face_angles = list(range(-10, 11))
        fig_fp = go.Figure()
        for path in [-5, 0, 5]:
            curves = [0.75 * (path - f) for f in face_angles]
            fig_fp.add_scatter(
                x=face_angles, y=curves,
                mode="lines", name=f"Path {path:+d} deg",
                line=dict(width=2))
        fig_fp.add_vline(x=0, line_color="#30363d", line_dash="dot")
        fig_fp.add_hline(y=0, line_color="#30363d", line_dash="dot")
        fig_fp.update_layout(
            **get_plot_layout(), height=340,
            xaxis_title="Face Angle (deg, - = closed, + = open)",
            yaxis_title="Curve (deg, - = draw, + = fade)",
            legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#8b949e"),
        )
        fig_fp.update_layout(title="Ball Curve by Face & Path Angle")
        fig_fp.update_layout(title_font=dict(color="#8b949e", size=13))
        st.plotly_chart(fig_fp, use_container_width=True)

    # ── TAB 2: Shot Shapes ───────────────────────────────────────
    with tabs[1]:
        st.markdown("### Shot Shape Reference")

        shapes_data = [
            ("Straight", "Beginner",
             "Face and path are <b>perfectly square</b> to each other and to the target line. "
             "Extremely rare in practice; even pros play a slight preference shape.",
             "Don't chase 'perfectly straight' -- a controlled draw or fade is more repeatable."),
            ("Draw", "Beginner",
             "Ball curves gently from <b>right to left</b> (for a right-handed golfer). "
             "Produced by an in-to-out swing path with a face slightly closed to that path. "
             "Generates lower spin, more run, and typically more distance.",
             "Aim your body right of the target, keep the face at the target, swing along your body line."),
            ("Fade", "Beginner",
             "Ball curves gently from <b>left to right</b>. Path is out-to-in relative to the face. "
             "Produces higher spin and a softer landing. Jack Nicklaus and Lee Trevino were famous faders.",
             "Aim body left, keep face at target, swing left. The ball will start left and drift back."),
            ("Hook", "Intermediate",
             "An <b>exaggerated draw</b> with too much face-to-path gap. Often caused by a very strong grip, "
             "forearm rotation through impact, or excessive in-to-out path with a closed face. "
             "Ball can dive sharply left and lose height quickly.",
             "Check grip neutrality. Ensure your forearms aren't rolling excessively through the hitting zone."),
            ("Slice", "Intermediate",
             "An <b>exaggerated fade</b> -- the most common shot shape problem for amateurs. "
             "Typically caused by an out-to-in swing path with an open face, creating high side-spin. "
             "Creates a weak shot that loses significant distance.",
             "Visualise swinging to the 'right field' (for a right-hander). Don't start the downswing with your shoulder."),
            ("Push", "Intermediate",
             "Ball launches <b>straight right</b> of the target with minimal curve. "
             "Face and path are both pointing right. Usually from an in-to-out path with a square face to that path.",
             "Check your stance alignment -- you may be set up too closed (aimed right)."),
            ("Pull", "Intermediate",
             "Ball launches <b>straight left</b> with minimal curve. "
             "Both face and path point left at impact. Commonly from casting over the top with the lead shoulder.",
             "Feel your trail elbow drop toward your hip in transition. Keep the lead shoulder from opening too early."),
            ("Push-Slice", "Advanced",
             "Ball starts <b>right then curves further right</b>. Path is in-to-out but face is even more open to that path. "
             "A combination that maximises side-spin. Spin axis is severely tilted.",
             "Focus on face angle first -- get the face closed to the path before worrying about path direction."),
            ("Pull-Hook", "Advanced",
             "Ball starts <b>left then curves further left</b>. Severe out-to-in path with a face even more closed. "
             "Often seen in players who flip the hands through impact or have a very strong grip.",
             "Strengthen your stance, weaken your grip slightly, and feel more 'hold off' through impact."),
        ]

        for title, level, body, tip in shapes_data:
            show_card(title, level, body, tip)

        # Shot shape radar diagram
        st.markdown("#### Shot Shape Dispersion Map")
        st.caption("Relative curvature and height of each shot shape (conceptual)")

        shapes_plot = pd.DataFrame({
            "Shape":  ["Straight","Draw","Fade","Hook","Slice","Push","Pull"],
            "LR_Curve": [0, -12, 12, -28, 28, 2, -2],
            "Height": [5, 4, 6, 3, 5, 4, 5],
            "Distance_Loss": [2, 1, 5, 10, 25, 3, 3],  # all >= 1 so bubble always visible
        })
        fig_sh = px.scatter(
            shapes_plot, x="LR_Curve", y="Height",
            size="Distance_Loss", color="Shape",
            text="Shape", size_max=30,
            labels={"LR_Curve":"Left (-) / Right (+) Curve (approx yds at 150y)",
                    "Height":"Relative Trajectory Height"},
        )
        fig_sh.update_traces(textposition="top center")
        fig_sh.add_vline(x=0, line_color="#30363d", line_dash="dot")
        fig_sh.update_layout(**get_plot_layout(), height=420, showlegend=False)
        fig_sh.update_xaxes(**get_axis_style())
        fig_sh.update_yaxes(**get_axis_style())
        fig_sh.update_xaxes(zerolinecolor="#58a6ff", zeroline=True)
        st.plotly_chart(fig_sh, use_container_width=True)
        st.caption("Bubble size = relative distance loss vs straight shot")

    # ── TAB 3: Spin & Physics ────────────────────────────────────
    with tabs[2]:
        st.markdown("### Ball Spin & Flight Physics")

        show_card(
            "Backspin: The Engine of Distance",
            "Beginner",
            "Backspin creates the Magnus effect -- air pressure below the ball is higher than above, "
            "generating lift. Without it, the ball would drop like a rock. "
            "Typical spin rates: Driver 2000-2800 rpm, 7-iron 6000-7000 rpm, Wedges 8000-12000 rpm.",
            tip="Too little driver spin = ball drops out of sky early. Too much = ballooning flight. Aim for 2200-2500 rpm."
        )
        show_card(
            "Sidespin & Spin Axis Tilt",
            "Intermediate",
            "Sidespin is actually a <b>tilt of the spin axis</b>, not a separate spin type. "
            "A tilted axis causes the Magnus lift to act sideways, curving the ball. "
            "A 10-degree axis tilt left produces a gentle draw; 20+ degrees produces a hook. "
            "Axis tilt is entirely driven by the face-to-path relationship at impact.",
            tip="The ball doesn't have two separate spins -- it has ONE spin on a tilted axis."
        )
        show_card(
            "Spin Loft & Compression",
            "Advanced",
            "Spin loft = dynamic loft - angle of attack. A steep angle of attack with a high-lofted face "
            "creates massive spin loft and high spin. Optimal spin loft for a driver is 12-15 degrees "
            "(low dynamic loft + slight positive angle of attack). For wedges, you <i>want</i> high spin loft "
            "(40-50 degrees) to generate stopping power. Ball compression is a red herring for most amateurs "
            "-- it only materially affects shots above 100 mph swing speed.",
            tip="Sweep your driver (slightly positive AoA). Hit down on irons (negative AoA). They need opposite attacks."
        )

        # Spin rate chart by club
        st.markdown("#### Typical Spin Rates by Club")
        spin_data = pd.DataFrame({
            "Club":  ["Driver","3-Wood","5-Wood","Hybrid","4-Iron","6-Iron","8-Iron","PW","SW"],
            "Min":   [1800, 3000, 3500, 4000, 4500, 5500, 7000, 8500, 10000],
            "Avg":   [2400, 3800, 4200, 4600, 5200, 6500, 8000, 9500, 11000],
            "Max":   [3200, 4800, 5500, 5500, 6500, 8000, 9500, 11000, 13000],
        })
        fig_spin = go.Figure()
        fig_spin.add_bar(name="Min", x=spin_data["Club"], y=spin_data["Min"],
                         marker_color="#388bfd", opacity=0.4)
        fig_spin.add_bar(name="Avg", x=spin_data["Club"], y=spin_data["Avg"],
                         marker_color="#58a6ff", opacity=0.9,
                         text=spin_data["Avg"], textposition="outside", textfont_color="#8b949e")
        fig_spin.add_bar(name="Max", x=spin_data["Club"], y=spin_data["Max"],
                         marker_color="#79c0ff", opacity=0.4)
        fig_spin.update_layout(**get_plot_layout(), barmode="overlay", height=360,
                               yaxis_title="Spin Rate (RPM)", xaxis_title=None,
                               legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#8b949e"))
        fig_spin.update_xaxes(**get_axis_style())
        fig_spin.update_yaxes(**get_axis_style())
        st.plotly_chart(fig_spin, use_container_width=True)

        # Magnus force diagram via Plotly
        st.markdown("#### Magnus Effect Visualisation")
        theta = np.linspace(0, 2 * np.pi, 100)
        x_ball = np.cos(theta) * 0.5
        y_ball = np.sin(theta) * 0.5 + 2
        fig_mag = go.Figure()
        fig_mag.add_scatter(x=x_ball, y=y_ball, mode="lines",
                            line=dict(color="#58a6ff", width=2), name="Ball")
        fig_mag.add_scatter(x=[0], y=[2], mode="markers",
                            marker=dict(size=18, color="#1f6feb"), name="Ball center",
                            showlegend=False)
        # Spin arrows (top of ball faster, bottom slower)
        for y_a, label, color in [(2.55, "Fast air (top)", "#3fb950"), (1.45, "Slow air (bottom)", "#f78166")]:
            fig_mag.add_annotation(x=1.2, y=y_a, ax=-1.2, ay=y_a,
                                   arrowhead=2, arrowsize=1, arrowwidth=2,
                                   arrowcolor=color, text=label,
                                   font=dict(color=color, size=10))
        fig_mag.add_annotation(x=0, y=3.2, ax=0, ay=2.65,
                               arrowhead=2, arrowsize=1.5, arrowwidth=2,
                               arrowcolor="#e3b341", text="Lift (Magnus Force)",
                               font=dict(color="#e3b341", size=11))
        fig_mag.update_layout(
            **get_plot_layout(), height=300, showlegend=False,
        )
        fig_mag.update_layout(title="Backspin generates upward Magnus lift")
        fig_mag.update_layout(title_font=dict(color="#8b949e", size=12))
        st.plotly_chart(fig_mag, use_container_width=True)

    # ── TAB 4: Swing Mechanics ───────────────────────────────────
    with tabs[3]:
        st.markdown("### Swing Mechanics")

        show_card(
            "The Grip: Your Only Connection",
            "Beginner",
            "Grip pressure should be a <b>4-5 out of 10</b> -- firm enough to control the club, "
            "light enough to feel the clubhead. A strong grip (hands turned right) encourages a draw/hook. "
            "A weak grip (hands turned left) encourages a fade/slice. Neutral is two knuckles visible "
            "on the lead hand at address.",
            tip="Hold the club like you're holding a live bird -- firm enough it can't fly away, gentle enough you won't hurt it."
        )
        show_card(
            "The Kinematic Sequence",
            "Intermediate",
            "A proper downswing initiates from the <b>ground up</b>: hips rotate first, then torso, "
            "then arms, then club. This sequence creates a 'lag' -- the angle between lead arm and shaft -- "
            "which is released through impact for power. Amateurs often cast (release lag early) which "
            "wastes stored energy and causes over-the-top paths.",
            tip="Feel your hips clear before your hands drop. Imagine your right elbow (trail arm) tucking into your hip."
        )
        show_card(
            "Attack Angle & Low Point",
            "Intermediate",
            "The low point of the swing arc is critical. For irons, you want the low point <b>2-4 inches "
            "in front of the ball</b> (toward the target) to produce a descending blow and compress the ball. "
            "For driver, you want to strike <i>after</i> the low point on a slight upswing (+2 to +4 degrees) "
            "to maximise launch and minimise spin.",
            tip="Place a tee 3 inches in front of your iron ball. Try to clip it after impact -- that's your target low point."
        )
        show_card(
            "Ground Reaction Forces",
            "Advanced",
            "Elite golfers generate vertical ground reaction forces of <b>1.5-2x body weight</b> during "
            "the downswing. This 'pushing into the ground' through the lead foot creates rotational torque "
            "via Newton's third law. Force plate data shows pros peak their vertical GRF before their peak "
            "horizontal GRF, sequencing power from the ground up efficiently. Amateur golfers often 'fall back' "
            "and shift weight to the trail foot, losing this ground force advantage entirely.",
            tip="Feel like you're pushing the ground away from you with your lead foot through impact."
        )

        # Kinematic sequence timing chart
        st.markdown("#### Kinematic Sequence (Timing Reference)")
        ks_data = pd.DataFrame({
            "Segment":  ["Hips","Torso","Lead Arm","Club"],
            "Peak_Velocity_pct": [65, 75, 85, 100],
            "Order": [1, 2, 3, 4]
        })
        fig_ks = go.Figure(go.Bar(
            x=ks_data["Segment"], y=ks_data["Peak_Velocity_pct"],
            marker=dict(color=["#3fb950","#58a6ff","#e3b341","#f78166"]),
            text=[f"Peaks at {v}%" for v in ks_data["Peak_Velocity_pct"]],
            textposition="outside", textfont_color="#8b949e"
        ))
        fig_ks.update_layout(**get_plot_layout(), height=320, yaxis_title="% through downswing at peak velocity",
                             xaxis_title=None, yaxis_range=[0, 120])
        fig_ks.update_xaxes(**get_axis_style())
        fig_ks.update_yaxes(**get_axis_style())
        st.plotly_chart(fig_ks, use_container_width=True)
        st.caption("Each segment peaks and decelerates, transferring energy to the next. Hips slow as torso accelerates, etc.")

    # ── TAB 5: Club Selection ────────────────────────────────────
    with tabs[4]:
        st.markdown("### Club Selection & Distance Gapping")

        show_card(
            "Why Gapping Matters",
            "Beginner",
            "You should have roughly <b>10-15 yards between each club</b>. If two clubs go the same distance, "
            "one is redundant. Start by knowing your 7-iron carry -- that's your anchor. Work outward from there. "
            "Most amateurs carry too many fairway woods and not enough wedges where 80% of shots are lost.",
            tip="Know your carry distance for every club, not total (roll-out depends on conditions)."
        )
        show_card(
            "Lie Angle & Distance Adjustment",
            "Intermediate",
            "Conditions change your effective distance. A headwind of 10 mph reduces carry by roughly "
            "<b>1 club</b> (15 yds for a mid-iron). Uphill lies add loft; downhill lies remove it. "
            "Ball above feet = ball curves left; ball below feet = ball curves right. "
            "Elevation: +1000 ft altitude = ~3% more carry distance.",
            tip="In the wind, 'grip down and swing smooth' beats 'muscle a shorter club'. More control, less spin wobble."
        )
        show_card(
            "Optimal Loft Gapping & Wedge Setup",
            "Advanced",
            "Tour players typically carry 4 wedges with loft gaps of 4-6 degrees: PW (44-46), "
            "GW (50-52), SW (56), LW (60). Each wedge is tuned for full, 3/4, and half swings, "
            "giving 9-12 distinct distance options. Bounce angle matters: high bounce (10-14 deg) "
            "for soft conditions and bunkers; low bounce (4-8 deg) for firm turf and tight lies. "
            "Grind profiles control how the sole interacts with the turf at different face positions.",
            tip="Build your wedge setup around the courses you play. Firm links = low bounce. Parkland = high bounce."
        )

        # Reference distance chart
        st.markdown("#### Reference Carry Distances by Handicap")
        hcp_data = pd.DataFrame({
            "Club": ["Driver","3-Wood","5-Iron","7-Iron","9-Iron","PW"],
            "Scratch": [275, 240, 195, 175, 145, 135],
            "10hcp":   [230, 195, 165, 145, 120, 110],
            "20hcp":   [195, 165, 140, 120, 100, 90],
            "Beginner":[160, 135, 110, 95,  80,  70],
        })
        fig_hcp = go.Figure()
        colors = {"Scratch":"#3fb950","10hcp":"#58a6ff","20hcp":"#e3b341","Beginner":"#f78166"}
        for cat_col, color in colors.items():
            fig_hcp.add_scatter(x=hcp_data["Club"], y=hcp_data[cat_col],
                                mode="lines+markers", name=cat_col,
                                line=dict(color=color, width=2),
                                marker=dict(size=7, color=color))
        fig_hcp.update_layout(**get_plot_layout(), height=360, yaxis_title="Carry Distance (yards)",
                              xaxis_title=None, legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#8b949e"))
        fig_hcp.update_xaxes(**get_axis_style())
        fig_hcp.update_yaxes(**get_axis_style())
        st.plotly_chart(fig_hcp, use_container_width=True)

    # ── TAB 6: Practice Drills ───────────────────────────────────
    with tabs[5]:
        st.markdown("### Practice Drills & Training")

        show_card(
            "The Gate Drill (Putting)",
            "Beginner",
            "Place two tees just wider than your putter head, 6 inches in front of the ball on your "
            "intended line. Putt through the gate without touching either tee. This trains face angle "
            "at contact and path direction simultaneously. Do 20 reps from 6 feet before every round.",
            tip="If you consistently miss the gate on one side, your face is open/closed. Adjust your grip."
        )
        show_card(
            "Alignment Stick Swing Plane Drill",
            "Beginner",
            "Stick an alignment rod in the ground at a 45-degree angle outside the ball pointing at "
            "your trail hip. On the takeaway, the club should track along the rod's plane. "
            "If the club goes inside the rod on takeaway, you'll likely come over-the-top on the way down.",
            tip="Film yourself from face-on with the rod in frame. The club should mirror the rod angle on the way back."
        )
        show_card(
            "Impact Bag Training",
            "Intermediate",
            "Hit an impact bag (or old duffle bag full of towels) with slow-motion swings, "
            "focusing on shaft lean, flat lead wrist, and hip rotation at the moment of contact. "
            "The bag gives instant feedback -- if you're flipping, the bag won't compress properly. "
            "Do 50 slow hits before switching to full speed. Motor patterns form faster at slow speed.",
            tip="Record at 120fps (iPhone slo-mo). Pause at impact. Check: lead wrist flat, shaft leaning forward, hips open."
        )
        show_card(
            "Random Practice vs Blocked Practice",
            "Intermediate",
            "Blocked practice (hitting 50 7-irons in a row) builds confidence but transfers poorly to the course. "
            "Random practice (alternating clubs every shot, varying targets, playing 'virtual holes') "
            "is harder but builds true skill. Research shows random practice produces <b>40-50% better "
            "retention</b> after 48 hours vs blocked practice. Tour pros do 70% random, 30% blocked in season.",
            tip="On the range, play your local course hole by hole. Club, target, shot shape -- simulate real decisions."
        )
        show_card(
            "Pressure Training & Consequences",
            "Advanced",
            "The brain learns better under mild pressure. Set up consequence-based drills: "
            "make 5 puts in a row from 6 feet (restart on miss), or hit 3 consecutive fairways "
            "before leaving the range. Research by Dr. Debbie Crews shows pre-shot EEG patterns "
            "of successful putts show <b>right-brain dominance</b> (quiet analytical mind) -- "
            "the 'consequence' drills train this neural quiet under stress.",
            tip="The '5 in a row' putting drill is more valuable than 200 consecutive range balls. Do it last every session."
        )
        show_card(
            "TrackMan Combine & Benchmarking",
            "Advanced",
            "The TrackMan Combine test measures 60 shots across all clubs, scoring accuracy (proximity to target). "
            "Scratch = ~130 points, Tour average = 165+, amateur average = 60-80. "
            "Use it quarterly as a baseline. Key metrics to chase: Smash Factor (driver 1.48-1.50 is excellent), "
            "Spin Loft efficiency, and Low Point control (SD < 1 inch for irons).",
            tip="Don't chase carry distance on Trackman. Chase smash factor and low point consistency -- distance follows."
        )

# =============================================================
#  PAGE: LOG SESSION (Admin)
# =============================================================
elif page == "Log Session":
    st.markdown("# Log Practice Session")

    st.markdown("#### Shot Shape")
    st.caption("Tap a shape below, then fill in the rest and hit Save Shot.")

    shape_cols = st.columns(len(SHOT_SHAPES))
    for i, shape in enumerate(SHOT_SHAPES):
        with shape_cols[i]:
            btn_type = "primary" if st.session_state.shot_shape == shape else "secondary"
            if st.button(shape, key=f"shape_{shape}", use_container_width=True, type=btn_type):
                st.session_state.shot_shape = shape
                st.rerun()

    st.info(f"Selected shape: **{st.session_state.shot_shape}**")
    st.divider()

    with st.form("log_form", clear_on_submit=True):
        st.markdown("#### Session Details")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            f_date  = st.date_input("Date", value=datetime.date.today(), key="f_date")
            f_club  = st.selectbox("Club Used", CLUB_ORDER, key="f_club")
        with f_col2:
            f_total = st.number_input("Total Distance (yards)", min_value=0, max_value=450, step=1)
            f_carry = st.number_input("Carry Distance (yards)", min_value=0, max_value=450, step=1)

        f_notes = st.text_area("Notes (optional)", placeholder="E.g. Good hip rotation...", key="f_notes")
        st.markdown(f"**Shot Shape:** `{st.session_state.shot_shape}` -- change above before submitting")
        submitted = st.form_submit_button("Save Shot", use_container_width=True)

    if submitted:
        if f_carry > f_total:
            st.error("Carry distance cannot exceed total distance.")
        else:
            try:
                supabase.table("performance_logs").insert({
                    "session_date"  : str(f_date),
                    "club_used"     : f_club,
                    "total_distance": int(f_total),
                    "carry_distance": int(f_carry),
                    "shot_shape"    : st.session_state.shot_shape,
                    "notes"         : f_notes.strip() or None,
                }).execute()
                invalidate_cache()
                st.success(f"Shot logged: {f_club}, {f_total} yds, {st.session_state.shot_shape}")
                st.session_state.shot_shape = "Straight"
            except Exception as e:
                st.error(f"Error saving session: {e}")

    st.divider()
    st.markdown("#### Recent Sessions")
    df = fetch_performance_logs()
    if not df.empty:
        preview = df.head(10).copy()
        preview["session_date"] = preview["session_date"].dt.strftime("%d %b %Y")
        st.dataframe(
            preview[["session_date","club_used","total_distance","carry_distance","shot_shape","notes"]]
              .rename(columns={"session_date":"Date","club_used":"Club",
                               "total_distance":"Total (yds)","carry_distance":"Carry (yds)",
                               "shot_shape":"Shape","notes":"Notes"}),
            use_container_width=True, hide_index=True)
        if st.button("Delete Most Recent Entry"):
            supabase.table("performance_logs").delete().eq("id", int(df.iloc[0]["id"])).execute()
            invalidate_cache()
            st.success("Deleted most recent entry.")
            st.rerun()
    else:
        st.info("No shots logged yet.")

# =============================================================
#  PAGE: UPLOAD MEDIA (Admin)
# =============================================================
elif page == "Upload Media":
    st.markdown("# Upload Swing Media")
    st.caption("Accepted: MP4, MOV, WEBM (video) | JPG, PNG, WEBP (image) | GIF | Max ~200 MB")

    with st.form("upload_form", clear_on_submit=True):
        u_col1, u_col2 = st.columns(2)
        with u_col1:
            u_date  = st.date_input("Media Date", value=datetime.date.today(), key="u_date")
            u_cat   = st.selectbox("Club Category", CATEGORIES, key="u_cat")
            u_title = st.text_input("Title", placeholder="E.g. Driver warmup hole 1", key="u_title")
        with u_col2:
            u_notes = st.text_area("Notes / Description",
                                   placeholder="E.g. Slight pull, good hip rotation...",
                                   height=120, key="u_notes")

        u_file = st.file_uploader(
            "Choose file",
            type=["mp4","mov","webm","avi","jpg","jpeg","png","webp","gif"],
            key="u_file"
        )
        upload_btn = st.form_submit_button("Upload to Vault", use_container_width=True)

    if upload_btn:
        if u_file is None:
            st.error("Please select a file.")
        else:
            ext       = u_file.name.rsplit(".", 1)[-1].lower()
            mime_type = MIME_MAP.get(ext, "application/octet-stream")
            ts        = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            safe_name = f"{u_cat}/{ts}_{u_file.name.replace(' ','_')}"

            with st.spinner("Uploading to Supabase Storage..."):
                try:
                    supabase.storage.from_(BUCKET).upload(
                        path=safe_name, file=u_file.read(),
                        file_options={"content-type": mime_type})
                    pub_url = supabase.storage.from_(BUCKET).get_public_url(safe_name)
                    supabase.table("video_vault").insert({
                        "clip_date"   : str(u_date),
                        "category"    : u_cat,
                        "title"       : u_title.strip() or None,
                        "notes"       : u_notes.strip() or None,
                        "storage_path": safe_name,
                        "public_url"  : pub_url,
                    }).execute()
                    invalidate_cache()
                    st.success(f"Uploaded: {u_file.name}")
                    st.markdown(f"[View file]({pub_url})")
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    st.divider()
    st.markdown("#### Recent Uploads")
    vdf = fetch_video_vault()
    if not vdf.empty:
        preview = vdf.head(8).copy()
        preview["clip_date"] = preview["clip_date"].dt.strftime("%d %b %Y")
        st.dataframe(
            preview[["clip_date","category","title","notes","public_url"]]
              .rename(columns={"clip_date":"Date","category":"Category",
                               "title":"Title","notes":"Notes","public_url":"URL"}),
            use_container_width=True, hide_index=True,
            column_config={"URL": st.column_config.LinkColumn("URL")})
    else:
        st.info("No media uploaded yet.")
