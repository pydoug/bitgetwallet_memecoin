import csv
import os
from datetime import datetime
import logging

# Configuration
logging.basicConfig(
    filename='simplified_log.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# File paths
horarios_csv_path = r'C:\Users\Douglas\Desktop\BitGetWallet_MemeCoin\horarios.csv'
contratos_csv_dir = r'C:\Users\Douglas\Desktop\BitGetWallet_MemeCoin\output_csvs'
reference_date = '2024-11-28'

def consultar_preco_e_ath(token, hour, reference_date='2024-11-28'):
    try:
        datetime_str = f"{reference_date} {hour}:00"
        target_datetime = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        csv_path = os.path.join(contratos_csv_dir, f'{token}.csv')

        if not os.path.isfile(csv_path):
            return {'price': 'N/A', 'ath_price': 'N/A', 'ath_time': 'N/A', 'live_price': 'N/A', 'live_time': 'N/A', 'profit_x': 'N/A', 'profit_dollar': 'N/A'}

        price_at_hour = 'N/A'
        ath_price = None
        ath_time = 'N/A'
        live_price = 'N/A'
        live_time = 'N/A'

        with open(csv_path, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row_time = datetime.strptime(row['datetime'], '%Y-%m-%d %H:%M:%S')
                if row_time == target_datetime:
                    price_at_hour = float(row.get('close', 0))
                if row_time > target_datetime:
                    high = float(row.get('high', 0))
                    if ath_price is None or high > ath_price:
                        ath_price = high
                        ath_time = row['datetime']
                live_price = float(row.get('close', 0))
                live_time = row['datetime']

        profit_x = round(ath_price / price_at_hour, 2) if price_at_hour > 0 and ath_price else 0
        profit_dollar = round(100 * profit_x, 1) if profit_x >= 1.99 else -100

        return {
            'price': price_at_hour,
            'ath_price': ath_price,
            'ath_time': ath_time,
            'live_price': live_price,
            'live_time': live_time,
            'profit_x': profit_x,
            'profit_dollar': profit_dollar
        }
    except Exception as e:
        logging.error(f"Error processing {token}: {e}")
        return {'price': 'N/A', 'ath_price': 'N/A', 'ath_time': 'N/A', 'live_price': 'N/A', 'live_time': 'N/A', 'profit_x': 'N/A', 'profit_dollar': 'N/A'}

def process_results(file_path):
    total_profit = 0
    rows = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hour = row.get('hour', 'N/A')
                token = row.get('ca', 'N/A')
                name = row.get('name', 'N/A')

                if not hour or not token:
                    continue

                result = consultar_preco_e_ath(token, hour, reference_date)
                if result:
                    profit_x = result['profit_x']
                    profit_dollar = result['profit_dollar']

                    if profit_dollar != 'N/A':
                        total_profit += profit_dollar

                    rows.append([name, f"{profit_x:.2f}", f"{profit_dollar:.1f}", token])

        print(f"{'Name':<15} | {'Profit X':<10} | {'Profit $':<10} | {'CA':<40}")
        print("-" * 80)
        for row in rows:
            print(f"{row[0]:<15} | {row[1]:<10} | {row[2]:<10} | {row[3]:<40}")
        print("-" * 80)
        print(f"Total Profit: {total_profit:.1f}")

    except Exception as e:
        logging.error(f"Error processing results: {e}")
        print(f"Error: {e}")

def process_simplified(file_path):
    total_profit = 0
    rows = []

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                hour = row.get('hour', 'N/A')
                token = row.get('ca', 'N/A')
                name = row.get('name', 'N/A')

                if not hour or not token:
                    continue

                result = consultar_preco_e_ath(token, hour, reference_date)
                if result:
                    profit_x = result['profit_x']
                    profit_dollar = result['profit_dollar']

                    if profit_x != 'N/A' and profit_x < 1.99:
                        profit_x = 0
                        profit_dollar = -100

                    rows.append([name, f"{profit_x:.2f}", f"{profit_dollar:.1f}", token])

                    if profit_dollar != 'N/A':
                        total_profit += profit_dollar

        print("\nSimplified Mode:")
        print(f"{'Name':<15} | {'Profit X':<10} | {'Profit $':<10} | {'CA':<40}")
        print("-" * 80)
        for row in rows:
            print(f"{row[0]:<15} | {row[1]:<10} | {row[2]:<10} | {row[3]:<40}")
        print("-" * 80)
        print(f"Total Profit: {total_profit:.1f}")

    except Exception as e:
        logging.error(f"Error processing simplified results: {e}")
        print(f"Error: {e}")

def main():
    process_results(horarios_csv_path)
    process_simplified(horarios_csv_path)

if __name__ == "__main__":
    main()
