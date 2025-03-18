import streamlit as st

# Define the pages
main_page = st.Page("app.py", title="Controle", icon="🎈")
page_2 = st.Page("UC.py", title="Consulta", icon="❄️")

# Set up navigation
pg = st.navigation([main_page, page_2])

# Run the selected page
pg.run()



