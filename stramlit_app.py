from datetime import date
import sqlite3
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Fitness Tracker App", page_icon="💪", layout="centered"
)


# Initialize SQLite Database
def init_db():
  conn = sqlite3.connect("fitness_data.db")
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            exercise TEXT,
            duration INTEGER,
            calories INTEGER,
            steps INTEGER
        )
    """)
  conn.commit()
  conn.close()


init_db()

# App Title & Overview
st.title("💪 Fitness Tracker App")
st.write("Track your daily activities, workouts, steps, and calories burned!")
st.markdown("---")

# Navigation Sidebar
menu = st.sidebar.selectbox(
    "Navigation Menu", ["📊 Dashboard", "➕ Log Workout", "📋 View All History"]
)

# ----------------- 1. DASHBOARD SCREEN -----------------
if menu == "📊 Dashboard":
  st.subheader("📈 Your Fitness Dashboard")

  conn = sqlite3.connect("fitness_data.db")
  c = conn.cursor()
  c.execute(
      "SELECT SUM(steps), SUM(calories), SUM(duration) FROM workouts"
  )
  result = c.fetchone()
  conn.close()

  total_steps = result[0] if result[0] else 0
  total_calories = result[1] if result[1] else 0
  total_duration = result[2] if result[2] else 0

  # Metrics Row
  col1, col2, col3 = st.columns(3)
  col1.metric("Total Steps", f"{total_steps:,}")
  col2.metric("Calories Burned", f"{total_calories} kcal")
  col3.metric("Active Minutes", f"{total_duration} mins")

  st.markdown("---")

  # Visual Progress Bars against daily/weekly goals
  st.subheader("🎯 Goal Progress")

  step_goal = 10000
  calorie_goal = 500

  step_progress = min(total_steps / step_goal, 1.0)
  calorie_progress = min(total_calories / calorie_goal, 1.0)

  st.write(f"**Step Goal:** {total_steps} / {step_goal} steps")
  st.progress(step_progress)

  st.write(f"**Calorie Burn Goal:** {total_calories} / {calorie_goal} kcal")
  st.progress(calorie_progress)

# ----------------- 2. LOG WORKOUT SCREEN -----------------
elif menu == "➕ Log Workout":
  st.subheader("📝 Log Your Daily Activity & Workout")

  with st.form("workout_form"):
    log_date = st.date_input("Date", value=date.today())
    exercise_type = st.selectbox(
        "Exercise Type",
        [
            "Running",
            "Walking",
            "Cycling",
            "Weightlifting",
            "Yoga",
            "Swimming",
            "HIIT",
        ],
    )
    duration = st.number_input(
        "Duration (minutes)", min_value=1, max_value=600, value=30
    )
    calories = st.number_input(
        "Calories Burned (kcal)", min_value=0, max_value=5000, value=200
    )
    steps = st.number_input("Steps Taken", min_value=0, max_value=100000, value=0)

    submit_button = st.form_submit_button(label="Save Workout Record")

    if submit_button:
      conn = sqlite3.connect("fitness_data.db")
      c = conn.cursor()
      c.execute(
          """
                INSERT INTO workouts (date, exercise, duration, calories, steps)
                VALUES (?, ?, ?, ?, ?)
            """,
          (
              str(log_date),
              exercise_type,
              duration,
              calories,
              steps,
          ),
      )
      conn.commit()
      conn.close()
      st.success("🎉 Workout and fitness data logged successfully!")

# ----------------- 3. VIEW HISTORY SCREEN -----------------
elif menu == "📋 View All History":
  st.subheader("📜 Past Fitness Records")

  conn = sqlite3.connect("fitness_data.db")
  c = conn.cursor()
  c.execute(
      "SELECT id, date, exercise, duration, calories, steps FROM workouts"
      " ORDER BY date DESC"
  )
  rows = c.fetchall()
  conn.close()

  if rows:
    # Display as a clean table
    import pandas as pd

    df = pd.DataFrame(
        rows,
        columns=[
            "ID",
            "Date",
            "Exercise Type",
            "Duration (mins)",
            "Calories (kcal)",
            "Steps",
        ],
    )
    st.dataframe(df, use_container_width=True)

    # Option to clear records
    if st.button("Clear All History"):
      conn = sqlite3.connect("fitness_data.db")
      c = conn.cursor()
      c.execute("DELETE FROM workouts")
      conn.commit()
      conn.close()
      st.warning("All records deleted.")
      st.rerun()
  else:
    st.info(
        "No fitness records found yet. Use the 'Log Workout' tab to add some!"
    )
