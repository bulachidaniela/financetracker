import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from sklearn.linear_model import LinearRegression
import numpy as np
import os
import json
from predict import predict_next_month_spending
from settings import save_settings
from settings import load_settings


def init_session_state():
    if "user" not in st.session_state:
        st.session_state["user"] = None

    if "history" not in st.session_state:
        st.session_state["history"] = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])

    if "settings" not in st.session_state:
        st.session_state["settings"] = {
            "monthly_budget": 2000.0,
            "categories": ["Food", "Transport", "Rent", "Subscriptions", "Other"]
        }
    if "show_form" not in st.session_state:
        st.session_state.show_form = False

    if "show_graphic" not in st.session_state:
        st.session_state.show_graphic = False

    if "categories" not in st.session_state:
        st.session_state.categories = ["Food", "Transport", "Rent", "Subscriptions", "Other"]

    if "monthly_budget" not in st.session_state:
        st.session_state.monthly_budget = 0.0

init_session_state()

st.title("💰 Smart Finance Tracker")
def login_and_load_data():
    if st.session_state["user"] is None:
        st.markdown("## Welcome!")
        st.markdown("Please enter your username to continue")
        username = st.text_input("Username", placeholder="Enter your username")
        if st.button("Next") and username.strip():
            st.session_state["user"] = username.strip()
            user = st.session_state["user"]
            with st.spinner("Loading your data..."):

            # Load expense history
                data_file = f"{user}_data.csv"
                if os.path.exists(data_file):
                    st.session_state["history"] = pd.read_csv(data_file, parse_dates=["Date"])
                else:
                    st.session_state["history"] = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])

            # Load settings
            settings = load_settings(user)
            if settings:
                st.session_state["settings"].update(settings)
            st.rerun()
        return False
    else:
        st.title(f"Hello, {st.session_state['user']}!")
        return True


def prepare_monthly_data():
    st.session_state.history["Date"] = pd.to_datetime(
        st.session_state.history["Date"], errors="coerce"
    )
    now_month = datetime.now().month
    now_year = datetime.now().year
    df_month = st.session_state.history[
        (st.session_state.history["Date"].dt.month == now_month) &
        (st.session_state.history["Date"].dt.year == now_year)
    ]
    return df_month["Amount"].sum()



def export_import_section():
    st.subheader("📤 Export / 📥 Import")

    # === EXPORT ===
    if not st.session_state.history.empty:
        csv = st.session_state.history.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📤 Download History (CSV)",
            data=csv,
            file_name="spending_history.csv",
            mime="text/csv"
        )
    else:
        st.info("No data to export")


    # === IMPORT ===
    uploaded_file = st.file_uploader("📥 Import a file (CSV)", type=["csv"])
    if uploaded_file is not None:
        try:
            new_data = pd.read_csv(uploaded_file, parse_dates=["Date"])
            expected_cols = {"Date", "Description", "Amount", "Category"}
            if expected_cols.issubset(set(new_data.columns)):
                st.session_state.history = pd.concat(
                    [st.session_state.history, new_data],
                    ignore_index=True
                ).drop_duplicates()
                st.success("File was imported!")
            else:
                st.error("File must contain: Date, Description, Amount, Category")
        except Exception as e:
            st.error(f"Import failed: {e}")



def budget_progress_section(monthly_spendings):
    monthly_budget = st.session_state["settings"].get("monthly_budget", 0.0)
    st.subheader("📊 Monthly Budget Progress")
    if monthly_budget > 0:
        procent = min(monthly_spendings / monthly_budget, 1.0)
        st.progress(procent, text=f"{monthly_spendings:.2f} from {monthly_budget:.2f}")
        if monthly_spendings > monthly_budget:
            st.error("⚠️ You exceeded your budget!")
    else:
        st.info("Set a budget in the sidebar to see progress.")



def category_sidebar_section():
    # Ensure settings exists
    if "settings" not in st.session_state or st.session_state["settings"] is None:
        st.session_state["settings"] = {
            "monthly_budget": 2000.0,
            "categories": ["Food", "Transport", "Rent", "Subscriptions", "Other"]
        }

    # Make sure required keys exist in settings
    st.session_state["settings"].setdefault("monthly_budget", 2000.0)
    st.session_state["settings"].setdefault("categories", ["Food", "Transport", "Rent", "Subscriptions", "Other"])

    # Budget input (default to saved budget)
    st.session_state.monthly_budget = st.sidebar.number_input(
        "Your budget",
        min_value=0.0,
        format="%.2f",
        value=float(st.session_state["settings"]["monthly_budget"])
    )

    # 🔧 Sidebar: Add a new category

    st.sidebar.subheader("➕ Add a new category")
    new_cat = st.sidebar.text_input("New category")

    if st.sidebar.button("Add"):
        if new_cat.strip():
            if new_cat not in st.session_state["settings"]["categories"]:
                st.session_state["settings"]["categories"].append(new_cat.strip())
                st.sidebar.success(f"Added: {new_cat.strip()}")
            else:
                st.sidebar.warning("This category already exists")
        else:
            st.sidebar.warning("Type a valid category.")



    # Show categories
    st.sidebar.markdown("#### Categories:")
    st.sidebar.write(st.session_state["settings"]["categories"])

    # Save settings
    st.sidebar.header("Settings")
    if st.sidebar.button("Save settings"):
        # Clean up category list
        categories_list = [c.strip() for c in st.session_state["settings"]["categories"] if c.strip()]
        st.session_state["settings"]["monthly_budget"] = st.session_state.monthly_budget
        st.session_state["settings"]["categories"] = categories_list
        save_settings(st.session_state["user"], st.session_state["settings"])
        st.success("Settings saved!")
        st.rerun()


def add_spending_form():
    if st.button("➕ Add your spending"):
        st.session_state.show_form = True

    if st.session_state.get("show_form", False):
        with st.form(key="spending_form"):
            date = st.date_input("Date", datetime.now())
            description = st.text_input("Description")
            amount = st.number_input("Amount", min_value=0.0, format="%.2f")
            category = st.selectbox("Category", st.session_state["settings"].get("categories", []))
            submit = st.form_submit_button("Add")

            if submit:
                if description.strip() and category:
                    new_row = {
                        "Date": pd.to_datetime(date),
                        "Description": description.strip(),
                        "Amount": amount,
                        "Category": category
                    }
                    # Append new row
                    st.session_state.history = pd.concat(
                        [st.session_state.history, pd.DataFrame([new_row])],
                        ignore_index=True
                    )

                    # Ensure correct type
                    st.session_state.history["Date"] = pd.to_datetime(
                        st.session_state.history["Date"], errors="coerce"
                    )

                    # Save to CSV
                    data_file = f"{st.session_state['user']}_data.csv"
                    st.session_state.history.to_csv(data_file, index=False)

                    st.success("✅ Spending was saved and added!")
                    st.session_state.show_form = False  # hide form after saving
                    st.rerun()
                else:
                    st.warning("Please enter a description and choose a category.")

def predict_spendings():
    if st.button("🤖 predict spendings for your next month"):
        if st.session_state.history.empty:
            st.info("no suffiecient data.")
        else:
            pred = predict_next_month_spending(st.session_state.history)
            if pred:
                st.success(f"We predict you will spend: {pred:.2f} next month")
            else:
                st.warning("there is no sufficient data for prediction.")

def page():
# reflect history of spendings
    st.subheader("History of spendings ")
    st.dataframe(st.session_state["history"])

# reflect budget and amount spent this month
    now_month = pd.Timestamp.now().to_period("M")
    df = st.session_state["history"]
    df["Date"] = pd.to_datetime(df["Date"])
    month_spent = df[df["Date"].dt.to_period("M") == now_month]["Amount"].sum()

    st.markdown(f"**Monthly budget:** {st.session_state['settings']['monthly_budget']:.2f}")
    st.markdown(f"**Spendings this month:** {month_spent:.2f}")

    if month_spent > st.session_state["settings"]["monthly_budget"]:
        st.error("⚠️ you are out of your budget!")

def exit():
    st.markdown("---")
    st.subheader("🗑️ Data reset")

    if st.button("Delete all history"):
        st.session_state.history = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])
        st.success("History was deleted.")
    if st.button("Logout"):
        st.session_state["user"] = None
        st.session_state["history"] = pd.DataFrame(columns=["Date", "Description", "Amount", "Category"])
        st.session_state["settings"] = None
        st.rerun()

def stats_section():
    st.markdown("---")
    show_stats = st.button("📊 Show stats & trends")
    if show_stats:
        df = st.session_state.history.copy()
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.dropna(subset=["Date", "Amount"])
        
        df["Month"] = df["Date"].dt.to_period("M").astype(str)
        monthly_spendings = df.groupby("Month")["Amount"].sum().reset_index()

        # line chart
        st.subheader("📈 Evolutions of monthly spendings")
        st.line_chart(monthly_spendings.set_index("Month"))

        # Category with the most spendings
        top_category = df.groupby("Category")["Amount"].sum().sort_values(ascending=False).reset_index()
        if not top_category.empty:
            st.markdown(f"🏆 **The most expensive category:** `{top_category.iloc[0]['Category']}` with **{top_category.iloc[0]['Amount']:.2f}**")
        else:
            st.info("There is no spendings to share the evidence")

        # Monthly average
        total_amount = df["Amount"].sum()
        unique_months = df["Date"].dt.to_period("M").nunique()
        average = total_amount / unique_months if unique_months > 0 else 0
        st.markdown(f"🗓️ **Monthly average:** {average:.2f}")

        # Alert if spendings this month exceed average
        now_month_str = datetime.now().strftime("%Y-%m")
        now_month_spending = df[df["Month"] == now_month_str]["Amount"].sum()
        if now_month_spending > average:
            st.warning(f"⚠️ Attention! Spendings this month (**{now_month_spending:.2f}**) are bigger than the monthly average")

        # Bar chart (Altair)
        st.altair_chart(
            alt.Chart(monthly_spendings).mark_bar().encode(
                x="Month",
                y="Amount"
            ).properties(width=600, height=300),
            use_container_width=True
        )

# Graphic section if activated
def graphics_section():
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Show Graphic"):
                st.session_state.show_graphic = True
        with col2:
            if st.button("❌ Hide Graphic"):
                st.session_state.show_graphic = False

        if st.session_state.show_graphic:
            if st.session_state.history.empty:
                st.warning("No data")
            else:
                st.session_state.history["Month"] = st.session_state.history["Date"].dt.strftime("%Y-%m")
                available_months = sorted(st.session_state.history["Month"].unique(), reverse=True)

                col3, col4 = st.columns(2)
                with col3:
                    selected_month = st.selectbox("Pick the month for analyzing", available_months)
                with col4:
                    compared_month = st.selectbox("Pick the month to compare with", available_months, index=1 if len(available_months) > 1 else 0)

            df_month = st.session_state.history[st.session_state.history["Month"] == selected_month]
            df_comp = st.session_state.history[st.session_state.history["Month"] == compared_month]

            total_month = df_month["Amount"].sum()
            total_comp = df_comp["Amount"].sum()

            diff = total_month - total_comp
            if diff > 0:
                message = f"❗ You spent {diff:.2f} more in {selected_month} than in {compared_month}."
            elif diff < 0:
                message = f"✅ You saved {-diff:.2f} in {selected_month} compared to {compared_month}."
            else:
                message = f"⚖️ The spendings are equal."

            df_graphic = df_month.groupby("Category")["Amount"].sum().reset_index()

            st.write(f"### Spendings on categories for {selected_month}")
            chart = alt.Chart(df_graphic).mark_bar().encode(
                x=alt.X("Category", sort="-y"),
                y="Amount",
                color="Category",
                tooltip=["Category", "Amount"]
            ).properties(width=600, height=400)
            st.altair_chart(chart)

            st.write("#### Percentage distribution (Pie Chart)")
            df_graphic["Percent"] = (df_graphic["Amount"] / df_graphic["Amount"].sum()) * 100
            pie_chart = alt.Chart(df_graphic).mark_arc(innerRadius=50).encode(
                theta="Amount",
                color="Category",
                tooltip=["Category", "Amount", alt.Tooltip("Percent", format=".2f")]
            ).properties(width=400, height=400)
            st.altair_chart(pie_chart)

            st.markdown(f"""
            <div style='text-align:center; padding: 20px; font-size:24px; background-color:#f0f2f6; border-radius:10px; margin-top:20px;'>
                💸 <b>Total spent in {selected_month}:</b> {total_month:.2f}
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style='text-align:center; padding: 15px; font-size:20px; background-color:#d3e4f0; border-radius:10px; margin-top:15px;'>
                📊 <b>Compared to {compared_month}:</b><br>{message}
            </div>
            """, unsafe_allow_html=True)

#--- Main app execution ---

init_session_state()


if login_and_load_data():
    monthly_spendings = prepare_monthly_data()
    page()
    export_import_section()
    budget_progress_section(monthly_spendings)
    category_sidebar_section()
    add_spending_form()
    stats_section()    
    graphics_section()
    predict_spendings()
    exit()

