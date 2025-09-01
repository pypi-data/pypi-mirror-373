import requests
import pandas as pd
from io import BytesIO
from datetime import datetime

def addtweets(client, dataframe: pd.DataFrame, CONGRESS_ID: str):
    url = f"https://admin-portal.ferma.ai/congresses/{CONGRESS_ID}/tweets/add"
    
    buffer = BytesIO()
    dataframe.to_csv(buffer, index=False)
    buffer.seek(0)
    
    files = {"file": (f"tweets_{CONGRESS_ID}.csv", buffer, "text/csv")}
    response = requests.post(url, headers=client, files=files)
    if response.status_code == 200:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Tweets were successfully added to Congress ID: {CONGRESS_ID}")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Failed to add tweets to Congress ID: {CONGRESS_ID} (Status: {response.status_code}) {response.text}")


def modifytweets(client, dataframe: pd.DataFrame, CONGRESS_ID: str):
    url = f"https://admin-portal.ferma.ai/congresses/{CONGRESS_ID}/tweets/modify"
    
    buffer = BytesIO()
    dataframe.to_csv(buffer, index=False)
    buffer.seek(0)
    
    files = {"file": (f"tweets_{CONGRESS_ID}.csv", buffer, "text/csv")}
    response = requests.post(url, headers=client, files=files)
    if response.status_code == 200:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Tweets were successfully modified for Congress ID: {CONGRESS_ID}")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Failed to modify tweets for Congress ID: {CONGRESS_ID} (Status: {response.status_code}) {response.text}")

def populatebuzz(client, CONGRESS_ID: str):
    url = f"https://admin-portal.ferma.ai/congresses/{CONGRESS_ID}/sessions/buzz_score/populate"
    response = requests.post(url, headers=client)
    if response.status_code in (200, 202):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Buzz Score triggered for Congress ID: {CONGRESS_ID} (Status: {response.status_code})")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]: Failed to trigger buzz score for Congress ID: {CONGRESS_ID} (Status: {response.status_code}) {response.text}")