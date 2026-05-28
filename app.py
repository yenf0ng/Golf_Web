# ============================================================
#  Golf Swing Tracker & Analytics Dashboard
#  app.py  —  Streamlit + Supabase
# ============================================================

import io
import os
import datetime
import hashlib

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from supabase import create_client, Client

# ── Page config (must be first Streamlit call) ───────────────
st.set_page_config(
    page_title="⛳ Swing Tracker",
    page_icon="⛳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Fonts ── */
  @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* ── Global background ── */
  .stApp {
    background: #0d1117;
    color: #e6edf3;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #21262d;
  }
  section[data-testid="stSidebar"] * {
    color: #e6edf3 !important;
  }

  /* ── Headings with Bebas ── */
  h1, h2, h3 {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 2px;
    color: #58a6ff !important;
  }
  h1 { font-size: 2.6rem !important; }
  h2 { font-size: 1.9rem !important; }
  h3 { font-size: 1.4rem !important; }

  /* ── Cards ── */
  .card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
  }
  .metric-card {
    background: linear-gradient(135deg, #161b22, #1c2333);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    text-align: center;
  }
  .metric-card .label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #8b949e;
    margin-bottom: 0.25rem;
  }
  .metric-card .value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.2rem;
    color: #58a6ff;
    line-height: 1;
  }
  .metric-card .sub {
    font-size: 0.75rem;
    color: #8b949e;
    margin-top: 0.2rem;
  }

  /* ── Category pill badges ── */
  .badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
  }
  .badge-Driver  { background:#1f6feb; color:#fff; }
  .badge-Irons   { background:#388bfd22; color:#58a6ff; border:1px solid #388bfd55; }
  .badge-Woods   { background:#2ea04322; color:#3fb950; border:1px solid #2ea04355; }
  .badge-Putting { background:#d2992222; color:#e3b341; border:1px solid #d2992255; }

  /* ── Shot shape toggle buttons ── */
  .shot-grid { display:flex; flex-wrap:wrap; gap:8px; margin:0.6rem 0 1rem; }
  .shot-btn {
    padding: 8px 18px;
    border-radius: 8px;
    border: 1.5px solid #30363d;
    background: #161b22;
    color: #8b949e;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all .15s ease;
    user-select: none;
  }
  .shot-btn:hover { border-color:#58a6ff; color:#58a6ff; }
  .shot-btn.active {
    background: #1f6feb;
    border-color: #58a6ff;
    color: #fff;
  }

  /* ── Video grid ── */
  .video-wrapper {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    overflow: hidden;
    margin-bottom: 1rem;
  }
  .video-meta {
    padding: 0.6rem 0.8rem;
    font-size: 0.8rem;
    color: #8b949e;
  }
  .video-meta strong { color: #e6edf3; }

  /* ── Tabs ── */
  .stTabs [role="tab"] {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.05rem;
    letter-spacing: 1.5px;
    color: #8b949e !important;
  }
  .stTabs [aria-selected="true"] {
    color: #58a6ff !important;
    border-bottom: 2px solid #58a6ff !important;
  }

  /* ── Inputs & selects ── */
  .stTextInput input, .stSelectbox select, .stNumberInput input,
  .stDateInput input, .stTextArea textarea {
    background: #0d1117 !important;
    border: 1px solid #30363d !important;
    color: #e6edf3 !important;
    border-radius: 8px !important;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: linear-gradient(135deg, #1f6feb, #388bfd);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    padding: 0.55rem 1.4rem;
    transition: opacity .15s;
  }
  .stButton > button:hover { opacity: .85; }

  /* ── Success / error messages ── */
  .stAlert { border-radius: 8px; }

  /* ── Divider ── */
  hr { border-color: #21262d; }

  /* ── Plotly charts — force dark ── */
  .js-plotly-plot .plotly { border-radius: 12px; }

  /* ── Mobile tweaks ── */
  @media (max-width: 640px) {
    h1 { font-size: 2rem !important; }
    .metric-card .value { font-size: 1.7rem; }
  }
</style>
""", unsafe_allow_html=True)

# ── Supabase client ──────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase()
BUCKET    = st.secrets.get("STORAGE_BUCKET", "swing-clips")

# ── Helper: hash admin password ──────────────────────────────
def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# ── Session state defaults ───────────────────────────────────
if "is_admin"    not in st.session_state: st.session_state.is_admin = False
if "shot_shape"  not in st.session_state: st.session_state.shot_shape = "Straight"
if "auth_error"  not in st.session_state: st.session_state.auth_error = False

# ── Plotly shared theme ──────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor="#161b22",
    plot_bgcolor ="#161b22",
    font_color   ="#e6edf3",
    font_family  ="DM Sans",
    colorway     =["#58a6ff","#3fb950","#e3b341","#f78166","#bc8cff","#79c0ff","#56d364"],
    margin       =dict(l=16, r=16, t=40, b=16),
    xaxis=dict(gridcolor="#21262d", zerolinecolor="#30363d"),
    yaxis=dict(gridcolor="#21262d", zerolinecolor="#30363d"),
)

# ============================================================
#  SIDEBAR — Auth + navigation
# ============================================================
with st.sidebar:
    st.markdown("## ⛳ Swing Tracker")
    st.caption("Personal Golf Analytics")
    st.divider()

    if not st.session_state.is_admin:
        st.markdown("**Admin Login**")
        pw_input = st.text_input("Password", type="password", key="pw_field",
                                 placeholder="Enter admin password…")
        if st.button("Unlock Admin", use_container_width=True):
            correct = st.secrets.get("ADMIN_PASSWORD", "")
            if pw_input == correct:
                st.session_state.is_admin  = True
                st.session_state.auth_error = False
                st.rerun()
            else:
                st.session_state.auth_error = True

        if st.session_state.auth_error:
            st.error("Incorrect password.")
        st.caption("👁️ Viewing in **read-only** mode")
    else:
        st.success("🔓 Admin Mode Active")
        if st.button("Lock & Sign Out", use_container_width=True):
            st.session_state.is_admin = False
            st.rerun()

    st.divider()
    st.markdown("**Navigate**")
    page = st.radio("", ["📊 Dashboard", "🎥 Video Vault",
                          "📝 Log Session", "📤 Upload Clip"],
                    label_visibility="collapsed")

    # Restrict admin-only pages
    if page in ["📝 Log Session", "📤 Upload Clip"] and not st.session_state.is_admin:
        st.warning("Admin access required.")
        page = "📊 Dashboard"

    st.divider()
    st.caption("Built with Streamlit + Supabase")

# ============================================================
#  DATA HELPERS
# ============================================================
@st.cache_data(ttl=60)
def fetch_performance_logs() -> pd.DataFrame:
    res = supabase.table("performance_logs") \
                  .select("*") \
                  .order("session_date", desc=True) \
                  .execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df["session_date"] = pd.to_datetime(df["session_date"])
        return df
    return pd.DataFrame(columns=[
        "id","created_at","session_date","club_used",
        "total_distance","carry_distance","shot_shape","notes"
    ])

@st.cache_data(ttl=60)
def fetch_video_vault() -> pd.DataFrame:
    res = supabase.table("video_vault") \
                  .select("*") \
                  .order("clip_date", desc=True) \
                  .execute()
    if res.data:
        df = pd.DataFrame(res.data)
        df["clip_date"] = pd.to_datetime(df["clip_date"])
        return df
    return pd.DataFrame(columns=[
        "id","created_at","clip_date","category","notes","storage_path","public_url"
    ])

def invalidate_cache():
    fetch_performance_logs.clear()
    fetch_video_vault.clear()

# ── Club ordering for charts ─────────────────────────────────
CLUB_ORDER = [
    "Driver","3-Wood","5-Wood","Hybrid",
    "3-Iron","4-Iron","5-Iron","6-Iron",
    "7-Iron","8-Iron","9-Iron",
    "PW","GW","SW","LW","Putter"
]
SHOT_SHAPES   = ["Straight","Draw","Fade","Push","Pull","Slice","Hook"]
CATEGORIES    = ["Driver","Irons","Woods","Putting"]
CLUBS_ALL     = CLUB_ORDER

# ============================================================
#  PAGE: DASHBOARD
# ============================================================
if page == "📊 Dashboard":
    st.markdown("# 📊 Analytics Dashboard")
    df = fetch_performance_logs()

    if df.empty:
        st.info("No performance data yet. Log some sessions to see your analytics here.")
        st.stop()

    # ── Top KPI metrics ──────────────────────────────────────
    total_shots   = len(df)
    avg_dist      = df["total_distance"].mean()
    best_dist     = df["total_distance"].max()
    sessions      = df["session_date"].dt.date.nunique()

    c1, c2, c3, c4 = st.columns(4)
    for col, label, val, sub in [
        (c1, "Total Shots", f"{total_shots:,}", "logged"),
        (c2, "Avg Distance", f"{avg_dist:.0f}", "yards"),
        (c3, "Best Shot",    f"{best_dist:,}",  "yards"),
        (c4, "Sessions",     f"{sessions}",     "days out"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
          <div class="label">{label}</div>
          <div class="value">{val}</div>
          <div class="sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    # ── Chart 1: Club Distance (Avg vs Max) ──────────────────
    st.markdown("### Club Distance Overview")
    grp = df.groupby("club_used")["total_distance"].agg(
        Avg="mean", Max="max"
    ).reset_index()
    grp = grp[grp["club_used"].isin(CLUB_ORDER)]
    grp["club_used"] = pd.Categorical(grp["club_used"], categories=CLUB_ORDER, ordered=True)
    grp = grp.sort_values("club_used")

    fig1 = go.Figure()
    fig1.add_bar(name="Avg Distance",
                 x=grp["club_used"], y=grp["Avg"],
                 marker_color="#388bfd", opacity=0.85,
                 text=grp["Avg"].round(0).astype(int),
                 textposition="outside", textfont_color="#8b949e")
    fig1.add_bar(name="Max Distance",
                 x=grp["club_used"], y=grp["Max"],
                 marker_color="#3fb950", opacity=0.55,
                 text=grp["Max"],
                 textposition="outside", textfont_color="#8b949e")
    fig1.update_layout(
        **PLOT_LAYOUT, barmode="group",
        legend=dict(bgcolor="#00000000", font_color="#8b949e"),
        yaxis_title="Yards", xaxis_title=None,
        height=380,
    )
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()

    # ── Chart 2: Shot Dispersion (Driver vs Irons) ───────────
    st.markdown("### Shot Shape Dispersion")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        disp_clubs = st.multiselect(
            "Filter Clubs",
            options=sorted(df["club_used"].unique()),
            default=sorted(df["club_used"].unique())[:4],
            key="disp_clubs"
        )

    disp_df = df[df["club_used"].isin(disp_clubs)] if disp_clubs else df
    shape_grp = disp_df.groupby(["club_used","shot_shape"]).size().reset_index(name="count")
    shape_grp["shot_shape"] = pd.Categorical(shape_grp["shot_shape"], categories=SHOT_SHAPES, ordered=True)
    shape_grp = shape_grp.sort_values("shot_shape")

    fig2 = px.bar(
        shape_grp, x="shot_shape", y="count",
        color="club_used", barmode="group",
        labels={"shot_shape":"Shot Shape","count":"# of Shots","club_used":"Club"},
    )
    fig2.update_layout(**PLOT_LAYOUT, height=380,
                       legend=dict(bgcolor="#00000000", font_color="#8b949e"),
                       xaxis_title=None, yaxis_title="Shots")
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # ── Chart 3: Consistency Score (Std Dev) ─────────────────
    st.markdown("### Consistency Score  *(lower = more consistent)*")

    cons = df.groupby("club_used")["total_distance"].agg(
        SD="std", Count="count"
    ).dropna().reset_index()
    cons = cons[cons["Count"] >= 2]           # need at least 2 shots
    cons = cons[cons["club_used"].isin(CLUB_ORDER)]
    cons["club_used"] = pd.Categorical(cons["club_used"], categories=CLUB_ORDER, ordered=True)
    cons = cons.sort_values("club_used")
    cons["color"] = cons["SD"].apply(
        lambda v: "#3fb950" if v < 10 else ("#e3b341" if v < 20 else "#f78166")
    )

    fig3 = go.Figure(go.Bar(
        x=cons["club_used"], y=cons["SD"].round(1),
        marker_color=cons["color"],
        text=cons["SD"].round(1),
        textposition="outside", textfont_color="#8b949e",
    ))
    fig3.update_layout(
        **PLOT_LAYOUT, height=340,
        yaxis_title="Std Dev (yards)", xaxis_title=None,
        annotations=[dict(
            text="🟢 < 10 yds   🟡 10-20 yds   🔴 > 20 yds",
            xref="paper", yref="paper", x=1, y=1.06,
            showarrow=False, font_color="#8b949e", font_size=11,
            xanchor="right"
        )]
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── Chart 4: Distance trend over time ────────────────────
    st.markdown("### Distance Trend")
    trend_club = st.selectbox("Club", options=sorted(df["club_used"].unique()), key="trend_club")
    trend_df   = df[df["club_used"] == trend_club].sort_values("session_date")

    fig4 = go.Figure()
    fig4.add_scatter(
        x=trend_df["session_date"], y=trend_df["total_distance"],
        mode="lines+markers",
        line=dict(color="#58a6ff", width=2),
        marker=dict(size=7, color="#79c0ff"),
        name="Total Dist"
    )
    fig4.add_scatter(
        x=trend_df["session_date"], y=trend_df["carry_distance"],
        mode="lines+markers",
        line=dict(color="#3fb950", width=2, dash="dot"),
        marker=dict(size=6, color="#56d364"),
        name="Carry"
    )
    fig4.update_layout(
        **PLOT_LAYOUT, height=320,
        yaxis_title="Yards", xaxis_title=None,
        legend=dict(bgcolor="#00000000", font_color="#8b949e"),
    )
    st.plotly_chart(fig4, use_container_width=True)

    # ── Raw data expander ────────────────────────────────────
    with st.expander("🔍 Raw Session Data"):
        st.dataframe(
            df.sort_values("session_date", ascending=False)
              .drop(columns=["id","created_at"], errors="ignore")
              .rename(columns={
                  "session_date":"Date","club_used":"Club",
                  "total_distance":"Total (yds)","carry_distance":"Carry (yds)",
                  "shot_shape":"Shape","notes":"Notes"
              }),
            use_container_width=True, hide_index=True
        )

# ============================================================
#  PAGE: VIDEO VAULT
# ============================================================
elif page == "🎥 Video Vault":
    st.markdown("# 🎥 Video Vault")
    vdf = fetch_video_vault()

    # Filter bar
    col_f1, col_f2 = st.columns([3, 1])
    with col_f1:
        cat_filter = st.multiselect(
            "Filter by Category",
            options=CATEGORIES,
            default=CATEGORIES,
            key="cat_filter"
        )
    with col_f2:
        sort_order = st.selectbox("Sort", ["Newest First","Oldest First"], key="vsort")

    if vdf.empty:
        st.info("No swing clips uploaded yet. Admins can upload via the 📤 Upload Clip page.")
        st.stop()

    fdf = vdf[vdf["category"].isin(cat_filter)] if cat_filter else vdf
    if sort_order == "Oldest First":
        fdf = fdf.sort_values("clip_date")

    if fdf.empty:
        st.warning("No clips match the selected filters.")
        st.stop()

    # 2-column responsive grid
    cols_per_row = 2
    rows = [fdf.iloc[i:i+cols_per_row] for i in range(0, len(fdf), cols_per_row)]

    for row in rows:
        cols = st.columns(cols_per_row)
        for col, (_, clip) in zip(cols, row.iterrows()):
            badge_cls = f"badge-{clip['category']}"
            date_str  = clip["clip_date"].strftime("%d %b %Y") if pd.notna(clip["clip_date"]) else "—"
            notes_str = clip["notes"] or "No notes"

            with col:
                st.markdown(f"""
                <div class="video-wrapper">
                  <div style="padding:0.6rem 0.8rem 0;">
                    <span class="badge {badge_cls}">{clip['category']}</span>
                  </div>
                """, unsafe_allow_html=True)

                try:
                    st.video(clip["public_url"])
                except Exception:
                    st.markdown(
                        f'<a href="{clip["public_url"]}" target="_blank">▶ Open clip</a>',
                        unsafe_allow_html=True
                    )

                st.markdown(f"""
                  <div class="video-meta">
                    <strong>{date_str}</strong><br>{notes_str}
                  </div>
                </div>""", unsafe_allow_html=True)

    if st.session_state.is_admin:
        st.divider()
        st.markdown("#### 🗑️ Delete a Clip (Admin)")
        del_opts = {f"{r['clip_date'].date()} — {r['category']} (id:{r['id']})": r
                    for _, r in fdf.iterrows()}
        del_label = st.selectbox("Select clip to delete", list(del_opts.keys()), key="del_clip")
        if st.button("Delete Selected Clip", type="primary"):
            clip_row = del_opts[del_label]
            try:
                supabase.storage.from_(BUCKET).remove([clip_row["storage_path"]])
            except Exception:
                pass  # storage object may already be gone
            supabase.table("video_vault").delete().eq("id", clip_row["id"]).execute()
            invalidate_cache()
            st.success("Clip deleted.")
            st.rerun()

# ============================================================
#  PAGE: LOG SESSION (Admin)
# ============================================================
elif page == "📝 Log Session":
    st.markdown("# 📝 Log Practice Session")

    with st.form("log_form", clear_on_submit=True):
        st.markdown("#### Session Details")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            f_date  = st.date_input("Date", value=datetime.date.today(), key="f_date")
            f_club  = st.selectbox("Club Used", CLUBS_ALL, key="f_club")
        with f_col2:
            f_total = st.number_input("Total Distance (yards)", min_value=0, max_value=450,
                                      step=1, key="f_total")
            f_carry = st.number_input("Carry Distance (yards)", min_value=0, max_value=450,
                                      step=1, key="f_carry")

        st.markdown("#### Shot Shape")
        st.caption("Select the shape that best describes this shot.")

        # Shot shape selector using radio as styled toggle
        shape_cols = st.columns(len(SHOT_SHAPES))
        shape_icons = {"Straight":"→","Draw":"↙","Fade":"↗","Push":"⇒","Pull":"⇐","Slice":"↪","Hook":"↩"}
        for i, shape in enumerate(SHOT_SHAPES):
            with shape_cols[i]:
                if st.button(
                    f"{shape_icons[shape]}\n{shape}",
                    key=f"shape_{shape}",
                    use_container_width=True,
                    type="primary" if st.session_state.shot_shape == shape else "secondary"
                ):
                    st.session_state.shot_shape = shape
                    st.rerun()

        st.info(f"✅ Selected: **{st.session_state.shot_shape}**")

        f_notes = st.text_area("Notes (optional)", placeholder="E.g. 'Felt great hip rotation, slight early extension…'", key="f_notes")

        submitted = st.form_submit_button("💾 Save Shot", use_container_width=True)

    if submitted:
        if f_carry > f_total:
            st.error("Carry distance can't exceed total distance.")
        else:
            try:
                supabase.table("performance_logs").insert({
                    "session_date"   : str(f_date),
                    "club_used"      : f_club,
                    "total_distance" : int(f_total),
                    "carry_distance" : int(f_carry),
                    "shot_shape"     : st.session_state.shot_shape,
                    "notes"          : f_notes.strip() or None,
                }).execute()
                invalidate_cache()
                st.success(f"✅ Shot logged — {f_club}, {f_total} yds, {st.session_state.shot_shape}")
                st.session_state.shot_shape = "Straight"
            except Exception as e:
                st.error(f"Error saving session: {e}")

    # Recent sessions preview
    st.divider()
    st.markdown("#### Recent Sessions")
    df = fetch_performance_logs()
    if not df.empty:
        preview = df.head(10).copy()
        preview["session_date"] = preview["session_date"].dt.strftime("%d %b %Y")
        st.dataframe(
            preview[["session_date","club_used","total_distance","carry_distance","shot_shape","notes"]]
              .rename(columns={
                  "session_date":"Date","club_used":"Club",
                  "total_distance":"Total (yds)","carry_distance":"Carry (yds)",
                  "shot_shape":"Shape","notes":"Notes"
              }),
            use_container_width=True, hide_index=True
        )

        # Delete last entry shortcut
        if st.button("🗑️ Delete Most Recent Entry"):
            last_id = df.iloc[0]["id"]
            supabase.table("performance_logs").delete().eq("id", last_id).execute()
            invalidate_cache()
            st.success("Deleted most recent entry.")
            st.rerun()
    else:
        st.info("No shots logged yet.")

# ============================================================
#  PAGE: UPLOAD CLIP (Admin)
# ============================================================
elif page == "📤 Upload Clip":
    st.markdown("# 📤 Upload Swing Clip")
    st.caption("Accepted formats: MP4, MOV — max ~200 MB (Streamlit free tier limit)")

    with st.form("upload_form", clear_on_submit=True):
        u_col1, u_col2 = st.columns(2)
        with u_col1:
            u_date = st.date_input("Clip Date", value=datetime.date.today(), key="u_date")
            u_cat  = st.selectbox("Club Category", CATEGORIES, key="u_cat")
        with u_col2:
            u_notes = st.text_area("Notes (optional)",
                                   placeholder="E.g. 'Driver on hole 3, slight pull…'",
                                   key="u_notes")

        u_file = st.file_uploader("Choose video file", type=["mp4","mov"], key="u_file")
        upload_btn = st.form_submit_button("📤 Upload to Vault", use_container_width=True)

    if upload_btn:
        if u_file is None:
            st.error("Please select a video file.")
        else:
            ext       = u_file.name.rsplit(".", 1)[-1].lower()
            ts        = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            safe_name = f"{u_cat}/{ts}_{u_file.name.replace(' ','_')}"
            mime_type = "video/mp4" if ext == "mp4" else "video/quicktime"

            with st.spinner("Uploading to Supabase Storage…"):
                try:
                    file_bytes = u_file.read()
                    supabase.storage.from_(BUCKET).upload(
                        path        = safe_name,
                        file        = file_bytes,
                        file_options= {"content-type": mime_type},
                    )
                    pub_url = supabase.storage.from_(BUCKET).get_public_url(safe_name)
                    supabase.table("video_vault").insert({
                        "clip_date"    : str(u_date),
                        "category"     : u_cat,
                        "notes"        : u_notes.strip() or None,
                        "storage_path" : safe_name,
                        "public_url"   : pub_url,
                    }).execute()
                    invalidate_cache()
                    st.success(f"✅ Clip uploaded: **{u_file.name}**")
                    st.markdown(f"[▶ View clip]({pub_url})", unsafe_allow_html=False)
                except Exception as e:
                    st.error(f"Upload failed: {e}")

    # Recent uploads list
    st.divider()
    st.markdown("#### Recent Uploads")
    vdf = fetch_video_vault()
    if not vdf.empty:
        preview = vdf.head(8).copy()
        preview["clip_date"] = preview["clip_date"].dt.strftime("%d %b %Y")
        st.dataframe(
            preview[["clip_date","category","notes","public_url"]]
              .rename(columns={
                  "clip_date":"Date","category":"Category",
                  "notes":"Notes","public_url":"URL"
              }),
            use_container_width=True, hide_index=True,
            column_config={"URL": st.column_config.LinkColumn("URL")}
        )
    else:
        st.info("No clips uploaded yet.")
