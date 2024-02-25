#!/usr/bin/python3

import requests
from notion_client import Client
from datetime import datetime, timedelta
import pytz  # To handle timezone conversions
from dotenv import load_dotenv  # Import this
import os  # Import this

# Load environment variables
load_dotenv()

# Your Notion integration token and database ID
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
CITY = os.getenv('CITY')
COUNTRY = os.getenv('COUNTRY')

# Define the prayer times we're interested in
PRAYER_TIMES_OF_INTEREST = ['Imsak', 'Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']

def get_prayer_times():
    url = f"http://api.aladhan.com/v1/timingsByCity?city={CITY}&country={COUNTRY}&method=13"
    response = requests.get(url)
    data = response.json()['data']['timings']
    
    # Map the API response to specified names and order
    prayer_times = {
        'Imsak': data['Fajr'],
        'Fajr': data['Sunrise'],
        'Dhuhr': data['Dhuhr'],
        'Asr': data['Asr'],
        'Maghrib': data['Maghrib'],
        'Isha': data['Isha']
    }
    
    # Return the prayer times in the specified order
    return {time: prayer_times[time] for time in PRAYER_TIMES_OF_INTEREST}

def update_notion(prayer_times):
    notion = Client(auth=NOTION_TOKEN)
    vienna_tz = pytz.timezone("Europe/Vienna")
    today_date = datetime.now(vienna_tz)
    formatted_date = today_date.strftime('%Y-%m-%d')

    for prayer_name in PRAYER_TIMES_OF_INTEREST:
        time = prayer_times[prayer_name]
        # Convert prayer time to the local timezone and format it
        prayer_time = vienna_tz.localize(datetime.strptime(f"{formatted_date} {time}", '%Y-%m-%d %H:%M'))
        
        if prayer_name == 'Fajr':
            # For Fajr, set the start time 20 minutes earlier
            start_time = prayer_time - timedelta(minutes=20)
            end_time = prayer_time
        else:
            # For other prayers, set a duration of 10 minutes
            start_time = prayer_time
            end_time = prayer_time + timedelta(minutes=10)
        
        # Create a new entry for each prayer time
        new_entry = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": prayer_name
                            }
                        }
                    ]
                },
                "Time": {
                    "date": {
                        "start": start_time.isoformat(),
                        "end": end_time.isoformat()
                    }
                }
            }
        }
        notion.pages.create(**new_entry)

def main():
    prayer_times = get_prayer_times()
    update_notion(prayer_times)

if __name__ == "__main__":
    main()
