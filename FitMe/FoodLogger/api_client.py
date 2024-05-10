# utils.py
import requests, openai, os
from dotenv import load_dotenv
load_dotenv()

def search_food(api_key, query):
    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "api_key": api_key,
        "query": query
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

def get_nutrient_values(api_key, fdc_id):
    url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
    params = {
        "api_key": api_key
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data['foodNutrients']
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None

openai.api_key = os.getenv("SECRET_KEY") 
messages = [{"role": "system", "content": "You are a chatbot named Nute that answers nutrition or health-related questions"}]

def CustomChatGPT(user_input):
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    ChatGPT_reply = response["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": ChatGPT_reply})
    return ChatGPT_reply