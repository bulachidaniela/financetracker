
# 💰 Smart Finance Tracker

An interactive [Streamlit](https://streamlit.io/) app for managing your personal budget, tracking expenses, and analyzing financial trends.

## 🚀 Features

- **Simple login** with a username.
- **Add expenses** with:
  - date
  - description
  - amount
  - category
- **Customizable categories** via the sidebar.
- **Monthly budget** with progress bar and alerts when exceeded.
- **Import/Export** data as CSV.
- **Statistics & trends**:
  - monthly spending evolution (line chart)
  - top spending categories
  - monthly average & alerts
  - bar & pie charts by category
- **Prediction** for next month’s spending (via `predict_next_month_spending`).
- **Month-to-month comparison** (chart & percentage per category).
- **Data reset** and **logout** options.

## 🛠️ Tech Stack

- Python 3.10+
- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Altair](https://altair-viz.github.io/)
- [scikit-learn](https://scikit-learn.org/stable/)
- NumPy

## 📂 Project Structure

```

.
├── app.py                  # Main Streamlit app
├── predict.py              # Prediction logic
├── settings.py             # Settings save/load functions
├── <user>\_data.csv         # User data file (generated at runtime)
└── requirements.txt        # Dependencies

````

## ▶️ How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/user/smart-finance-tracker.git
   cd smart-finance-tracker
````

2. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

3. Start the app:

   ```bash
   streamlit run app.py
   ```

4. Open the URL shown in the terminal (default: `http://localhost:8501`).



Do you want me to prepare that modular version next?
```
