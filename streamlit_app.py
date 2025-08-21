import streamlit as st
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for smoothie name
name_on_order = st.text_input("Name on Smoothie:")
if name_on_order:
    st.write(f"The name on your Smoothie will be: **{name_on_order}**")

# ✅ Get Snowflake connection + session
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options from Snowflake
fruit_df = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col("FRUIT_NAME"))
fruit_options = [row["FRUIT_NAME"] for row in fruit_df.collect()]

# Multiselect input
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_options,
    max_selections=5
)

# ✅ Only run when button clicked
if st.button("Submit Order"):
    if ingredients_list and name_on_order:
        # Build ingredients string (comma-separated)
        ingredients_string = ", ".join(ingredients_list)

        # Insert order into Snowflake using safe SQL binding
        session.sql(
            "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, NAME_ON_ORDER) VALUES (?, ?)",
            params=[ingredients_string, name_on_order]
        ).collect()

        st.success(f"Your Smoothie for **{name_on_order}** is ordered! ✅")

    elif ingredients_list and not name_on_order:
        st.warning("⚠️ Please enter a name for your smoothie before ordering.")
    else:
        st.warning("⚠️ Please select at least one ingredient and enter a name before submitting.")
