# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import pandas as pd
import requests
from urllib.parse import quote  # for safe URL encoding

st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("**Choose the fruits you want in your custom smoothie!**")

# Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load table (Snowpark -> pandas)
my_data_frame = (
    session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS")
           .select(col("FRUIT_NAME"), col("SEARCH_ON"))
)
pd_df = my_data_frame.to_pandas()

# Build options for the multiselect (list of fruit names)
fruit_options = pd_df["FRUIT_NAME"].dropna().astype(str).tolist()

title = st.text_input("Name on Smoothie")
st.write("The name on Smoothie will be:", title)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients",
    fruit_options,
    max_selections=5
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list) + " "

    for fruit_chosen in ingredients_list:
        # Lookup SEARCH_ON; fallback to FRUIT_NAME if missing
        row = pd_df.loc[pd_df["FRUIT_NAME"] == fruit_chosen]
        if not row.empty:
            search_on_val = row["SEARCH_ON"].iloc[0]
        else:
            search_on_val = fruit_chosen

        # Ensure string, strip spaces, fallback if still blank
        search_on = str(search_on_val).strip()
        if not search_on:
            search_on = fruit_chosen

        # URL-encode (handles spaces & special chars safely)
        search_on_quoted = quote(search_on)

        st.subheader(f"{fruit_chosen} Nutrition Information")
        try:
            resp = requests.get(f"https://fruityvice.com/api/fruit/{search_on_quoted}", timeout=10)
            resp.raise_for_status()
            st.dataframe(data=resp.json(), use_container_width=True)
        except Exception as e:
            st.error(f"Could not fetch data for '{fruit_chosen}' (search: '{search_on}'). Error: {e}")

    # Safer insert (avoid string concat issues)
    # If you must keep simple SQL, at least replace single quotes in free text
    safe_title = (title or "").replace("'", "''")
    safe_ingredients = ingredients_string.replace("'", "''")

    my_insert_stmt = f"""
        INSERT INTO SMOOTHIES.PUBLIC.ORDERS (INGREDIENTS, name_on_order)
        VALUES ('{safe_ingredients}', '{safe_title}')
    """
    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered!", icon="✅")
