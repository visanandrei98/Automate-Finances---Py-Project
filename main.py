import pandas as pd  # Pentru manipularea tabelelor de date
import streamlit as st  # Pentru interfață web interactivă
import os  # Pentru verificarea existenței fișierelor
import json  # Pentru salvarea și încărcarea categoriilor din/în fișier JSON
import plotly.express as px  # Pentru generarea de grafice (Pie chart)

# Numele fișierului unde se salvează categoriile și keywordurile aferente
category_file = "categories.json"

# Inițializare variabile globale în session_state dacă nu există deja
if "debits_df" not in st.session_state:
    st.session_state.debits_df = None

if "credits_df" not in st.session_state:
    st.session_state.credits_df = None

if "categories" not in st.session_state:
    st.session_state.categories = {"Uncategorized": []}  # Categorie de rezervă implicită

# Dacă fișierul categories.json există, îl încarcă în session_state
if os.path.exists(category_file):
    with open(category_file, "r") as f:
        st.session_state.categories = json.load(f)

# Titlul aplicației în interfață
st.title("Simple Finance App")

# Încărcare fișier CSV de la utilizator
uploaded_file = st.file_uploader("Upload a csv file", type=["csv"])


# Funcție care adaugă un keyword la o categorie și salvează în JSON
def add_keyword_to_category(category, keyword):
    kw = keyword.lower().strip()  # Normalizează keyword-ul
    if kw not in st.session_state.categories[category]:
        st.session_state.categories[category].append(kw)  # Adaugă keyword
        save_categories()  # Salvează în JSON


# Funcție pentru salvarea `categories.json`
def save_categories():
    with open(category_file, "w") as f:
        json.dump(st.session_state.categories, f)


# Funcția principală care rulează logica aplicației
def main():
    if uploaded_file is not None:  # Dacă utilizatorul a încărcat fișierul
        df = pd.read_csv(uploaded_file)  # Citește fișierul într-un DataFrame
        df["Amount"] = df["Amount"].str.replace(",", "")  # Curăță virgulă din sume
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")  # Conversie text->float

        # Adaugă o categorie nouă din UI
        add_text_input = st.text_input("Type the new category")
        add_button = st.button("Add Category", on_click=save_categories)

        if add_button and add_text_input:
            st.session_state.categories[add_text_input] = []  # Creează listă goală pt keywords
            save_categories() #l-ai declarat mai sus -> cel cu json.dump pentru a popula json.file cu categorii noi
            st.success("Category added!")
            st.rerun()  # Reîncarcă aplicația pentru a vedea modificările -> fara sa dai reload la pagina

        st.dataframe(df)  # Afișează fișierul brut inițial -> afiseaza tabelul de date

        st.session_state["transactions"] = df  # Salvează toate tranzacțiile în memorie

        categories = st.session_state.categories  # Shortcut pentru categorie -> sa fie mai usor de folosit(scris)

        df["Category"] = "Uncategorized"  # Inițializează coloana Category -> ea nu exista inainte si o creeaza acum prin aceasta comanda

        # CATEGORISIRE automată folosind keywords
        for idx, row in df.iterrows():
            details_text = str(row["Details"]).lower().strip()
            for category, keywords in categories.items():
                for keyword in keywords:
                    if keyword in details_text:
                        df.at[idx, "Category"] = category
                        break

        # Înlocuiește NaN cu „Uncategorized”
        df["Category"] = df["Category"].fillna("Uncategorized")

        # Validează că toate categoriile sunt în listă
        valid_categories = list(st.session_state.categories.keys())
        df.loc[~df["Category"].isin(valid_categories), "Category"] = "Uncategorized"

        # Salvează în memorie tranzacțiile
        st.session_state["transactions"] = df

        # Separă debits și credits
        st.session_state.debits_df = df[df["Debit/Credit"] == "Debit"].copy()
        st.session_state.credits_df = df[df["Debit/Credit"] == "Credit"].copy()

        # Calculează sumele totale
        total_credits = st.session_state.credits_df["Amount"].sum()
        total_debits = st.session_state.debits_df["Amount"].sum()

        # Creează două taburi: Debits și Credits
        tab1, tab2 = st.tabs(["Debits", "Credits"])
        with tab1:
            st.metric("Total Expenses", f"${total_debits:.2f}")
        with tab2:
            st.metric("Total Expenses", f"${total_credits:.2f}")

        # Editor interactiv pentru Debits
        st.subheader("Debits Table")
        edit_table_debits = st.data_editor(
            st.session_state.debits_df[["Date", "Details", "Amount", "Category"]],
            column_config={
                "Category": st.column_config.SelectboxColumn(
                    "Category",  # Titlul coloanei
                    options=list(st.session_state.categories.keys())  # Opțiuni din JSON
                )
            },
            hide_index=True,
            use_container_width=True,
            key="debits_table"
        )

        # Editor interactiv pentru Credits
        st.subheader("Credits Table")
        edit_table_credits = st.data_editor(
            st.session_state.credits_df[["Date", "Details", "Amount", "Category"]],
            column_config={
                "Category": st.column_config.SelectboxColumn(
                    "Category",
                    options=list(st.session_state.categories.keys())
                )
            },
            hide_index=True,
            use_container_width=True,
            key="credits_table"
        )

        # Buton care salvează manual modificările + keyword nou
        save_button = st.button("Save", type="primary")

        if save_button:
            # Parcurge rândurile din Debits și salvează modificările
            for idx, row in edit_table_debits.iterrows():
                new_category = row["Category"]
                old_category = st.session_state.debits_df.at[idx, "Category"]

                if new_category != old_category:
                    st.session_state.debits_df.at[idx, "Category"] = new_category
                    details = row["Details"]
                    add_keyword_to_category(new_category, details)

            # La fel și pentru Credits
            for idx, row in edit_table_credits.iterrows():
                new_category = row["Category"]
                old_category = st.session_state.credits_df.at[idx, "Category"]

                if new_category != old_category:
                    st.session_state.credits_df.at[idx, "Category"] = new_category
                    details = row["Details"]
                    add_keyword_to_category(new_category, details)

        # Graficele Pie pentru Debits și Credits
        st.subheader("Debits Pie Chart")
        fig = px.pie(
            names="Category",
            values="Amount",
            data_frame=df[df["Debit/Credit"] == "Debit"]
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Credits Pie Chart")
        fig = px.pie(
            names="Category",
            values="Amount",
            data_frame=df[df["Debit/Credit"] == "Credit"]
        )
        st.plotly_chart(fig, use_container_width=True)


# Rularea funcției principale
main()
