# Import python packages
import streamlit as st 
from snowflake.snowpark.functions import col
import requests


# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write(
  """**Choose the fruits you want in your custom smoothie!**
  """
)

cnx = st.connection("snowflake")
session = cnx.session()
my_data_frame = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS") \
                      .select(col("FRUIT_NAME"), col("SEARCH_ON"))

#st.dataframe(data = my_data_frame,use_container_width= True)
#st.stop()
#Convert the Snowpark DataFrame to a pandas DataFrame so we can use the LOC Function
pd_df = my_data_frame.to_pandas()
#st.dataframe(pd_df)
#st.stop()

title = st.text_input('Name on Smoothiee')
st.write('The name on Smoothiee will be',title)
ingredients_list =st.multiselect(
    'Choose up to 5 ingredients',
    my_data_frame,
    max_selections=5
)

if ingredients_list:
    ingredients_string =''
    for fruit_chosen in ingredients_list:
        ingredients_string+=fruit_choosen + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        st.subheader(fruit_choosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_choosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)

    my_insert_stmt =""" INSERT INTO SMOOTHIES.PUBLIC.ORDERS(INGREDIENTS,name_on_order) 
    VALUES('""" + ingredients_string + """','""" + title +""" ')"""
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

