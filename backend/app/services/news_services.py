import requests
import os
from app.models.news_item import NewsItem


API_KEY = os.getenv("NEWS_API_KEY")

# News API's specific address to retrieve what's trending atm
BASE_URL = "https://newsapi.org/v2/top-headlines" 

# US provides more data and more global content.
# create a button in Streamlit later where you select the country!
def get_top_headlines(country="us"):
    # Pass parameters to the API
    params = {
        "country": country,
        "apiKey": API_KEY
    }
    
    response = requests.get(BASE_URL, params=params)
    
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        
        # Map (transform) the News API's data to NewsItem model
        news_list = []
        for art in articles[:5]: # 5 newest aeticles to begin with 
            item = NewsItem(
                title=art["title"],
                url=art["url"],
                source=art["source"]["name"],
                description=art.get("description") # .get tries find description. If not there, None will be used instead of a missing paramter crashing the program
            )
            news_list.append(item)
        return news_list
    
    return [] # improve error ganfling here later 