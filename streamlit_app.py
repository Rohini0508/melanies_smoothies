import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

st.title("Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for smoothie name
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be:", name_on_order)

# Get Snowflake session and fruit options
session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Multiselect input
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# ✅ Only run when button clicked
if st.button("Submit Order"):
    if ingredients_list and name_on_order:  
        # Build ingredients string (comma-separated for clarity)
        ingredients_string = ', '.join(ingredients_list)

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
