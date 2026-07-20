import streamlit as st
import pandas as pd
import datetime
import json
import os
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StepFlow – Fitness Tracker",
    page_icon="👟",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&family=Space+Grotesk:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #0d0d0d;
    color: #f0f0f0;
}

.main { background-color: #0d0d0d; }

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif;
    font-weight: 700;
}

.hero {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    margin-bottom: 2rem;
    border: 1px solid #00f5d4;
    box-shadow: 0 0 40px rgba(0,245,212,0.08);
}

.hero h1 {
    font-size: 3rem;
    background: linear-gradient(90deg, #00f5d4, #9b5de5);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.2rem;
}

.hero p {
    color: #aaa;
    font-size: 1.05rem;
}

.metric-card {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 1.4rem 1.2rem;
    text-align: center;
    transition: border-color 0.3s;
}

.metric-card:hover { border-color: #00f5d4; }

.metric-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.2rem;
    font-weight: 700;
    color: #00f5d4;
}

.metric-label {
    font-size: 0.78rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.3rem;
}

.metric-icon { font-size: 1.8rem; margin-bottom: 0.4rem; }

.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #f0f0f0;
    border-left: 4px solid #00f5d4;
    padding-left: 0.8rem;
    margin: 1.8rem 0 1rem 0;
}

.log-entry {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.6rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.badge {
    background: linear-gradient(135deg, #00f5d4, #9b5de5);
    border-radius: 20px;
    padding: 0.2rem 0.8rem;
    font-size: 0.75rem;
    font-weight: 600;
    color: #0d0d0d;
}

.stButton > button {
    background: linear-gradient(135deg, #00f5d4, #9b5de5);
    color: #0d0d0d;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 0.6rem 1.8rem;
    font-size: 1rem;
    width: 100%;
    cursor: pointer;
    font-family: 'Inter', sans-serif;
}

.stButton > button:hover { opacity: 0.88; }

.stSlider > div > div > div { color: #00f5d4 !important; }

label, .stSelectbox label, .stSlider label, .stNumberInput label {
    color: #aaa !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

input[type="number"], .stSelectbox > div {
    background: #1e1e1e !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
    color: #f0f0f0 !important;
}

.stDateInput input {
    background: #1e1e1e !important;
    color: #f0f0f0 !important;
    border: 1px solid #333 !important;
    border-radius: 8px !important;
}

hr { border-color: #222; }

.tip-box {
    background: #111b2e;
    border: 1px solid #1a4a6b;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    color: #7dd3fc;
    font-size: 0.9rem;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ── Data storage helpers ──────────────────────────────────────────────────────
DATA_FILE = "stepflow_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ── Calculation helpers ───────────────────────────────────────────────────────
def steps_to_km(steps, stride_cm=75):
    return round((steps * stride_cm) / 100000, 2)

def calories_burned(steps, weight_kg, activity):
    met = {"Walking": 3.5, "Running": 7.0, "Jogging": 5.5}[activity]
    # approx: MET * weight * time_hours  (steps / cadence → hours)
    cadence = {"Walking": 100, "Running": 160, "Jogging": 130}[activity]
    hours = steps / cadence / 60
    return round(met * weight_kg * hours, 1)

def time_taken(steps, activity):
    cadence = {"Walking": 100, "Running": 160, "Jogging": 130}[activity]
    minutes = steps / cadence
    h = int(minutes // 60)
    m = int(minutes % 60)
    s = int((minutes * 60) % 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"

def get_tip(steps, calories):
    if steps < 3000:
        return "💡 You're just getting started! Even a 10-min walk adds ~1,200 steps."
    elif steps < 7000:
        return "💡 Good effort! Try to hit 8,000 steps — your heart will thank you."
    elif steps < 10000:
        return "💡 Almost there! 10,000 steps is today's goal — push a little more."
    else:
        return f"🏆 Amazing! You crushed 10,000 steps and burned {calories} kcal today!"

# ── Load session data ─────────────────────────────────────────────────────────
if "logs" not in st.session_state:
    st.session_state.logs = load_data()

# ── Hero header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>👟 StepFlow</h1>
    <p>Track every step, kilometre, minute & calorie — all in one place.</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar – Log activity ────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ➕ Log Activity")
    st.markdown("---")

    log_date = st.date_input("Date", value=datetime.date.today())
    activity = st.selectbox("Activity Type", ["Walking", "Jogging", "Running"])
    steps = st.number_input("Steps", min_value=0, max_value=100000, value=5000, step=100)
    weight = st.number_input("Your Weight (kg)", min_value=30, max_value=200, value=65, step=1)
    goal = st.slider("Daily Step Goal", 3000, 20000, 10000, 500)

    if st.button("💾 Save Activity"):
        km = steps_to_km(steps)
        cal = calories_burned(steps, weight, activity)
        duration = time_taken(steps, activity)

        entry = {
            "date": str(log_date),
            "activity": activity,
            "steps": steps,
            "km": km,
            "calories": cal,
            "duration": duration,
            "weight": weight,
            "goal": goal,
        }
        st.session_state.logs.append(entry)
        save_data(st.session_state.logs)
        st.success(f"✅ Logged {steps:,} steps for {log_date}!")

    st.markdown("---")
    if st.button("🗑️ Clear All Data"):
        st.session_state.logs = []
        save_data([])
        st.warning("All data cleared.")

# ── Main content ──────────────────────────────────────────────────────────────
logs = st.session_state.logs

if not logs:
    st.markdown("""
    <div style='text-align:center; padding: 4rem 0; color:#555;'>
        <div style='font-size:4rem;'>👟</div>
        <div style='font-size:1.3rem; margin-top:1rem;'>No activities yet.</div>
        <div style='font-size:0.9rem; margin-top:0.5rem;'>Use the sidebar to log your first workout!</div>
    </div>
    """, unsafe_allow_html=True)
else:
    df = pd.DataFrame(logs)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date", ascending=False)

    # ── Today's summary ───────────────────────────────────────────────────────
    today = datetime.date.today()
    today_df = df[df["date"].dt.date == today]

    total_steps_today = int(today_df["steps"].sum())
    total_km_today    = round(today_df["km"].sum(), 2)
    total_cal_today   = round(today_df["calories"].sum(), 1)
    daily_goal        = int(today_df["goal"].iloc[0]) if not today_df.empty else goal

    progress = min(total_steps_today / daily_goal, 1.0)

    st.markdown('<div class="section-title">Today\'s Summary</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col, icon, val, label in [
        (c1, "👣", f"{total_steps_today:,}", "Steps"),
        (c2, "📏", f"{total_km_today} km", "Distance"),
        (c3, "🔥", f"{total_cal_today} kcal", "Calories"),
        (c4, "⏱️", today_df["duration"].iloc[0] if not today_df.empty else "—", "Duration"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    # Goal progress bar
    st.markdown(f"""
    <div style='margin: 1.2rem 0 0.4rem; color:#aaa; font-size:0.8rem; text-transform:uppercase; letter-spacing:0.08em;'>
        Daily Goal Progress — {total_steps_today:,} / {daily_goal:,} steps
    </div>
    """, unsafe_allow_html=True)
    st.progress(progress)

    if not today_df.empty:
        tip = get_tip(total_steps_today, total_cal_today)
        st.markdown(f'<div class="tip-box">{tip}</div>', unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">7-Day Trends</div>', unsafe_allow_html=True)

    last7 = df[df["date"] >= pd.Timestamp(today - datetime.timedelta(days=6))]
    daily = last7.groupby("date").agg({"steps":"sum","km":"sum","calories":"sum"}).reset_index()

    col_left, col_right = st.columns(2)

    with col_left:
        fig1 = px.bar(
            daily, x="date", y="steps",
            title="Steps per Day",
            color_discrete_sequence=["#00f5d4"],
        )
        fig1.update_layout(
            plot_bgcolor="#161616", paper_bgcolor="#161616",
            font_color="#aaa", title_font_color="#f0f0f0",
            xaxis=dict(showgrid=False, tickfont=dict(color="#aaa")),
            yaxis=dict(showgrid=True, gridcolor="#222", tickfont=dict(color="#aaa")),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col_right:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=daily["date"], y=daily["calories"],
            mode="lines+markers",
            line=dict(color="#9b5de5", width=2.5),
            marker=dict(size=7, color="#9b5de5"),
            name="Calories",
        ))
        fig2.add_trace(go.Scatter(
            x=daily["date"], y=daily["km"],
            mode="lines+markers",
            line=dict(color="#f72585", width=2, dash="dot"),
            marker=dict(size=6, color="#f72585"),
            name="km",
            yaxis="y2",
        ))
        fig2.update_layout(
            title="Calories & Distance",
            plot_bgcolor="#161616", paper_bgcolor="#161616",
            font_color="#aaa", title_font_color="#f0f0f0",
            xaxis=dict(showgrid=False, tickfont=dict(color="#aaa")),
            yaxis=dict(showgrid=True, gridcolor="#222", tickfont=dict(color="#aaa"), title="Calories"),
            yaxis2=dict(overlaying="y", side="right", tickfont=dict(color="#f72585"), title="km"),
            legend=dict(bgcolor="#161616", bordercolor="#333", font=dict(color="#aaa")),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── All logs table ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Activity Log</div>', unsafe_allow_html=True)

    display_df = df[["date","activity","steps","km","calories","duration"]].copy()
    display_df["date"] = display_df["date"].dt.strftime("%d %b %Y")
    display_df.columns = ["Date","Activity","Steps","Distance (km)","Calories (kcal)","Duration"]
    display_df = display_df.reset_index(drop=True)

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    # ── All-time stats ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">All-Time Stats</div>', unsafe_allow_html=True)
    ca, cb, cc = st.columns(3)

    for col, icon, val, label in [
        (ca, "🏃", f"{int(df['steps'].sum()):,}", "Total Steps"),
        (cb, "🌍", f"{round(df['km'].sum(),1)} km", "Total Distance"),
        (cc, "🔥", f"{round(df['calories'].sum(),0):,} kcal", "Total Calories"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)