import csv
import cloudscraper
import json
from datetime import datetime, timedelta
import time
import os
import logging

logging.basicConfig(
    filename='process_log.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

input_csv_file_path = r'C:\Users\Douglas\Desktop\BitGetWallet_MemeCoin\ca.csv'
output_directory = r'C:\Users\Douglas\Desktop\BitGetWallet_MemeCoin\output_csvs'

base_url = 'https://gmgn.ai/defi/quotation/v1/tokens/mcapkline/sol/{token}?resolution=1m&from={from_ts}&to={to_ts}'

reference_date = '2024-11-28'

def to_unix_timestamp(date_str, time_str):
    dt_str = f"{date_str} {time_str}:00"
    try:
        dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        return int(dt.timestamp())
    except:
        return None

def get_all_tokens(file_path):
    tokens = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                token = row.get('ca')
                if token:
                    tokens.append(token)
        return tokens
    except:
        return []

def fetch_data(token, from_ts, to_ts):
    if from_ts is None or to_ts is None:
        print(f"Invalid timestamps for token: {token}")
        return None

    url = base_url.format(token=token, from_ts=from_ts, to_ts=to_ts)
    timestamp_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{timestamp_now} | {token}")

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'Referer': f'https://gmgn.ai/sol/token/{token}',
        'Accept-Language': 'pt-BR,pt;q=0.5',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-GPC': '1',
        'Sec-CH-UA': '"Brave";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'Sec-CH-UA-Arch': '"x86"',
        'Sec-CH-UA-Bitness': '"64"',
        'Sec-CH-UA-Full-Version-List': '"Brave";v="131.0.0.0", "Chromium";v="131.0.0.0", "Not_A Brand";v="24.0.0.0"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Model': '""',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-CH-UA-Platform-Version': '"10.0.0"',
        'Sec-Fetch-Dest': 'empty',
        'Upgrade-Insecure-Requests': '1',
    }


    try:
        scraper = cloudscraper.create_scraper()
        response = scraper.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except:
        print(f"Error fetching data for token: {token}")
        return None

def save_to_csv_per_token(token, data, directory):
    if not data or not isinstance(data, dict) or data.get('code') != 0 or not isinstance(data.get('data'), list):
        print(f"No valid data for token: {token}")
        return

    csv_data = []
    for item in data['data']:
        try:
            timestamp_sec = int(item.get('time', '0')) / 1000
            datetime_str = datetime.fromtimestamp(timestamp_sec).strftime('%Y-%m-%d %H:%M:%S')
            csv_data.append({
                'datetime': datetime_str,
                'open': item.get('open', ''),
                'high': item.get('high', ''),
                'low': item.get('low', ''),
                'close': item.get('close', ''),
                'volume': item.get('volume', '')
            })
        except:
            continue

    safe_token = ''.join(c for c in token if c.isalnum() or c in ('_', '-')).rstrip()
    output_csv = os.path.join(directory, f'{safe_token}.csv')

    try:
        with open(output_csv, mode='w', encoding='utf-8', newline='') as csvfile:
            fieldnames = ['datetime', 'open', 'high', 'low', 'close', 'volume']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)
        print(f"Saved data for token: {token}")
    except:
        print(f"Error saving data for token: {token}")

def process_all_tokens(input_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    tokens = get_all_tokens(input_file)
    if not tokens:
        print("No tokens found.")
        return

    to_datetime = datetime.strptime(reference_date, '%Y-%m-%d') + timedelta(days=1)
    from_datetime = to_datetime - timedelta(days=1)
    from_ts = int(from_datetime.timestamp())
    to_ts = int(to_datetime.timestamp())

    for idx, token in enumerate(tokens, start=1):
        data = fetch_data(token, from_ts, to_ts)
        if data:
            save_to_csv_per_token(token, data, output_dir)
        time.sleep(1)

    print("Processing complete.")

if __name__ == "__main__":
    process_all_tokens(input_csv_file_path, output_directory)
