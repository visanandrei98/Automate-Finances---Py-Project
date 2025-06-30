# 💰 Simple Finance Dashboard

A lightweight personal finance dashboard built using **Streamlit**, designed to help users upload, categorize, and visualize their bank transactions. Ideal for individuals or freelancers who want a privacy-friendly tool to track expenses without using third-party apps.

---

## ✨ Features

- 📁 Upload CSV files with transaction data
- 🔍 Auto-categorize transactions based on keywords
- ➕ Add new categories and train them with custom keywords
- 📝 Edit categories directly from the app interface
- 📊 Visualize your expenses with interactive pie charts
- 💾 Save categories persistently using local `JSON` file
- ⚡ Built with Streamlit for fast, browser-based interaction

---

## 📷 Screenshots

![image](https://github.com/user-attachments/assets/4b867beb-f561-4f0a-a096-e2a109971af2)
![image](https://github.com/user-attachments/assets/4993ab64-085b-4a25-8945-713a8c1fdc35)


---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) – UI Framework
- [Pandas](https://pandas.pydata.org/) – Data manipulation
- [Plotly Express](https://plotly.com/python/plotly-express/) – Data visualization
- JSON – Local category storage

Make sure you have Python installed. Then run the following commands to see the demo:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install pandas streamlit plotly
streamlit run main.py


