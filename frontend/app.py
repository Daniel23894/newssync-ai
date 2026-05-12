import streamlit as st
import requests

# set what is seen in browser window and first paragraph on the page itself 
st.set_page_config(page_title="NewsSync AI", page_icon="🚀")
st.title("Welcome to NewsSync AI")

#capital letters for constant variable
BACKEND_URL = "http://backend:8000"

try: 
    response = requests.get(BACKEND_URL)

    if response.status_code == 200:
        data = response.json()
        st.success(f"Connection successful Message: {data['message']}")

    else: st.error(f"Backend returned an error: {response.status_code}")

except Exception as e:
    st.warning("Could not connect to the backend. Is it running?")