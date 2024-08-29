import os
import pandas as pd
import numpy as np
import datetime
import argparse
from loguru import logger
from tensorflow.keras.models import load_model
import joblib
#from sklearn.preprocessing import StandardScaler
#import sklearn


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


def ml_inference(record, model, scaler):
    if model == 'mock_wrapper':
        return 1
    else:
        scaled_record = scaler.transform(record.reshape(1, -1))
        prediction = model.predict(scaled_record)
        prediction_binary = np.where(prediction > 0.4, 1, 0)
        return prediction_binary


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Applies machine learning to the news embeddings and outputs the sentiment result.")
    parser.add_argument("--input-path", required=False, default="data/inference/in/news", help="Path to the news embeddings.")
    parser.add_argument("--output-path", required=False, default="data/inference/out/result", help="Path to the model output.")
    parser.add_argument("--model", required=False, default="data/inference/in/input/feedforward.keras", help="Path to the model parameters file.")
    parser.add_argument("--scaler", required=False, default="data/inference/in/input/scaler.pkl", help="Path to the scaler parameters.")
    args = parser.parse_args()

    news_df = load_latest_screener(args.input_path)

    inference_model = load_model(args.model)
    logger.success(f'Neural Network model successfully loaded.')

    scaler = joblib.load(args.scaler)
    logger.success(f'Scaler successfully loaded.')

    logger.info('Running news sentiment analysis...')
    news_df['news_sentiment_1_2_3_4_7_10_30'] = news_df['last_summary_embedding'].apply(lambda x: ml_inference(np.fromstring(x.strip('[]'), sep=','), inference_model, scaler))
    logger.success('News sentiment analysis completed.')

    news_df['News Sentiment 1 Day'] = news_df['news_sentiment_1_2_3_4_7_10_30'].apply(lambda x: x[0][0])
    news_df['News Sentiment 2 Day'] = news_df['news_sentiment_1_2_3_4_7_10_30'].apply(lambda x: x[0][1])
    news_df['News Sentiment 3 Day'] = news_df['news_sentiment_1_2_3_4_7_10_30'].apply(lambda x: x[0][2])
    news_df['News Sentiment 4 Day'] = news_df['news_sentiment_1_2_3_4_7_10_30'].apply(lambda x: x[0][3])
    news_df['News Sentiment 7 Day'] = news_df['news_sentiment_1_2_3_4_7_10_30'].apply(lambda x: x[0][4])
    news_df['News Sentiment 10 Day'] = news_df['news_sentiment_1_2_3_4_7_10_30'].apply(lambda x: x[0][5])
    news_df['News Sentiment 30 Day'] = news_df['news_sentiment_1_2_3_4_7_10_30'].apply(lambda x: x[0][6])

    result_columns = ['News Sentiment 1 Day','News Sentiment 2 Day','News Sentiment 3 Day',
       'News Sentiment 4 Day', 'News Sentiment 7 Day',
       'News Sentiment 10 Day', 'News Sentiment 30 Day',
        'last_news_summary', 'Ticker', 'Company', 'Country', 'Market Cap', 'Shares Float',
       'Insider Ownership', 'Insider Transactions', 'Institutional Ownership',
       'Institutional Transactions', 'Short Interest',
       'Performance (Half Year)', 'Volatility (Week)', 'Volatility (Month)',
       'Earnings Date', 'Change from Open', 'Gap', 'Average Volume',
       'Relative Volume', 'Volume', 'Price', 'Change']

    result_df = news_df[result_columns]
    
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"result_data_{current_time}.csv"
    file_path = os.path.join(args.output_path, file_name)

    result_df.to_csv(file_path)
    logger.success(f'News sentiment analysis saved in {file_path}')


if __name__ == "__main__":
    main()