# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col


# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """**Choose the fruits you want in your custom smoothie!**
  """
)

cnx = st.connection("snowflake")
session = cnx.session()
my_data_frame = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col("FRUIT_NAME"))

#st.dataframe(data = my_data_frame,use_container_width= True)

title = st.text_input('Name on Smoothiee')
st.write('The name on Smoothiee will be',title)
ingredients_list =st.multiselect(
    'Choose up to 5 ingredients',
    my_data_frame,
    max_selections=5
)

if ingredients_list:
    ingredients_string =''
    for fruit_choosen in ingredients_list:
        ingredients_string+=fruit_choosen + ' '    
    my_insert_stmt =""" INSERT INTO SMOOTHIES.PUBLIC.ORDERS(INGREDIENTS,name_on_order) 
    VALUES('""" + ingredients_string + """','""" + title +""" ')"""
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
    

