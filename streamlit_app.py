import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

st.set_page_config(page_title="Smoothie Builder", page_icon="🥤", layout="centered")

st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# ✅ Get Snowflake connection + session
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options from Snowflake
my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col("FRUIT_NAME"))
fruit_options = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Multiselect input
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# ✅ Submit order
if st.button("Submit Order"):
    if ingredients_list and name_on_order:
        # Build ingredients string
        ingredients_string = ", ".join(ingredients_list)

        # Insert order into Snowflake (safe binding)
        session.sql(
            "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success(f"✅ Your Smoothie for **{name_on_order}** is ordered!")

    elif ingredients_list and not name_on_order:
        st.warning("⚠️ Please enter a name for your smoothie before ordering.")
    else:
        st.warning("⚠️ Please select at least one ingredient and enter a name before submitting.")

# -------------------------------------------------------------------
# 🍍 SmoothieFroot API Section
# -------------------------------------------------------------------
st.header("🍓 Get Fruit Nutrition Info")

fruit_choice = st.text_input("Enter a fruit name to fetch details:", "watermelon")

if fruit_choice:
    smoothiefroot_response = requests.get(
        f"https://my.smoothiefroot.com/api/fruit/{fruit_choice.lower()}"
    )

    if smoothiefroot_response.status_code == 200:
        fruit_data = smoothiefroot_response.json()

        # Show raw JSON
        st.subheader(f"📦 API Response for {fruit_choice.title()}")
        st.json(fruit_data)

        # Convert JSON → DataFrame
        sf_df = pd.json_normalize(fruit_data)
        st.subheader("📊 Nutrition Data")
        st.dataframe(sf_df)
    else:
        st.error(f"❌ API request failed: {smoothiefroot_response.status_code}")
