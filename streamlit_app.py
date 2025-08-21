import streamlit as st
from snowflake.snowpark.functions import col
import requests

st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# ================================
# 🍹 Smoothie Order Section
# ================================

# Input for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# ✅ Get Snowflake connection + session
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
fruit_options = [row["FRUIT_NAME"] for row in my_dataframe.collect()]

# Multiselect input
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# ✅ Only run when button clicked
if st.button("Submit Order"):
    if ingredients_list and name_on_order:  
        # Build ingredients string (comma-separated for clarity)
        ingredients_string = ", ".join(ingredients_list)

        # Insert order into Snowflake
        my_insert_stmt = f"""
            insert into SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER)
            values ('{ingredients_string}', '{name_on_order}')
        """
        session.sql(my_insert_stmt).collect()

        st.success(f"Your Smoothie for **{name_on_order}** is ordered! ✅")

    elif ingredients_list and not name_on_order:
        st.warning("⚠️ Please enter a name for your smoothie before ordering.")
    else:
        st.warning("⚠️ Please select at least one ingredient and enter a name before submitting.")


# ================================
# 🥋 SmoothieFroot Nutrition API
# ================================
st.header("🍓 Get Nutrition Info from SmoothieFroot")

# User enters fruit name for nutrition info
fruit_choice = st.text_input("Enter a fruit name to get nutrition info:", "watermelon")

if fruit_choice:
    smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_choice.lower()}")

    if smoothiefroot_response.status_code == 200:
        fruit_data = smoothiefroot_response.json()

        # Show raw JSON response
        st.subheader("📦 Raw API Response")
        st.text(fruit_data)

        # Convert JSON into a DataFrame
        st.subheader(f"📊 Nutrition Info for {fruit_choice.title()}")
        st.dataframe(data=fruit_data, use_container_width=True)

    else:
        st.error(f"❌ API request failed with status {smoothiefroot_response.status_code}")
