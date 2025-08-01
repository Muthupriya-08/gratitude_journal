import streamlit as st
import pandas as pd
from datetime import datetime
import random
import os
import plotly.express as px

# Set page config
st.set_page_config(page_title="Gratitude Journal", layout="centered")

# Daily quotes
quotes = [
    "Gratitude turns what we have into enough.",
    "Start each day with a grateful heart.",
    "Gratitude is the fairest blossom which springs from the soul.",
    "Acknowledging the good that you already have in your life is the foundation for all abundance.",
    "Happiness is not what makes us grateful. It is gratefulness that makes us happy."
]

# Get daily quote
def get_quote_of_the_day():
    today = datetime.today().day
    return quotes[today % len(quotes)]

# File for journal entries
JOURNAL_FILE = "journal_entries.csv"
USERS_FILE = "users.csv"

# Initialize journal file if not exists
if not os.path.exists(JOURNAL_FILE):
    df_init = pd.DataFrame(columns=["username", "date", "mood", "gratitude", "affirmation"])
    df_init.to_csv(JOURNAL_FILE, index=False)

# Initialize user file if not exists
if not os.path.exists(USERS_FILE):
    users_df = pd.DataFrame([{"username": "admin", "password": "admin123"}])
    users_df.to_csv(USERS_FILE, index=False)

# Login system
def check_user_login():
    st.sidebar.subheader("🔐 Login to Your Journal")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login = st.sidebar.button("Login")

    if login:
        try:
            users_df = pd.read_csv(USERS_FILE)
            if ((users_df['username'] == username) & (users_df['password'] == password)).any():
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.sidebar.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials.")
        except FileNotFoundError:
            st.sidebar.error("User database not found.")

    # ✅ Handle logged-in session and logout
    if "logged_in" in st.session_state and st.session_state["logged_in"]:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 Logged in as: `{st.session_state['username']}`")
        if st.sidebar.button("🚪 Logout"):
            st.session_state["logged_in"] = False
            st.session_state["username"] = None
            st.rerun()
        return st.session_state["username"]

    return None

# Add journal entry
def add_journal_entry(username):
    st.markdown("### ✍️ Fill in your journal below")
    st.markdown("---")
    st.subheader("📝 Today's Journal")
    mood = st.selectbox("How are you feeling today?", ["😊 Happy", "😐 Okay", "😔 Sad", "😠 Angry", "😴 Tired"])
    gratitude = st.text_area("🙏 I am grateful for...", height=100)
    affirmation = st.text_input("💖 My positive affirmation for today:")
    image = st.file_uploader("🖼️ Add an image (optional)", type=["png", "jpg", "jpeg"])
    if st.button("📥 Save Entry"):
        if gratitude.strip() == "" or affirmation.strip() == "":
            st.warning("Please fill in both gratitude and affirmation.")
        else:
            new_entry = {
                "username": username,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "mood": mood,
                "gratitude": gratitude,
                "affirmation": affirmation,
                "image_name": image.name if image else ""
            }
            if image:
                os.makedirs("uploads", exist_ok=True)
                with open(os.path.join("uploads", image.name), "wb") as f:
                    f.write(image.read())
            df = pd.read_csv(JOURNAL_FILE)
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(JOURNAL_FILE, index=False)
            st.success("Your journal entry has been saved!")

def signup_user():
    st.sidebar.subheader("🆕 Create a New Account")
    new_username = st.sidebar.text_input("New Username", key="signup_username")
    new_password = st.sidebar.text_input("New Password", type="password", key="signup_password")
    confirm_password = st.sidebar.text_input("Confirm Password", type="password", key="confirm_password")
    create_account = st.sidebar.button("Sign Up")

    if create_account:
        if not new_username or not new_password:
            st.sidebar.warning("Please fill in all fields.")
        elif new_password != confirm_password:
            st.sidebar.warning("Passwords do not match.")
        else:
            try:
                users_df = pd.read_csv(USERS_FILE)
            except FileNotFoundError:
                users_df = pd.DataFrame(columns=["username", "password"])

            if new_username in users_df["username"].values:
                st.sidebar.error("Username already exists. Choose another.")
            else:
                new_user = pd.DataFrame([{"username": new_username, "password": new_password}])
                users_df = pd.concat([users_df, new_user], ignore_index=True)
                users_df.to_csv(USERS_FILE, index=False)
                st.sidebar.success("Account created! Please log in.")

# Main app logic
signup_user()  # Allow user to register before logging in
username = check_user_login()
# 🎨 Theme Selector
theme = st.sidebar.radio("🎨 Choose Theme", ["Light", "Soft Pink"])

if theme == "Soft Pink":
    st.markdown("""
        <style>
            body {
                background-color: #fff0f5;
            }
        </style>
    """, unsafe_allow_html=True)

if username:
    st.title("🌸 My Gratitude Journal")
    st.markdown(f"""
    <div style='background-color:#fff0f5; padding: 15px; border-radius: 12px; margin-bottom: 20px;'>
        <h3 style='color:#c71585;'>Hello, {username}! 🌼</h3>
        <p style='color:#6a5acd; font-size: 16px;'>Today is a beautiful day to reflect on what you’re grateful for 💫</p>
    </div>
    """, unsafe_allow_html=True)
    # Load user entries
    df = pd.read_csv(JOURNAL_FILE)
    user_entries = df[df["username"] == username]

    # Count total entries
    entry_count = user_entries.shape[0]
    st.markdown(f"🗓️ You’ve written **{entry_count}** gratitude entries so far! Keep going strong 💖")

    today_str = datetime.now().strftime("%Y-%m-%d")
    if today_str not in user_entries["date"].values:
        st.warning("⏰ You haven’t added a journal entry today. Take a moment to reflect 🌿")


    st.markdown(f"🌟 *Quote of the Day:* “{get_quote_of_the_day()}”")
    tab1, tab2, tab3 = st.tabs(["📔 Log Today", "📚 View Entries", "🪞 Reflect Weekly"])

    with tab1:
        add_journal_entry(username)

    with tab2:
        st.markdown("### 📚 Browse your gratitude moments")
        st.markdown("---")
        st.subheader("📖 Your Past Entries")
        try:
            df = pd.read_csv(JOURNAL_FILE)
            user_entries = df[df["username"] == username]
            # 🧠 Mood Analytics
            # 🗓️ Date Filter
            st.markdown("### 📊 Mood Overview")

            if not user_entries.empty:
                mood_count = user_entries["mood"].value_counts().reset_index()
                mood_count.columns = ["Mood", "Count"]

                fig = px.pie(mood_count, names="Mood", values="Count", title="Your Mood Distribution",
                            color_discrete_sequence=px.colors.sequential.RdPu)
                st.plotly_chart(fig)
            else:
                st.info("No entries yet to analyze mood.")
            
            # 📊 Weekly Mood Trend (Bar Chart)
            user_entries["date"] = pd.to_datetime(user_entries["date"])
            user_entries["week"] = user_entries["date"].dt.to_period("W").astype(str)
            weekly_mood = user_entries.groupby(["week", "mood"]).size().reset_index(name="count")
            fig_bar = px.bar(
                weekly_mood,
                x="week",
                y="count",
                color="mood",
                title="Mood Trend by Week",
                barmode="group",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_bar)

            # 🗓️ Add Date Filter
            st.markdown("#### 🔍 Filter by Date")
            selected_date = st.date_input("Choose a date to view specific entries (or leave it to view all):")

            # Format selected date to match stored format
            selected_str = selected_date.strftime("%Y-%m-%d")

            # Filter by selected date
            filtered_entries = user_entries[user_entries["date"] == selected_str]

            if filtered_entries.empty:
                st.info("No entries found for the selected date.")

            if user_entries.empty:
                st.info("You haven't added any entries yet.")
            else:
                # ✅ Download button
                st.download_button(
                    label="⬇️ Download My Journal as CSV",
                    data=user_entries.to_csv(index=False),
                    file_name=f"{username}_journal.csv",
                    mime="text/csv"
                )

                # Display all entries in reverse order
                for idx, row in user_entries[::-1].iterrows():
                    with st.expander(f"📅 {row['date']} — {row['mood']}"):
                        edited_grat = st.text_area("🙏 Gratitude", row['gratitude'], key=f"gratitude_{idx}")
                        edited_aff = st.text_input("💖 Affirmation", row['affirmation'], key=f"affirmation_{idx}")
                        # 📷 Display image if available
                        image_filename = str(row.get("image_name", "")).strip()

                        if image_filename and image_filename.lower() != "nan":
                            image_path = os.path.join("uploads", image_filename)
                            if os.path.exists(image_path):
                                st.image(image_path, width=250, caption="Your journal image")

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📝 Save Changes", key=f"save_{idx}"):
                                df.at[idx, 'gratitude'] = edited_grat
                                df.at[idx, 'affirmation'] = edited_aff
                                df.to_csv(JOURNAL_FILE, index=False)
                                st.success("✅ Changes saved!")
                                st.rerun()  # 🔄 Updated here
                        with col2:
                            if st.button("🗑️ Delete Entry", key=f"delete_{idx}"):
                                df = df.drop(idx)
                                df.to_csv(JOURNAL_FILE, index=False)
                                st.warning("❌ Entry deleted.")
                                st.rerun()  # 🔄 To reflect the deletion immediately

        except FileNotFoundError:
            st.warning("No journal entries found.")
    with tab3:
        st.subheader("🪞 Write to Your Future Self")
        st.markdown("Reflect on your week, your growth, or anything you want to remember.")

        reflection = st.text_area("💭 Your message", height=200)
        if st.button("💌 Save Reflection"):
            with open(f"weekly_notes/{username}_{datetime.now().strftime('%Y-%m-%d')}.txt", "w") as f:
                f.write(reflection)
            st.success("Your reflection was saved 💗")

else:
    st.title("🌸 Welcome to My Trust Diary")
    st.markdown("""
        <div style='background-color:#fff0f5; padding: 20px; border-radius: 15px;'>
            <h2 style='color:#c71585;'>Reflect • Reconnect • Rejoice</h2>
            <p style='color:#6a5acd; font-size: 16px;'>
                This is your personal gratitude space where you can record moments of joy, track your emotions, 
                                   and build a habit of positivity ✨
            </p>
        </div>
    """, unsafe_allow_html=True)
    # Features overview
    st.markdown("### 🧰 Features")
    st.markdown("""
    - ✍️ Daily Gratitude & Affirmation Entries  
    - 📅 Date Filter & Mood Tracking  
    - 📊 Mood Analytics (Pie Chart)  
    - 📝 Edit or Delete Past Reflections  
    - ⬇️ Download Your Journal Anytime  
    """)

    # Motivation
    st.markdown("### 🌟 Quote of the Day")
    st.success(f"“{get_quote_of_the_day()}”")

    # Footer
    st.markdown("""
        <hr>
        <p style='text-align:center; color: gray;'>Login from the sidebar to begin your gratitude journey 🌷</p>
    """, unsafe_allow_html=True)
