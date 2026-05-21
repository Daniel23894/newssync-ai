import streamlit as st
import requests

# Set what is seen in the browser window tab and the main title on the page
st.set_page_config(page_title="NewsSync AI", page_icon="🚀")
st.title("Welcome to NewsSync AI")

# URL where the backend container lives inside the Docker network
BACKEND_URL = "http://backend:8000"

try: 
    # Ping the backend to grab the news data
    response = requests.get(BACKEND_URL)

    if response.status_code == 200:
        data = response.json()
        
        # check if we got a non empty list with articles / data inside, to avoid crash
        if isinstance(data, list) and data:
            first_item = data[0]
            
            # Show the headline in a green box and print the source below it
            st.success(f"Fundet: {first_item.get('title', 'Ukendt titel')}")
            st.write(f"Kilde: {first_item.get('source', 'Ukendt kilde')}")
        else:
            st.info("Ingen nyheder modtaget fra backend.")

    else:
        st.error(f"Backend returned an error: {response.status_code}")

except Exception as e:
    # catches connection failures if the backend container is completely offline
    st.warning("Could not connect to the backend. Is it running?")
    st.error(f"Teknisk fejlbesked: {e}")