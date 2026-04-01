import requests
import os
from dotenv import load_dotenv

#initialization
load_dotenv()
BOARD_ID= "xCt7BUDf"
url = f"https://api.trello.com/1/boards/{BOARD_ID}/lists"
query = {
    "key":  os.getenv("TRELLO_API_KEY"),
    "token": os.getenv("TRELLO_TOKEN")
}



response = requests.get(url, params=query)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)