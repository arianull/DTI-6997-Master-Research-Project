import os
import pandas as pd
import datetime
import argparse
from loguru import logger



def load_latest_screener(input_path: str):
    files = os.listdir(input_path)
    csv_files = [file for file in files if file.endswith('.csv')]
    if not csv_files:
        logger.error("No CSV files found in the provided path.")
        return pd.DataFrame()
    latest_file = max(csv_files, key=lambda x: int(x.split('_')[2].split('.')[0]))
    file_path = os.path.join(input_path, latest_file)
    df = pd.read_csv(file_path, index_col='No.')
    logger.success(f'Latest screener download file {latest_file} loaded.')
    return df


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Applies formula to the scraped output and filters accordingly.")
    parser.add_argument("--input-path", required=False, default="data/finviz", help="Path to the scrapper output.")
    parser.add_argument("--output-path", required=False, default="data/inference/in/screener", help="Path to the screener output.")
    args = parser.parse_args()

    scrapper_df = load_latest_screener(args.input_path)
    
    screener_df = scrapper_df[(scrapper_df['Volume']/720)/((scrapper_df['Shares Float']*1000000)/720) > 1]

    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"screener_data_{current_time}.csv"
    file_path = os.path.join(args.output_path, file_name)

    screener_df.to_csv(file_path)
    logger.success(f'Screener after formula filter saved in {file_path}')

if __name__ == "__main__":
    main()