import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StepTrack - Steps Tracker",
    page_icon="👟",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    /* Main Background */
    .stApp {
        background-color: #f5f7fb;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    /* Main Title */
    .main-title {
        font-size: 42px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #6b7280;
        margin-bottom: 30px;
    }

    /* Metric Cards */
    .metric-card {
        background-color: white;
        padding: 22px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        border: 1px solid #e5e7eb;
        min-height: 140px;
    }

    .metric-icon {
        font-size: 28px;
    }

    .metric-title {
        color: #6b7280;
        font-size: 15px;
        margin-top: 8px;
    }

    .metric-value {
        font-size: 30px;
        font-weight: 700;
        color: #111827;
    }

    /* Section Cards */
    .section-card {
        background-color: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e5e7eb;
        margin-bottom: 20px;
    }

    /* Goal Box */
    .goal-box {
        background-color: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border: 1px solid #e5e7eb;
    }

    .goal-title {
        font-size: 20px;
        font-weight: 600;
        color: #111827;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #6b7280;
        padding: 30px;
        font-size: 14px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE INITIALIZATION
# ============================================================

if "activity_history" not in st.session_state:
    st.session_state.activity_history = pd.DataFrame(
        columns=[
            "Date",
            "Activity",
            "Steps",
            "Distance (km)",
            "Duration (min)",
            "Calories"
        ]
    )


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def calculate_distance(steps, height):
    """
    Estimate distance using stride length.

    Average stride length is approximately:
    Height × 0.415 for males
    Height × 0.413 for females
    """

    stride_length = height * 0.415
    distance_km = (steps * stride_length) / 100000

    return round(distance_km, 2)


def calculate_calories(weight, distance, activity):
    """
    Estimate calories burned.

    Approximate MET values:
    Walking = 3.5
    Running = 8.0
    """

    if activity == "Walking":
        met = 3.5
    else:
        met = 8.0

    # Approximate calories burned
    calories = met * weight * (distance / 5)

    return round(calories, 2)


def format_duration(minutes):
    """
    Convert minutes into hours and minutes.
    """

    hours = minutes // 60
    remaining_minutes = minutes % 60

    if hours > 0:
        return f"{hours} hr {remaining_minutes} min"

    return f"{remaining_minutes} min"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("# 👟 StepTrack")

    st.markdown(
        "### Your personal activity dashboard"
    )

    st.divider()

    st.markdown("### 👤 User Profile")

    user_name = st.text_input(
        "Your Name",
        value="Fitness Enthusiast"
    )

    height = st.number_input(
        "Height (cm)",
        min_value=100,
        max_value=250,
        value=170,
        step=1
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=30.0,
        max_value=250.0,
        value=70.0,
        step=0.5
    )

    st.divider()

    st.markdown("### 🎯 Daily Goal")

    daily_goal = st.number_input(
        "Target Steps",
        min_value=1000,
        max_value=100000,
        value=10000,
        step=500
    )

    st.divider()

    st.info(
        "💡 Tip: Regular walking and running can improve your fitness and overall health."
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">👟 StepTrack</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="subtitle">Welcome back, {user_name}! Track your daily movement and reach your goals.</div>',
    unsafe_allow_html=True
)


# ============================================================
# ADD ACTIVITY SECTION
# ============================================================

st.markdown("## ➕ Add Activity")

with st.container(border=True):

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        activity_date = st.date_input(
            "📅 Date",
            value=date.today()
        )

    with col2:

        activity_type = st.selectbox(
            "🏃 Activity Type",
            ["Walking", "Running"]
        )

    with col3:

        steps = st.number_input(
            "👣 Number of Steps",
            min_value=0,
            max_value=100000,
            value=5000,
            step=100
        )

    with col4:

        duration = st.number_input(
            "⏱️ Duration (minutes)",
            min_value=1,
            max_value=1440,
            value=30,
            step=5
        )

    add_activity = st.button(
        "➕ Add Activity",
        use_container_width=True,
        type="primary"
    )

    if add_activity:

        if steps <= 0:

            st.error("Please enter a valid number of steps.")

        else:

            distance = calculate_distance(
                steps,
                height
            )

            calories = calculate_calories(
                weight,
                distance,
                activity_type
            )

            new_activity = pd.DataFrame(
                {
                    "Date": [activity_date],
                    "Activity": [activity_type],
                    "Steps": [steps],
                    "Distance (km)": [distance],
                    "Duration (min)": [duration],
                    "Calories": [calories]
                }
            )

            st.session_state.activity_history = pd.concat(
                [
                    st.session_state.activity_history,
                    new_activity
                ],
                ignore_index=True
            )

            st.success(
                "✅ Activity successfully added!"
            )


# ============================================================
# CALCULATE TODAY'S STATISTICS
# ============================================================

history = st.session_state.activity_history

today = date.today()

if not history.empty:

    today_data = history[
        history["Date"] == today
    ]

    total_steps = int(
        today_data["Steps"].sum()
    )

    total_distance = round(
        today_data["Distance (km)"].sum(),
        2
    )

    total_duration = int(
        today_data["Duration (min)"].sum()
    )

    total_calories = round(
        today_data["Calories"].sum(),
        2
    )

else:

    total_steps = 0
    total_distance = 0
    total_duration = 0
    total_calories = 0


# ============================================================
# TODAY'S DASHBOARD
# ============================================================

st.markdown("## 📊 Today's Overview")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">👣</div>
            <div class="metric-title">Steps</div>
            <div class="metric-value">{total_steps:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">📏</div>
            <div class="metric-title">Distance</div>
            <div class="metric-value">{total_distance} km</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">⏱️</div>
            <div class="metric-title">Active Time</div>
            <div class="metric-value">{format_duration(total_duration)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-icon">🔥</div>
            <div class="metric-title">Calories Burned</div>
            <div class="metric-value">{total_calories} kcal</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# DAILY GOAL PROGRESS
# ============================================================

st.markdown("## 🎯 Daily Goal")

progress = min(
    total_steps / daily_goal,
    1.0
)

percentage = min(
    int((total_steps / daily_goal) * 100),
    100
)

st.progress(
    progress
)

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        f"### {total_steps:,} / {daily_goal:,} steps"
    )

with col2:

    st.markdown(
        f"### {percentage}% completed"
    )

if total_steps >= daily_goal:

    st.success(
        "🎉 Congratulations! You have reached your daily step goal!"
    )

else:

    remaining_steps = daily_goal - total_steps

    st.info(
        f"💪 Only {remaining_steps:,} more steps to reach your goal!"
    )


# ============================================================
# ANALYTICS SECTION
# ============================================================

if not history.empty:

    st.markdown("## 📈 Activity Analytics")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### 👣 Steps by Activity Date")

        chart_data = (
            history
            .groupby("Date")["Steps"]
            .sum()
            .reset_index()
        )

        chart_data["Date"] = pd.to_datetime(
            chart_data["Date"]
        )

        chart_data = chart_data.set_index(
            "Date"
        )

        st.line_chart(
            chart_data
        )

    with col2:

        st.markdown("### 🔥 Calories Burned")

        calories_data = (
            history
            .groupby("Date")["Calories"]
            .sum()
            .reset_index()
        )

        calories_data["Date"] = pd.to_datetime(
            calories_data["Date"]
        )

        calories_data = calories_data.set_index(
            "Date"
        )

        st.bar_chart(
            calories_data
        )


# ============================================================
# ACTIVITY HISTORY
# ============================================================

st.markdown("## 📋 Activity History")

if not history.empty:

    display_history = history.copy()

    display_history["Date"] = display_history[
        "Date"
    ].astype(str)

    display_history["Duration"] = display_history[
        "Duration (min)"
    ].apply(format_duration)

    display_history = display_history[
        [
            "Date",
            "Activity",
            "Steps",
            "Distance (km)",
            "Duration",
            "Calories"
        ]
    ]

    st.dataframe(
        display_history,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        label="⬇️ Download Activity History",
        data=history.to_csv(index=False),
        file_name="steps_activity_history.csv",
        mime="text/csv"
    )

else:

    st.info(
        "No activity recorded yet. Add your first activity above! 🚶"
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        👟 StepTrack | Personal Activity Tracking Dashboard
        <br>
        Stay Active • Stay Healthy • Keep Moving
    </div>
    """,
    unsafe_allow_html=True
)
